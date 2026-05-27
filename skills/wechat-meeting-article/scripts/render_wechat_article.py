#!/usr/bin/env python3
"""Render a structured meeting article JSON file to WeChat-friendly HTML."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any


ACCENT = "#256f8f"
TEXT = "#243042"
MUTED = "#6b7280"
SOFT = "#eef7fa"
BORDER = "#d9e8ee"


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def para(text: str) -> str:
    if not text:
        return ""
    return f'<p style="margin:8px 0 0;color:{TEXT};line-height:1.75;">{esc(text)}</p>'


def h2(title: str) -> str:
    return (
        '<section style="margin:28px 0 12px;">'
        f'<p style="margin:0;color:{ACCENT};font-size:18px;font-weight:700;line-height:1.5;">{esc(title)}</p>'
        f'<p style="margin:6px 0 0;width:42px;border-top:3px solid {ACCENT};"></p>'
        "</section>"
    )


def tag(text: str) -> str:
    if not text:
        return ""
    return (
        f'<span style="display:inline-block;margin:0 6px 6px 0;padding:2px 8px;'
        f'border:1px solid {BORDER};border-radius:999px;color:{ACCENT};font-size:13px;line-height:1.6;">{esc(text)}</span>'
    )


def quote_block(text: str, speaker: str = "", source: str = "") -> str:
    label = " ".join(part for part in [speaker, source and f"source: {source}"] if part)
    label_html = (
        f'<p style="margin:0 0 4px;color:{MUTED};font-size:13px;line-height:1.5;">{esc(label)}</p>'
        if label
        else ""
    )
    return (
        f'<blockquote style="margin:10px 0 0;padding:10px 12px;border-left:3px solid {ACCENT};'
        f'background:{SOFT};color:{TEXT};line-height:1.75;">'
        f"{label_html}{para(text)}"
        "</blockquote>"
    )


def render_english(data: dict[str, Any]) -> str:
    speeches = data.get("speeches") or []
    parts = [h2(data.get("title") or "英语交流")]
    parts.append(tag(data.get("topic") or ""))
    parts.append(para(data.get("intro") or ""))
    cards = []
    for item in speeches:
        speaker = item.get("speaker") or "Speaker"
        role = item.get("role") or ""
        source = item.get("source") or ""
        cards.append(
            f'<section style="box-sizing:border-box;display:inline-block;vertical-align:top;width:82%;'
            f'max-width:320px;min-height:180px;margin:8px 10px 8px 0;padding:16px;white-space:normal;'
            f'border:1px solid {BORDER};border-radius:8px;background:#ffffff;">'
            f'<p style="margin:0;color:{ACCENT};font-size:17px;font-weight:700;line-height:1.4;">{esc(speaker)}</p>'
            f'<p style="margin:2px 0 10px;color:{MUTED};font-size:13px;line-height:1.5;">{esc(role)}</p>'
            f'<p style="margin:0;color:{TEXT};font-size:15px;line-height:1.75;">{esc(item.get("text") or "")}</p>'
            f'<p style="margin:10px 0 0;color:{MUTED};font-size:12px;line-height:1.4;">{esc(source)}</p>'
            "</section>"
        )
    if cards:
        parts.append(
            '<section style="box-sizing:border-box;overflow-x:auto;white-space:nowrap;'
            '-webkit-overflow-scrolling:touch;margin:12px 0 4px;padding-bottom:4px;">'
            + "".join(cards)
            + "</section>"
        )
    return "".join(parts)


def render_literature(data: dict[str, Any]) -> str:
    parts = [h2(data.get("title") or "文献分享")]
    for paper in data.get("papers") or []:
        parts.append(
            f'<section style="margin:14px 0 18px;padding:14px 0;border-top:1px solid {BORDER};">'
            f'<p style="margin:0;color:{TEXT};font-size:17px;font-weight:700;line-height:1.5;">{esc(paper.get("title") or "Untitled paper")}</p>'
            f'<p style="margin:4px 0 0;color:{MUTED};font-size:13px;line-height:1.5;">'
            f'{esc(paper.get("authors") or "")} {esc(paper.get("venue") or "")}</p>'
            f'{tag(paper.get("presenter") and "分享人：" + paper.get("presenter"))}'
            f'{tag(paper.get("doi") and "DOI: " + paper.get("doi"))}'
            f'{para(paper.get("summary") or "")}'
        )
        for comment in paper.get("comments") or []:
            parts.append(quote_block(comment.get("text") or "", comment.get("speaker") or "", comment.get("source") or ""))
        parts.append("</section>")
    return "".join(parts)


def render_policy(data: dict[str, Any]) -> str:
    parts = [h2(data.get("title") or "时政交流")]
    parts.append(tag(data.get("topic") or ""))
    parts.append(para(data.get("summary") or ""))
    for viewpoint in data.get("viewpoints") or []:
        parts.append(quote_block(viewpoint.get("text") or "", viewpoint.get("speaker") or "", viewpoint.get("source") or ""))
    return "".join(parts)


def render_free_discussion(data: dict[str, Any]) -> str:
    parts = [h2(data.get("title") or "自由讨论与会议总结")]
    for item in data.get("items") or []:
        parts.append(quote_block(item.get("text") or "", item.get("speaker") or "", item.get("source") or ""))
    parts.append(para(data.get("closing") or ""))
    return "".join(parts)


def render_article(article: dict[str, Any]) -> str:
    meta = article.get("meta") or {}
    sections = article.get("sections") or {}
    parts = [
        f'<h1 style="margin:0 0 12px;color:{TEXT};font-size:22px;line-height:1.35;font-weight:800;">{esc(meta.get("title") or "组会纪要")}</h1>',
        f'<p style="margin:0 0 12px;color:{MUTED};font-size:13px;line-height:1.6;">{esc(meta.get("date") or "")} {esc(meta.get("group") or "")} {esc(meta.get("host") and "主持：" + meta.get("host"))}</p>',
        para(meta.get("summary") or ""),
    ]
    if sections.get("english_exchange"):
        parts.append(render_english(sections["english_exchange"]))
    if sections.get("literature_sharing"):
        parts.append(render_literature(sections["literature_sharing"]))
    if sections.get("policy_discussion"):
        parts.append(render_policy(sections["policy_discussion"]))
    if sections.get("free_discussion"):
        parts.append(render_free_discussion(sections["free_discussion"]))
    return "".join(parts)


def main() -> None:
    configure_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument("article_json", type=Path)
    parser.add_argument("--out", type=Path, default=Path("dist"))
    args = parser.parse_args()

    try:
        article = json.loads(args.article_json.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        lines = args.article_json.read_text(encoding="utf-8-sig").splitlines()
        bad_line = lines[exc.lineno - 1] if 0 <= exc.lineno - 1 < len(lines) else ""
        print(
            f"Invalid JSON in {args.article_json} at line {exc.lineno}, column {exc.colno}: {exc.msg}",
            file=sys.stderr,
        )
        if bad_line:
            print(bad_line, file=sys.stderr)
            print(" " * (max(exc.colno - 1, 0)) + "^", file=sys.stderr)
        print(
            "Tip: create article.json with scripts/create_article_json.py or Python json.dump. "
            "Do not handwrite unescaped quotes inside JSON strings.",
            file=sys.stderr,
        )
        raise SystemExit(2) from exc
    skill_dir = Path(__file__).resolve().parents[1]
    template = (skill_dir / "assets" / "article-template.html").read_text(encoding="utf-8")
    body = template.replace("{{content}}", render_article(article))

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "article.wechat.html").write_text(body, encoding="utf-8")
    preview = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<title>WeChat Article Preview</title></head>"
        "<body style='margin:0;background:#f3f4f6;'>"
        "<main style='box-sizing:border-box;max-width:430px;margin:0 auto;min-height:100vh;padding:18px;background:#fff;'>"
        f"{body}</main></body></html>"
    )
    (args.out / "article.preview.html").write_text(preview, encoding="utf-8")
    print(f"Wrote {args.out / 'article.wechat.html'}")
    print(f"Wrote {args.out / 'article.preview.html'}")


if __name__ == "__main__":
    main()
