#!/usr/bin/env python3
"""Extract text from meeting material folders into agent-friendly Markdown."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


DEPENDENCY_HELP = """
Missing optional document parser dependencies.

Install them in the active Python environment:
  python -m pip install python-docx python-pptx pdfplumber pypdf

On Windows, if Chinese output is garbled, run:
  $env:PYTHONIOENCODING="utf-8"
"""


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def slug(value: str) -> str:
    value = re.sub(r'["“”‘’`´]+', "_", value)
    value = value.replace("：", "_").replace("、", "_")
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", value)
    cleaned = re.sub(r"_+", "_", cleaned).strip(" ._")
    return cleaned[:90] or "material"


def read_text_file(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "gbk"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def extract_docx(path: Path) -> str:
    try:
        from docx import Document
    except ImportError as exc:
        raise RuntimeError("python-docx is required for .docx files") from exc

    doc = Document(str(path))
    parts: list[str] = []
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text:
            parts.append(text)
    for table in doc.tables:
        for row in table.rows:
            cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
            if any(cells):
                parts.append(" | ".join(cells))
    return "\n\n".join(parts)


def extract_pptx(path: Path) -> str:
    try:
        from pptx import Presentation
    except ImportError as exc:
        raise RuntimeError("python-pptx is required for .pptx files") from exc

    prs = Presentation(str(path))
    slides: list[str] = []
    for index, slide in enumerate(prs.slides, start=1):
        texts: list[str] = []
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text:
                text = shape.text.strip()
                if text:
                    texts.append(text)
            if getattr(shape, "has_table", False):
                for row in shape.table.rows:
                    cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                    if any(cells):
                        texts.append(" | ".join(cells))
        if texts:
            slides.append(f"## Slide {index}\n\n" + "\n\n".join(texts))
    return "\n\n".join(slides)


def parse_pdf_pages(value: str) -> int | None:
    normalized = str(value).strip().lower()
    if normalized in {"all", "full", "*"}:
        return None
    try:
        pages = int(normalized)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--pdf-pages must be a positive integer or 'all'") from exc
    if pages <= 0:
        raise argparse.ArgumentTypeError("--pdf-pages must be a positive integer or 'all'")
    return pages


def requested_pages_label(value: int | None) -> str:
    return "all" if value is None else str(value)


def extract_pdf(path: Path, max_pages: int | None) -> tuple[str, dict[str, Any]]:
    try:
        import pdfplumber
    except ImportError:
        pdfplumber = None

    if pdfplumber is not None:
        pages: list[str] = []
        total_pages = 0
        with pdfplumber.open(str(path)) as pdf:
            total_pages = len(pdf.pages)
            selected_pages = pdf.pages if max_pages is None else pdf.pages[:max_pages]
            for index, page in enumerate(selected_pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    pages.append(f"## Page {index}\n\n{text.strip()}")
        metadata = {
            "pdf_pages_total": total_pages,
            "pdf_pages_extracted": total_pages if max_pages is None else min(max_pages, total_pages),
            "pdf_pages_requested": requested_pages_label(max_pages),
            "pdf_text_pages": len(pages),
        }
        if pages:
            return "\n\n".join(pages), metadata

    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("pdfplumber or pypdf is required for .pdf files") from exc

    reader = PdfReader(str(path))
    pages = []
    total_pages = len(reader.pages)
    selected_pages = reader.pages if max_pages is None else reader.pages[:max_pages]
    for index, page in enumerate(selected_pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"## Page {index}\n\n{text.strip()}")
    return "\n\n".join(pages), {
        "pdf_pages_total": total_pages,
        "pdf_pages_extracted": total_pages if max_pages is None else min(max_pages, total_pages),
        "pdf_pages_requested": requested_pages_label(max_pages),
        "pdf_text_pages": len(pages),
    }


def extract_one(path: Path, pdf_pages: int | None) -> tuple[str, str, dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        return "docx", extract_docx(path), {}
    if suffix == ".pptx":
        return "pptx", extract_pptx(path), {}
    if suffix == ".pdf":
        text, metadata = extract_pdf(path, pdf_pages)
        return "pdf", text, metadata
    if suffix in {".txt", ".md"}:
        return suffix.lstrip("."), read_text_file(path), {}
    raise ValueError(f"unsupported file type: {suffix}")


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--out", type=Path, default=Path("extracted_materials"))
    parser.add_argument("--pdf-pages", type=parse_pdf_pages, default=None)
    parser.add_argument("--no-recursive", action="store_true",
                        help="Only scan top-level files, do not recurse into subdirectories")
    args = parser.parse_args()

    input_dir = args.input_dir.resolve()
    out_dir = args.out.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    supported = {".docx", ".pptx", ".pdf", ".txt", ".md"}
    if args.no_recursive:
        files = [p for p in sorted(input_dir.iterdir()) if p.is_file() and p.suffix.lower() in supported]
    else:
        files = [p for p in sorted(input_dir.rglob("*")) if p.is_file() and p.suffix.lower() in supported]
    manifest: dict[str, Any] = {"input_dir": str(input_dir), "files": []}
    had_error = False

    for path in files:
        rel = path.relative_to(input_dir)
        if len(rel.parts) > 1:
            prefix = slug("_".join(rel.parts[:-1]))
            output_name = f"{prefix}_{slug(path.stem)}.md"
        else:
            output_name = f"{slug(path.stem)}.md"
        output_path = out_dir / output_name
        record: dict[str, Any] = {
            "source": str(path),
            "type": path.suffix.lower().lstrip("."),
            "output": str(output_path),
            "status": "ok",
        }
        try:
            detected_type, text, metadata = extract_one(path, args.pdf_pages)
            record["type"] = detected_type
            record.update(metadata)
            if detected_type == "pdf" and metadata.get("pdf_text_pages") == 0:
                record["warning"] = "No extractable text found in selected PDF pages; the PDF may be scanned or image-based."
            output_path.write_text(
                f"# {path.name}\n\nSource: `{path}`\n\n{text.strip()}\n",
                encoding="utf-8",
            )
            record["chars"] = len(text)
        except Exception as exc:  # noqa: BLE001 - report per-file extraction failures.
            had_error = True
            record["status"] = "error"
            record["error"] = str(exc)
        manifest["files"].append(record)

    (out_dir / "materials_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    scope = "top-level" if args.no_recursive else "recursive"
    print(f"Scanned {len(files)} supported files from {input_dir} ({scope})")
    print(f"Wrote manifest: {out_dir / 'materials_manifest.json'}")
    if had_error:
        print(DEPENDENCY_HELP, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
