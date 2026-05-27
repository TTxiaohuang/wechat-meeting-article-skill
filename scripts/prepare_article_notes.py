#!/usr/bin/env python3
"""Prepare budgeted intermediate notes from extracted meeting materials."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


PAPER_SECTION_PATTERNS: dict[str, tuple[str, ...]] = {
    "摘要": ("摘要", "abstract"),
    "引言": ("引言", "研究背景", "introduction"),
    "研究设计": ("研究设计", "数据", "方法", "模型", "识别策略", "method", "data"),
    "研究结果": ("研究结果", "实证结果", "结果", "发现", "results", "findings"),
    "机制与稳健性": ("机制", "渠道", "稳健", "异质", "robust", "mechanism"),
    "结论": ("结论", "讨论", "启示", "conclusion", "discussion"),
}
TRANSCRIPT_HINTS = ("录音", "转录", "transcript", "原文")
PAPER_HINTS = ("pdf", "doi", "摘要", "abstract")


def configure_stdio() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def compact(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: max(limit - 1, 0)].rstrip() + "…"


def load_manifest(input_dir: Path) -> dict[str, Any]:
    manifest_path = input_dir / "materials_manifest.json"
    if manifest_path.exists():
        return json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    files = []
    for path in sorted(input_dir.glob("*.md")):
        files.append({"source": path.name, "type": "md", "output": str(path), "chars": len(read_text(path))})
    return {"files": files}


def first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return fallback


def looks_like_paper(record: dict[str, Any], text: str) -> bool:
    haystack = f"{record.get('source', '')}\n{text[:3000]}".lower()
    return record.get("type") == "pdf" or any(hint in haystack for hint in PAPER_HINTS)


def looks_like_transcript(record: dict[str, Any], text: str) -> bool:
    haystack = f"{record.get('source', '')}\n{text[:1000]}".lower()
    return any(hint in haystack for hint in TRANSCRIPT_HINTS)


def find_section_excerpt(text: str, keywords: tuple[str, ...], limit: int) -> str:
    lowered = text.lower()
    for keyword in keywords:
        index = lowered.find(keyword.lower())
        if index >= 0:
            start = max(index - 80, 0)
            return compact(text[start : start + limit * 3], limit)
    return ""


def paper_note(record: dict[str, Any], text: str, limit: int) -> dict[str, Any]:
    sections = {}
    for label, keywords in PAPER_SECTION_PATTERNS.items():
        excerpt = find_section_excerpt(text, keywords, limit)
        if excerpt:
            sections[label] = excerpt
    return {
        "source": record.get("source", ""),
        "title": re.sub(r"\.(pdf|md|docx|pptx|txt)$", "", first_heading(text, Path(str(record.get("source", ""))).stem), flags=re.I),
        "chars": record.get("chars", len(text)),
        "pdf_pages_total": record.get("pdf_pages_total"),
        "pdf_pages_extracted": record.get("pdf_pages_extracted"),
        "pdf_pages_requested": record.get("pdf_pages_requested"),
        "pdf_text_pages": record.get("pdf_text_pages"),
        "sections": sections,
        "reading_instruction": (
            "Use these excerpts as an index only. Re-open the extracted Markdown around relevant headings "
            "before making precise claims."
        ),
    }


def transcript_note(record: dict[str, Any], text: str, limit: int) -> dict[str, Any]:
    cues = []
    for keyword in ("老师", "同学", "讨论", "问题", "建议", "安排", "不准", "识别"):
        excerpt = find_section_excerpt(text, (keyword,), limit)
        if excerpt:
            cues.append({"cue": keyword, "excerpt": excerpt})
    return {
        "source": record.get("source", ""),
        "chars": record.get("chars", len(text)),
        "noisy_transcript": True,
        "use_policy": "Paraphrase stable meaning; cross-check public facts against PPT/PDF/filenames.",
        "cues": cues[:8],
    }


def intake_template(input_dir: Path) -> dict[str, Any]:
    return {
        "intake_gate": {
            "material_folder": {"value": str(input_dir), "status": "user_provided"},
            "date": {"value": "", "status": "user_provided|inferred"},
            "editor": {"value": "", "status": "user_provided|omitted_confirmed"},
            "visual_style": {"value": "classic", "status": "user_provided|default_confirmed"},
            "images": {"value": "", "status": "provided|suggestions_only|none_confirmed"},
        }
    }


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--out", type=Path, default=Path("article_notes"))
    parser.add_argument("--max-section-chars", type=int, default=900)
    args = parser.parse_args()

    manifest = load_manifest(args.input_dir)
    args.out.mkdir(parents=True, exist_ok=True)
    paper_notes = []
    transcript_notes = []
    for record in manifest.get("files", []):
        output = record.get("output")
        path = Path(output) if output else args.input_dir / f"{Path(str(record.get('source', 'material'))).stem}.md"
        if not path.exists():
            continue
        text = read_text(path)
        if looks_like_paper(record, text):
            paper_notes.append(paper_note(record, text, args.max_section_chars))
        elif looks_like_transcript(record, text):
            transcript_notes.append(transcript_note(record, text, args.max_section_chars))

    (args.out / "paper_notes.json").write_text(
        json.dumps({"papers": paper_notes}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.out / "transcript_notes.json").write_text(
        json.dumps({"transcripts": transcript_notes}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.out / "intake_decision.template.json").write_text(
        json.dumps(intake_template(args.input_dir), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote notes to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
