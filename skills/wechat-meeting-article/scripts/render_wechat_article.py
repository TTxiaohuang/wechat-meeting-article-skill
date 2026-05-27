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
ACCENT_2 = "#7a6f45"
TEXT = "#243042"
MUTED = "#6b7280"
SOFT = "#eef7fa"
WARM = "#faf7ef"
BORDER = "#d9e8ee"
LINE = "#e7edf0"


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def paragraphs(text: str, *, size: int = 15, margin_top: int = 8) -> str:
    if not text:
        return ""
    chunks = [part.strip() for part in str(text).replace("\r\n", "\n").split("\n\n") if part.strip()]
    if not chunks:
        chunks = [str(text).strip()]
    rendered = []
    for index, chunk in enumerate(chunks):
        rendered.append(
            f'<p style="margin:{margin_top if index == 0 else 7}px 0 0;'
            f'color:{TEXT};font-size:{size}px;line-height:1.78;text-align:justify;">'
            f'{esc(chunk).replace(chr(10), "<br>")}</p>'
        )
    return "".join(rendered)


def h2(title: str, index: int | None = None) -> str:
    number = f"{index:02d}" if index is not None else ""
    number_html = (
        f'<span style="display:inline-block;margin-right:8px;color:{ACCENT_2};font-size:13px;'
        f'font-weight:700;letter-spacing:0;">{number}</span>'
        if number
        else ""
    )
    return (
        '<section style="margin:30px 0 14px;padding:0 0 8px;border-bottom:1px solid #eef2f4;">'
        f'<p style="margin:0;color:{TEXT};font-size:19px;font-weight:800;line-height:1.45;">'
        f'{number_html}{esc(title)}</p>'
        f'<p style="margin:7px 0 0;width:44px;border-top:3px solid {ACCENT};"></p>'
        "</section>"
    )


def tag(text: str) -> str:
    if not text:
        return ""
    return (
        f'<span style="display:inline-block;margin:0 6px 6px 0;padding:2px 8px;'
        f'border:1px solid {BORDER};border-radius:999px;color:{ACCENT};'
        f'background:#ffffff;font-size:13px;line-height:1.6;">{esc(text)}</span>'
    )


def info_card(title: str, text: str) -> str:
    if not text:
        return ""
    return (
        f'<section style="margin:12px 0 0;padding:12px 14px;border:1px solid {BORDER};'
        f'border-radius:8px;background:{SOFT};">'
        f'<p style="margin:0 0 4px;color:{ACCENT};font-size:14px;font-weight:700;line-height:1.5;">{esc(title)}</p>'
        f'{paragraphs(text, size=14, margin_top=0)}'
        "</section>"
    )


def quote_block(text: str, speaker: str = "") -> str:
    label_html = (
        f'<p style="margin:0 0 4px;color:{ACCENT};font-size:14px;font-weight:700;line-height:1.5;">{esc(speaker)}</p>'
        if speaker
        else ""
    )
    return (
        f'<blockquote style="margin:10px 0 0;padding:11px 13px;border-left:3px solid {ACCENT};'
        f'background:{SOFT};color:{TEXT};line-height:1.75;">'
        f"{label_html}{paragraphs(text, size=14, margin_top=0)}"
        "</blockquote>"
    )


def render_image(image: dict[str, Any] | str) -> str:
    if isinstance(image, str):
        src = image
        caption = ""
        alt = ""
    else:
        src = image.get("url") or image.get("src") or image.get("path") or ""
        caption = image.get("caption") or ""
        alt = image.get("alt") or caption
    if not src:
        return ""
    return (
        '<section style="margin:14px 0;text-align:center;">'
        f'<img src="{esc(src)}" alt="{esc(alt)}" style="display:block;width:100%;max-width:100%;'
        'height:auto;border-radius:8px;border:0;" />'
        f'{f"<p style=\'margin:6px 0 0;color:{MUTED};font-size:12px;line-height:1.5;text-align:center;\'>{esc(caption)}</p>" if caption else ""}'
        "</section>"
    )


def render_section_images(images: list[Any]) -> str:
    return "".join(render_image(image) for image in images or [])


def render_english(data: dict[str, Any], index: int) -> str:
    speeches = data.get("speeches") or []
    parts = [h2(data.get("title") or "英语交流", index)]
    parts.append(tag(data.get("topic") or ""))
    parts.append(paragraphs(data.get("intro") or ""))
    parts.append(render_section_images(data.get("images") or []))
    if speeches:
        parts.append(
            f'<p style="margin:12px 0 0;color:{MUTED};font-size:13px;line-height:1.6;">'
            f'左右滑动查看完整英文发言</p>'
        )
    cards = []
    total = len(speeches)
    for card_index, item in enumerate(speeches, start=1):
        speaker = item.get("speaker") or "Speaker"
        role = item.get("role") or ""
        cards.append(
            f'<section style="box-sizing:border-box;display:inline-block;vertical-align:top;width:86%;'
            f'max-width:340px;min-height:220px;margin:8px 12px 8px 0;padding:16px 16px 14px;white-space:normal;'
            f'border:1px solid {BORDER};border-radius:8px;background:#ffffff;">'
            f'<p style="margin:0;color:{MUTED};font-size:12px;line-height:1.4;text-align:right;">{card_index}/{total}</p>'
            f'<p style="margin:0;color:{ACCENT};font-size:18px;font-weight:800;line-height:1.4;">{esc(speaker)}</p>'
            f'<p style="margin:2px 0 10px;color:{MUTED};font-size:13px;line-height:1.5;">{esc(role)}</p>'
            f'{paragraphs(item.get("text") or "", size=14, margin_top=0)}'
            "</section>"
        )
    if cards:
        parts.append(
            '<section style="box-sizing:border-box;overflow-x:auto;white-space:nowrap;'
            '-webkit-overflow-scrolling:touch;margin:10px 0 4px;padding-bottom:8px;">'
            + "".join(cards)
            + "</section>"
        )
    return "".join(parts)


def render_findings(findings: list[Any]) -> str:
    if not findings:
        return ""
    items = []
    for finding in findings:
        items.append(
            f'<li style="margin:6px 0;color:{TEXT};font-size:14px;line-height:1.7;">{esc(finding)}</li>'
        )
    return (
        f'<section style="margin:10px 0 0;padding:10px 12px;border-radius:8px;background:{WARM};">'
        f'<p style="margin:0;color:{ACCENT_2};font-size:14px;font-weight:700;line-height:1.5;">核心发现</p>'
        f'<ul style="margin:6px 0 0;padding-left:18px;">{"".join(items)}</ul>'
        "</section>"
    )


def render_literature(data: dict[str, Any], index: int) -> str:
    parts = [h2(data.get("title") or "文献分享", index)]
    parts.append(paragraphs(data.get("intro") or ""))
    parts.append(render_section_images(data.get("images") or []))
    for paper_index, paper in enumerate(data.get("papers") or [], start=1):
        title = paper.get("title") or "Untitled paper"
        parts.append(
            f'<section style="margin:16px 0 22px;padding:15px 0 0;border-top:1px solid {LINE};">'
            f'<p style="margin:0 0 4px;color:{MUTED};font-size:12px;font-weight:700;line-height:1.5;">文献 {paper_index}</p>'
            f'<p style="margin:0;color:{TEXT};font-size:18px;font-weight:800;line-height:1.5;">{esc(title)}</p>'
            f'<p style="margin:4px 0 0;color:{MUTED};font-size:13px;line-height:1.55;">'
            f'{esc(paper.get("authors") or "")} {esc(paper.get("venue") or "")}</p>'
            f'<p style="margin:7px 0 0;">'
            f'{tag(paper.get("presenter") and "分享人：" + paper.get("presenter"))}'
            f'{tag(paper.get("doi") and "DOI: " + paper.get("doi"))}'
            "</p>"
        )
        parts.append(render_section_images(paper.get("images") or []))
        parts.append(info_card("研究背景", paper.get("background") or ""))
        parts.append(info_card("研究问题", paper.get("research_question") or ""))
        parts.append(info_card("方法与数据", paper.get("methods_data") or ""))
        parts.append(render_findings(paper.get("findings") or []))
        parts.append(info_card("讨论价值", paper.get("discussion_value") or ""))
        if paper.get("summary") and not any(
            paper.get(key) for key in ("background", "research_question", "methods_data", "discussion_value")
        ):
            parts.append(paragraphs(paper.get("summary") or ""))
        comments = paper.get("comments") or []
        if comments:
            parts.append(
                f'<p style="margin:14px 0 0;color:{TEXT};font-size:15px;font-weight:700;line-height:1.5;">讨论摘录</p>'
            )
        for comment in comments:
            parts.append(quote_block(comment.get("text") or "", comment.get("speaker") or ""))
        parts.append("</section>")
    return "".join(parts)


def render_policy(data: dict[str, Any], index: int) -> str:
    parts = [h2(data.get("title") or "时政交流", index)]
    parts.append(tag(data.get("topic") or ""))
    parts.append(paragraphs(data.get("summary") or ""))
    parts.append(render_section_images(data.get("images") or []))
    for viewpoint in data.get("viewpoints") or []:
        parts.append(quote_block(viewpoint.get("text") or "", viewpoint.get("speaker") or ""))
    return "".join(parts)


def render_free_discussion(data: dict[str, Any], index: int) -> str:
    parts = [h2(data.get("title") or "自由讨论与会议总结", index)]
    parts.append(render_section_images(data.get("images") or []))
    for item in data.get("items") or []:
        parts.append(quote_block(item.get("text") or "", item.get("speaker") or ""))
    closing = data.get("closing") or ""
    if closing:
        parts.append(
            f'<section style="margin:14px 0 0;padding:14px;border:1px solid {BORDER};'
            f'border-radius:8px;background:#ffffff;">'
            f'<p style="margin:0;color:{ACCENT};font-size:15px;font-weight:800;line-height:1.5;">会议小结</p>'
            f'{paragraphs(closing, size=15, margin_top=6)}'
            "</section>"
        )
    return "".join(parts)


def render_article(article: dict[str, Any]) -> str:
    meta = article.get("meta") or {}
    sections = article.get("sections") or {}
    parts = [
        f'<h1 style="margin:0 0 10px;color:{TEXT};font-size:23px;line-height:1.35;font-weight:800;">'
        f'{esc(meta.get("title") or "组会纪要")}</h1>',
        f'<p style="margin:0 0 12px;color:{MUTED};font-size:13px;line-height:1.6;">'
        f'{esc(meta.get("date") or "")} {esc(meta.get("group") or "")} '
        f'{esc(meta.get("host") and "主持：" + meta.get("host"))}</p>',
    ]
    cover = meta.get("cover_image") or ""
    if cover:
        parts.append(render_image({"url": cover, "caption": meta.get("cover_caption") or ""}))
    if meta.get("summary"):
        parts.append(
            f'<section style="margin:12px 0 4px;padding:13px 14px;border-radius:8px;'
            f'background:{WARM};border:1px solid #efe6cf;">'
            f'<p style="margin:0;color:{ACCENT_2};font-size:14px;font-weight:800;line-height:1.5;">本期导读</p>'
            f'{paragraphs(meta.get("summary") or "", size=14, margin_top=5)}'
            "</section>"
        )

    section_order = [
        ("english_exchange", render_english),
        ("literature_sharing", render_literature),
        ("policy_discussion", render_policy),
        ("free_discussion", render_free_discussion),
    ]
    visible_index = 1
    for key, renderer in section_order:
        if sections.get(key):
            parts.append(renderer(sections[key], visible_index))
            visible_index += 1
    return "".join(parts)


def main() -> None:
    configure_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument("article_json", type=Path)
    parser.add_argument("--out", type=Path, default=Path("dist"))
    args = parser.parse_args()

    try:
        raw_json = args.article_json.read_text(encoding="utf-8-sig")
        article = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        lines = raw_json.splitlines() if "raw_json" in locals() else []
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
