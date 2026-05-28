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
LOCAL_PATH_RE = re.compile(r"(?:[A-Za-z]:\\|/mnt/[a-z]/|/Users/|/home/)")
SUPPORTED_TEMPLATES = {
    "classic",
    "notebook",
    "journal",
    "campus",
    "minimal",
    "magazine",
    "warm-note",
    "briefing",
    "fieldnote",
}
SUPPORTED_PALETTES = {"classic", "forest", "blueprint", "warm", "ink", "sunrise", "mono", "sakura", "ocean"}
SUPPORTED_INSERT_TYPES = {"honor_news", "honor-news", "announcement", "milestone", "note"}
SUPPORTED_PLACEMENTS = {
    "after_lead",
    "before_english_exchange",
    "after_english_exchange",
    "before_literature_sharing",
    "after_literature_sharing",
    "before_policy_discussion",
    "after_policy_discussion",
    "before_free_discussion",
    "after_free_discussion",
    "before_closing",
}
REQUIRED_INTAKE_FIELDS = ("material_folder", "date", "editor", "visual_style")
EDITOR_OMISSION_STATUSES = {"omitted_confirmed", "not_needed_confirmed"}


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


def visible_text_length(article: dict[str, Any]) -> int:
    total = 0

    def walk(value: Any, key: str = "") -> None:
        nonlocal total
        if key in {"source", "cover_image", "url", "src", "path", "doi"}:
            return
        if isinstance(value, str):
            total += len(value.strip())
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, dict):
            for child_key, child_value in value.items():
                if child_key == "_meta":
                    continue
                walk(child_value, child_key)

    walk(article)
    return total


def check_scaffold_and_length(article: dict[str, Any], min_chars: int) -> list[str]:
    issues: list[str] = []
    if article.get("_meta", {}).get("scaffold_generated"):
        issues.append("scaffold-generated article must be expanded before delivery")
    length = visible_text_length(article)
    if length < min_chars:
        issues.append(f"article appears too short: {length} visible chars, expected at least {min_chars}")
    return issues


def normalize_choice(value: Any) -> str:
    return str(value or "").strip().lower().replace("_", "-")


def intake_field_status(gate: dict[str, Any], field: str) -> str:
    value = gate.get(field)
    if isinstance(value, dict):
        return str(value.get("status") or "").strip().lower()
    if isinstance(value, str):
        return "recorded" if value.strip() else ""
    return ""


def check_intake_gate(article: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    gate = article.get("_meta", {}).get("intake_gate")
    if not isinstance(gate, dict):
        return ["intake gate missing; record required confirmations or inferences before delivery"]
    for field in REQUIRED_INTAKE_FIELDS:
        if not intake_field_status(gate, field):
            issues.append(f"intake gate missing {field} decision")
    return issues


def check_meta_and_style(article: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    meta = article.get("meta", {})
    for field in ("title", "date", "host"):
        if not str(meta.get(field) or "").strip():
            issues.append(f"meta.{field} is missing")
    gate = article.get("_meta", {}).get("intake_gate") or {}
    editor_status = intake_field_status(gate, "editor") if isinstance(gate, dict) else ""
    if not str(meta.get("editor") or meta.get("article_editor") or "").strip():
        if editor_status not in EDITOR_OMISSION_STATUSES:
            issues.append("editor decision missing; set meta.editor or record omitted_confirmed in _meta.intake_gate.editor")

    template = normalize_choice(article.get("template") or meta.get("template") or "classic")
    palette = normalize_choice(article.get("palette") or meta.get("palette") or "classic")
    if template not in SUPPORTED_TEMPLATES:
        issues.append(f"unsupported template: {template}")
    if palette not in SUPPORTED_PALETTES:
        issues.append(f"unsupported palette: {palette}")
    return issues


def check_english(article: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    speeches = article.get("sections", {}).get("english_exchange", {}).get("speeches", [])
    seen: dict[str, int] = {}
    for index, speech in enumerate(speeches, start=1):
        text = speech.get("text") or ""
        if len(text.strip()) < 80:
            issues.append(f"english speech {index} may be too short for full-text mode")
        fingerprint = re.sub(r"\s+", " ", text.strip().lower())
        if fingerprint:
            if fingerprint in seen:
                issues.append(f"english speech {index} duplicates speech {seen[fingerprint]}")
            else:
                seen[fingerprint] = index
    return issues


def check_custom_sections(article: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    inserts = article.get("custom_sections") or article.get("inserts") or []
    if not inserts:
        return issues
    if not isinstance(inserts, list):
        return ["custom_sections must be an array"]
    for index, item in enumerate(inserts, start=1):
        if not isinstance(item, dict):
            issues.append(f"custom section {index} must be an object")
            continue
        kind = str(item.get("type") or item.get("kind") or "note").strip().lower().replace("_", "-")
        placement = str(item.get("placement") or "after_lead").strip()
        if kind not in SUPPORTED_INSERT_TYPES:
            issues.append(f"custom section {index} has unsupported type: {kind}")
        if placement not in SUPPORTED_PLACEMENTS:
            issues.append(f"custom section {index} has unsupported placement: {placement}")
        body = str(item.get("text") or item.get("summary") or "").strip()
        if kind in {"honor_news", "honor-news"}:
            if not (body or item.get("person") or item.get("award")):
                issues.append(f"custom honor section {index} lacks text/person/award details")
        elif not body:
            issues.append(f"custom section {index} lacks text")
    return issues


def check_html(html_path: Path | None) -> list[str]:
    if not html_path:
        return []
    html = html_path.read_text(encoding="utf-8-sig")
    leaked = sorted(set(SOURCE_EXT_RE.findall(html)))
    issues = []
    if leaked:
        issues.append(f"visible source filename leaked in HTML: {', '.join(leaked)}")
    if LOCAL_PATH_RE.search(html):
        issues.append("visible local filesystem path leaked in HTML")
    return issues


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument("article_json", type=Path)
    parser.add_argument("--html", type=Path)
    parser.add_argument("--min-chars", type=int, default=1200)
    args = parser.parse_args()

    article = load_json(args.article_json)
    issues = []
    issues.extend(check_scaffold_and_length(article, args.min_chars))
    issues.extend(check_intake_gate(article))
    issues.extend(check_meta_and_style(article))
    issues.extend(check_literature(article))
    issues.extend(check_english(article))
    issues.extend(check_custom_sections(article))
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
