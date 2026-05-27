#!/usr/bin/env python3
"""Write article.json from a Python file that defines ARTICLE or article."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


def configure_stdio() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def load_article(path: Path) -> dict[str, Any]:
    spec = importlib.util.spec_from_file_location("article_data", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    article = getattr(module, "ARTICLE", None)
    if article is None:
        article = getattr(module, "article", None)
    if not isinstance(article, dict):
        raise RuntimeError("Input file must define ARTICLE or article as a dict")
    return article


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument("input_py", type=Path)
    parser.add_argument("--out", type=Path, default=Path("article.json"))
    args = parser.parse_args()

    article = load_article(args.input_py)
    args.out.write_text(json.dumps(article, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
