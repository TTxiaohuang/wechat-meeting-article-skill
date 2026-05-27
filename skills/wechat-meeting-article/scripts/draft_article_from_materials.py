#!/usr/bin/env python3
"""Create a rough article.json draft from extracted Markdown materials."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SPEAKER_RE = re.compile(r"^(?P<name>[A-Za-z][A-Za-z ._-]{1,30}|[\u4e00-\u9fff]{2,8})(?:[:：])?$")
DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b")


def configure_stdio() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return fallback


def compact(text: str, limit: int = 260) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def looks_like_english(text: str) -> bool:
    letters = sum(ch.isalpha() and ord(ch) < 128 for ch in text)
    return letters >= 20 and letters > len(text) * 0.45


def split_english_speeches(text: str, source: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in text.splitlines()]
    speeches: list[dict[str, str]] = []
    current_name = ""
    current_role = ""
    current_text: list[str] = []

    def flush() -> None:
        nonlocal current_name, current_role, current_text
        body = "\n\n".join(part for part in current_text if part).strip()
        if current_name and looks_like_english(body):
            speeches.append(
                {
                    "speaker": current_name,
                    "role": current_role or "学生",
                    "mode": "full_text",
                    "text": body,
                    "source": source,
                }
            )
        current_name = ""
        current_role = ""
        current_text = []

    index = 0
    while index < len(lines):
        line = lines[index]
        match = SPEAKER_RE.match(line)
        if match and index + 1 < len(lines):
            next_line = lines[index + 1].strip()
            if next_line in {"学生", "老师", "教师", "主持人"} or looks_like_english(next_line):
                flush()
                current_name = match.group("name").strip()
                if next_line in {"学生", "老师", "教师", "主持人"}:
                    current_role = next_line
                    index += 2
                    continue
        if line and not line.startswith("#") and current_name:
            current_text.append(line)
        index += 1
    flush()
    return speeches


def extract_abstract(text: str) -> str:
    match = re.search(r"(摘要[:：]\s*)(?P<body>.+?)(?:关键词|Abstract|引言|一、|\n#|\Z)", text, re.S)
    if match:
        return compact(match.group("body"), 360)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.strip()) > 40]
    return compact(paragraphs[0], 300) if paragraphs else ""


def paper_from_markdown(path: Path, text: str) -> dict[str, Any]:
    heading = first_heading(text, path.stem)
    title = re.sub(r"\.(pdf|md|docx|pptx|txt)$", "", heading.strip(), flags=re.I)
    doi_match = DOI_RE.search(text)
    abstract = extract_abstract(text)
    return {
        "title": title,
        "authors": "",
        "venue": "",
        "doi": doi_match.group(0) if doi_match else "",
        "presenter": "",
        "images": [],
        "background": abstract,
        "research_question": "",
        "methods_data": "",
        "findings": [],
        "discussion_value": "",
        "summary": abstract,
        "comments": [],
    }


def classify_files(input_dir: Path) -> tuple[list[Path], list[Path], list[Path]]:
    markdowns = sorted(input_dir.glob("*.md"))
    english = [p for p in markdowns if any(key in p.name.lower() for key in ("英语", "english", "speech"))]
    papers = [p for p in markdowns if "pdf" in read_text(p)[:200].lower() or "doi" in read_text(p).lower()[:2000]]
    transcripts = [p for p in markdowns if p not in english and p not in papers]
    return english, papers, transcripts


def build_article(input_dir: Path) -> dict[str, Any]:
    english_files, paper_files, transcript_files = classify_files(input_dir)
    speeches: list[dict[str, str]] = []
    for path in english_files:
        speeches.extend(split_english_speeches(read_text(path), path.name))

    papers = [paper_from_markdown(path, read_text(path)) for path in paper_files]
    free_items = []
    for path in transcript_files[:2]:
        text = read_text(path)
        free_items.append(
            {
                "speaker": "会议讨论",
                "text": compact(text, 420),
                "source": path.name,
            }
        )

    sections: dict[str, Any] = {}
    if speeches:
        sections["english_exchange"] = {
            "title": "英语交流",
            "topic": "",
            "intro": "本次英语交流环节，同学们围绕主题进行英文分享。",
            "images": [],
            "speeches": speeches,
        }
    if papers:
        sections["literature_sharing"] = {
            "title": "文献分享",
            "intro": "本次文献分享围绕以下研究展开。",
            "images": [],
            "papers": papers,
        }
    if free_items:
        sections["free_discussion"] = {
            "title": "自由讨论与会议总结",
            "images": [],
            "items": free_items,
            "closing": "",
        }

    return {
        "meta": {
            "title": "组会纪要",
            "date": "",
            "group": "",
            "host": "",
            "cover_image": "",
            "cover_caption": "",
            "summary": "本次组会围绕英语交流、文献分享和自由讨论展开。",
        },
        "sections": sections,
        "assets": {"images": []},
    }


def main() -> None:
    configure_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--out", type=Path, default=Path("article.draft.json"))
    args = parser.parse_args()

    article = build_article(args.input_dir)
    args.out.write_text(json.dumps(article, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote draft article JSON: {args.out}")


if __name__ == "__main__":
    main()
