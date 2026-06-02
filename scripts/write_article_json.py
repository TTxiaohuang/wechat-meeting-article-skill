#!/usr/bin/env python3
"""Write article.json from a Python file that defines ARTICLE or article."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def configure_stdio() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def read_source(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "gbk"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def load_article(path: Path) -> dict[str, Any]:
    namespace: dict[str, Any] = {}
    source = read_source(path)
    if "\ufffd" in source:
        raise RuntimeError(
            f"{path} contains replacement characters, which usually means Chinese text was garbled while writing the file.\n"
            "Do not keep retrying with large Bash heredocs or inline Python. Write article.json directly, "
            "validate it with render_wechat_article.py, then run update_article_gate.py."
        )
    try:
        code = compile(source, str(path), "exec")
        exec(code, namespace)  # noqa: S102 - trusted local article data file.
    except Exception as exc:  # noqa: BLE001 - report authoring failures clearly.
        raise RuntimeError(
            f"Could not execute {path}: {exc}\n"
            "If this is Claude Code on Windows and Chinese text is garbled, write article.json directly, "
            "validate it with render_wechat_article.py, then run update_article_gate.py."
        ) from exc
    article = namespace.get("ARTICLE")
    if article is None:
        article = namespace.get("article")
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
