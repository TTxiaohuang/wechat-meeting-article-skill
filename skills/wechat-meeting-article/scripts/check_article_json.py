#!/usr/bin/env python3
"""Run quality checks for a generated WeChat meeting article JSON file."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SOURCE_EXT_RE = re.compile(r"[\w\u4e00-\u9fff（）()《》“”\"'-]+\.(?:docx|pdf|pptx|md|txt)", re.I)


def configure_stdio() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def check_literature(article: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    papers = article.get("sections", {}).get("literature_sharing", {}).get("papers", [])
    required = ["background", "research_question", "methods_data", "discussion_value"]
    for index, paper in enumerate(papers, start=1):
        missing = [field for field in required if not paper.get(field)]
        if not paper.get("findings"):
            missing.append("findings")
        if missing:
            issues.append(f"paper {index} missing literature fields: {', '.join(missing)}")
    return issues


def check_english(article: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    speeches = article.get("sections", {}).get("english_exchange", {}).get("speeches", [])
    for index, speech in enumerate(speeches, start=1):
        text = speech.get("text") or ""
        if len(text.strip()) < 80:
            issues.append(f"english speech {index} may be too short for full-text mode")
    return issues


def check_html(html_path: Path | None) -> list[str]:
    if not html_path:
        return []
    html = html_path.read_text(encoding="utf-8-sig")
    leaked = sorted(set(SOURCE_EXT_RE.findall(html)))
    if leaked:
        return [f"visible source filename leaked in HTML: {', '.join(leaked)}"]
    return []


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument("article_json", type=Path)
    parser.add_argument("--html", type=Path)
    args = parser.parse_args()

    article = load_json(args.article_json)
    issues = []
    issues.extend(check_literature(article))
    issues.extend(check_english(article))
    issues.extend(check_html(args.html))

    if not issues:
        print("No article quality issues found.")
        return 0
    print("Article quality issues:")
    for issue in issues:
        print(f"- {issue}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
