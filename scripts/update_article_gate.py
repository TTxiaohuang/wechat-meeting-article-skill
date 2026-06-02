#!/usr/bin/env python3
"""Patch intake-gate and style metadata into an existing article.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def configure_stdio() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"Invalid JSON in {path} at line {exc.lineno}, column {exc.colno}: {exc.msg}\n"
            "Fix JSON syntax first, then rerun update_article_gate.py."
        ) from exc


def set_decision(gate: dict[str, Any], key: str, value: str, status: str) -> None:
    if value or status:
        gate[key] = {"value": value, "status": status}


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument("article_json", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--material-folder", default="")
    parser.add_argument("--date", default="")
    parser.add_argument("--date-status", default="inferred")
    parser.add_argument("--editor", default="")
    parser.add_argument("--editor-status", default="")
    parser.add_argument("--template", default="")
    parser.add_argument("--palette", default="")
    parser.add_argument("--style-status", default="default_confirmed")
    parser.add_argument("--images-status", default="")
    args = parser.parse_args()

    article = load_json(args.article_json)
    meta = article.setdefault("meta", {})
    meta_block = article.setdefault("_meta", {})
    gate = meta_block.setdefault("intake_gate", {})

    material_folder = args.material_folder
    date = args.date or str(meta.get("date") or "")
    template = args.template or str(article.get("template") or meta.get("template") or "classic")
    palette = args.palette or str(article.get("palette") or meta.get("palette") or "classic")
    editor = args.editor or str(meta.get("editor") or meta.get("article_editor") or "")
    editor_status = args.editor_status or ("user_provided" if editor else "omitted_confirmed")

    if date:
        meta["date"] = date
    if editor:
        meta["editor"] = editor
    article["template"] = template
    article["palette"] = palette

    set_decision(gate, "material_folder", material_folder, "user_provided" if material_folder else "")
    set_decision(gate, "date", date, args.date_status if date else "")
    set_decision(gate, "editor", editor, editor_status)
    set_decision(gate, "visual_style", template, args.style_status)
    if palette:
        set_decision(gate, "palette", palette, "selected")
    if args.images_status:
        set_decision(gate, "images", "", args.images_status)

    out = args.out or args.article_json
    out.write_text(json.dumps(article, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
