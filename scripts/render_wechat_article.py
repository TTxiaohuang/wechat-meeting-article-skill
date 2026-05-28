#!/usr/bin/env python3
"""Render a structured meeting article JSON file to WeChat-friendly HTML."""

from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
import re
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
BRAND_GREEN = "#0f9f76"
BRAND_GOLD = "#b58a3a"
CURRENT_TEMPLATE = "classic"
CURRENT_PALETTE = "classic"
CURRENT_MOTION = False
EMBED_IMAGES = False
JSON_DIR: Path | None = None

PALETTES: dict[str, dict[str, str]] = {
    "classic": {
        "accent": "#256f8f",
        "accent_2": "#7a6f45",
        "soft": "#eef7fa",
        "warm": "#faf7ef",
        "border": "#d9e8ee",
        "line": "#e7edf0",
    },
    "forest": {
        "accent": "#2f6f5e",
        "accent_2": "#9a7b3f",
        "soft": "#eef8f3",
        "warm": "#fff8e6",
        "border": "#d6ebe2",
        "line": "#e6eee8",
    },
    "blueprint": {
        "accent": "#2f5f8f",
        "accent_2": "#687545",
        "soft": "#eef5fb",
        "warm": "#f7f8ef",
        "border": "#d7e5f2",
        "line": "#e4ecf5",
    },
    "warm": {
        "accent": "#8a5a44",
        "accent_2": "#2f6f5e",
        "soft": "#f7f1ec",
        "warm": "#fff8e8",
        "border": "#eadbd2",
        "line": "#efe5de",
    },
    "ink": {
        "accent": "#2f3a45",
        "accent_2": "#7a6048",
        "soft": "#f4f5f5",
        "warm": "#faf7f1",
        "border": "#dfe3e6",
        "line": "#e8eaec",
    },
    "sunrise": {
        "accent": "#b85d48",
        "accent_2": "#2f7a68",
        "soft": "#fff3ef",
        "warm": "#fff8df",
        "border": "#f0d5c9",
        "line": "#f1e4dd",
    },
    "mono": {
        "accent": "#3f4650",
        "accent_2": "#686f78",
        "soft": "#f6f7f8",
        "warm": "#fafafa",
        "border": "#e1e4e8",
        "line": "#eceff2",
    },
    "sakura": {
        "accent": "#c46b8a",
        "accent_2": "#8a6b5e",
        "soft": "#fdf2f5",
        "warm": "#fff8f0",
        "border": "#f0d4de",
        "line": "#f5e4ea",
    },
    "ocean": {
        "accent": "#1a6b8a",
        "accent_2": "#4a7a5e",
        "soft": "#eef6fa",
        "warm": "#f5faf7",
        "border": "#c8dde8",
        "line": "#dde9f0",
    },
}

TEMPLATE_ALIASES = {
    "default": "classic",
    "intro": "classic",
    "simple": "classic",
    "journal": "classic",
    "minimal": "classic",
    "brief": "briefing",
    "report": "briefing",
    "fieldnote": "briefing",
    "reading-note": "notebook",
    "notes": "notebook",
    "warmnote": "notebook",
    "warm-note": "notebook",
    "warm_notes": "notebook",
    "academic": "classic",
    "school": "campus",
    "editorial": "magazine",
}
SUPPORTED_TEMPLATES = {
    "classic",
    "notebook",
    "campus",
    "magazine",
    "briefing",
}


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def normalize_choice(value: Any, allowed: set[str], default: str, aliases: dict[str, str] | None = None) -> str:
    choice = str(value or "").strip().lower().replace("_", "-")
    if aliases:
        choice = aliases.get(choice, choice)
    return choice if choice in allowed else default


def apply_visual_style(article: dict[str, Any]) -> tuple[str, str]:
    global ACCENT, ACCENT_2, SOFT, WARM, BORDER, LINE, CURRENT_TEMPLATE, CURRENT_PALETTE, CURRENT_MOTION

    meta = article.get("meta") or {}
    template = normalize_choice(article.get("template") or meta.get("template"), SUPPORTED_TEMPLATES, "classic", TEMPLATE_ALIASES)
    palette = normalize_choice(article.get("palette") or meta.get("palette") or template, set(PALETTES), "classic")
    colors = PALETTES[palette]

    ACCENT = colors["accent"]
    ACCENT_2 = colors["accent_2"]
    SOFT = colors["soft"]
    WARM = colors["warm"]
    BORDER = colors["border"]
    LINE = colors["line"]
    CURRENT_TEMPLATE = template
    CURRENT_PALETTE = palette
    CURRENT_MOTION = bool(article.get("experimental_motion") or meta.get("experimental_motion"))
    return template, palette


IMAGE_MARKER_RE = re.compile(r"\{\{image:([^}|]+?)(?:\|([^}]*))?\}\}")


def paragraphs(text: str, *, size: int = 15, margin_top: int = 8) -> str:
    if not text:
        return ""
    # Check for inline image markers {{image:src}} or {{image:src|caption}}
    if "{{image:" in text:
        return _render_with_inline_images(text, size=size, margin_top=margin_top)
    chunks = [part.strip() for part in str(text).replace("\r\n", "\n").split("\n\n") if part.strip()]
    if not chunks:
        chunks = [str(text).strip()]
    rendered = []
    for index, chunk in enumerate(chunks):
        rendered.append(
            f'<p style="margin:{margin_top if index == 0 else 7}px 0 0;'
            f'color:{TEXT};font-size:{size}px;line-height:1.82;text-align:justify;">'
            f'{esc(chunk).replace(chr(10), "<br>")}</p>'
        )
    return "".join(rendered)


def _render_with_inline_images(text: str, size: int = 15, margin_top: int = 8) -> str:
    """Render text that contains {{image:src|caption}} markers inline."""
    parts: list[str] = []
    last_end = 0
    for match in IMAGE_MARKER_RE.finditer(text):
        # Text before this marker
        before = text[last_end:match.start()].strip()
        if before:
            parts.append(_text_chunks_html(before, size, margin_top if last_end == 0 else 0))
        # The image itself
        src = match.group(1).strip()
        caption = (match.group(2) or "").strip()
        parts.append(render_image({"url": src, "caption": caption} if caption else src))
        last_end = match.end()
    # Remaining text after last marker
    after = text[last_end:].strip()
    if after:
        parts.append(_text_chunks_html(after, size, 0))
    return "".join(parts)


def _text_chunks_html(text: str, size: int, margin_top: int) -> str:
    """Split text by double-newline into paragraph HTML."""
    chunks = [p.strip() for p in text.replace("\r\n", "\n").split("\n\n") if p.strip()]
    if not chunks:
        chunks = [text]
    rendered = []
    for i, chunk in enumerate(chunks):
        rendered.append(
            f'<p style="margin:{margin_top if i == 0 else 7}px 0 0;'
            f'color:{TEXT};font-size:{size}px;line-height:1.82;text-align:justify;">'
            f'{esc(chunk).replace(chr(10), "<br>")}</p>'
        )
    return "".join(rendered)


def brand_enabled(article: dict[str, Any]) -> bool:
    meta = article.get("meta") or {}
    return (article.get("theme") or meta.get("theme") or "").lower() == "zhengeryanzi"


def brand_icon(size: int = 28) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 64 64" '
        f'fill="none" style="display:block;">'
        f'<rect x="10" y="14" width="44" height="36" rx="6" fill="#f8fbf8" stroke="{BRAND_GREEN}" stroke-width="3"/>'
        f'<path d="M18 24h28M18 32h22M18 40h18" stroke="{BRAND_GREEN}" stroke-width="3" stroke-linecap="round"/>'
        f'<circle cx="48" cy="18" r="5" fill="{BRAND_GOLD}"/>'
        f'</svg>'
    )


def render_brand_signature(meta: dict[str, Any]) -> str:
    credits = []
    if meta.get("host"):
        credits.append(f"主持：{meta.get('host')}")
    editor = meta.get("editor") or meta.get("article_editor")
    if editor:
        credits.append(f"推文编辑：{editor}")
    credits_html = (
        f'<p style="margin:3px 0 0;color:{MUTED};font-size:12px;line-height:1.5;">{esc(" ｜ ".join(credits))}</p>'
        if credits
        else ""
    )
    return (
        '<section data-brand="zhengeryanzi" style="margin:26px 0 4px;padding:14px 12px;'
        'border-top:1px solid #e6efe9;text-align:center;">'
        f'<section style="width:30px;margin:0 auto 6px;">{brand_icon(28)}</section>'
        f'<p style="margin:0;color:{TEXT};font-size:14px;font-weight:700;line-height:1.6;">本期记录由郑而研资整理</p>'
        f'{credits_html}'
        '</section>'
    )


def brand_section_mark() -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 32 32" '
        f'fill="none" style="display:inline-block;vertical-align:-3px;margin-right:5px;">'
        f'<path d="M6 17c8-1 13-5 17-11 2 8-2 16-10 19-3 1-6 1-9 0 4-1 7-3 9-6" '
        f'fill="#eaf7f1" stroke="{BRAND_GREEN}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        f'</svg>'
    )


def sparkle_mark(size: int = 20) -> str:
    animate = (
        '<animate attributeName="opacity" values="0.65;1;0.65" dur="1.8s" repeatCount="indefinite"/>'
        if CURRENT_MOTION
        else ""
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 32 32" '
        f'fill="none" style="display:inline-block;vertical-align:-4px;margin-right:6px;">'
        f'<path d="M16 4l3.2 8.2L28 16l-8.8 3.8L16 28l-3.2-8.2L4 16l8.8-3.8L16 4z" '
        f'fill="{WARM}" stroke="{ACCENT_2}" stroke-width="2" stroke-linejoin="round">{animate}</path>'
        f'</svg>'
    )


def h2(title: str, index: int | None = None, branded: bool = False) -> str:
    number = f"{index:02d}" if index is not None else ""
    number_html = (
        f'<span style="display:inline-block;margin-right:8px;color:{ACCENT_2};font-size:13px;'
        f'font-weight:700;letter-spacing:0;">{number}</span>'
        if number
        else ""
    )
    title_html = f'{number_html}{brand_section_mark() if branded else ""}{esc(title)}'
    if CURRENT_TEMPLATE == "notebook":
        return (
            f'<section style="margin:30px 0 14px;padding:10px 12px;border-left:4px solid {ACCENT};'
            f'background:{SOFT};border-radius:0 8px 8px 0;">'
            f'<p style="margin:0;color:{TEXT};font-size:19px;font-weight:800;line-height:1.45;">'
            f'{title_html}</p>'
            "</section>"
        )
    if CURRENT_TEMPLATE == "campus":
        return (
            f'<section style="margin:30px 0 14px;padding:11px 13px;border:1px solid {BORDER};'
            f'border-radius:8px;background:{SOFT};">'
            f'<p style="margin:0;color:{TEXT};font-size:19px;font-weight:800;line-height:1.45;">'
            f'{number_html}{brand_section_mark() if branded else ""}{esc(title)}</p>'
            "</section>"
        )
    if CURRENT_TEMPLATE == "magazine":
        return (
            f'<section style="margin:32px 0 15px;padding:0;">'
            f'<p style="margin:0;color:{ACCENT_2};font-size:13px;font-weight:800;line-height:1.4;">'
            f'{number or "READ"}</p>'
            f'<p style="margin:3px 0 0;color:{TEXT};font-size:21px;font-weight:900;line-height:1.35;">'
            f'{brand_section_mark() if branded else ""}{esc(title)}</p>'
            f'<p style="margin:8px 0 0;width:100%;border-top:3px solid {ACCENT};"></p>'
            "</section>"
        )
    if CURRENT_TEMPLATE == "briefing":
        number_chip = (
            f'<span style="display:inline-block;margin-right:9px;padding:1px 7px;border-radius:999px;'
            f'background:{ACCENT};color:#ffffff;font-size:12px;font-weight:800;line-height:1.6;">{number}</span>'
            if number
            else ""
        )
        return (
            f'<section style="margin:30px 0 14px;padding:9px 0 8px;border-top:2px solid {ACCENT};'
            f'border-bottom:1px solid {LINE};">'
            f'<p style="margin:0;color:{TEXT};font-size:19px;font-weight:800;line-height:1.45;">'
            f'{number_chip}{brand_section_mark() if branded else ""}{esc(title)}</p>'
            "</section>"
        )
    # classic (default)
    return (
        '<section style="margin:30px 0 14px;padding:0 0 8px;border-bottom:1px solid #eef2f4;">'
        f'<p style="margin:0;color:{TEXT};font-size:19px;font-weight:800;line-height:1.45;">'
        f'{title_html}</p>'
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
        f'<section style="margin:12px 0 0;padding:0 0 0 10px;border-left:3px solid {BORDER};">'
        f'<p style="margin:0 0 4px;color:{ACCENT};font-size:14px;font-weight:700;line-height:1.5;">{esc(title)}</p>'
        f'{paragraphs(text, size=14, margin_top=0)}'
        "</section>"
    )


def quote_mark_svg(size: int = 18) -> str:
    """Generate a template-appropriate SVG quote mark."""
    if CURRENT_TEMPLATE == "notebook":
        # Corner bracket 「
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none"><path d="M4 4v8h8M4 4h8v8" stroke="{ACCENT}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" opacity="0.5"/></svg>'
    elif CURRENT_TEMPLATE == "campus":
        # Circle dot
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none"><circle cx="8" cy="8" r="5" fill="{ACCENT}" opacity="0.35"/><circle cx="16" cy="14" r="4" fill="{ACCENT}" opacity="0.2"/></svg>'
    elif CURRENT_TEMPLATE == "magazine":
        # Large stylized "
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{size+4}" height="{size+4}" viewBox="0 0 28 28" fill="none"><path d="M6 8c0-3 2-6 6-6v4c-2 0-2 2-2 4h2v6H6V8zm10 0c0-3 2-6 6-6v4c-2 0-2 2-2 4h2v6H16V8z" fill="{ACCENT}" opacity="0.25"/></svg>'
    elif CURRENT_TEMPLATE == "briefing":
        # Square bracket with line
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none"><path d="M6 3v18M6 3h5M6 21h5" stroke="{ACCENT}" stroke-width="2" stroke-linecap="round" opacity="0.4"/></svg>'
    else:
        # classic: accent dot
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="6" fill="{ACCENT}" opacity="0.2"/></svg>'
    return f'<span style="display:inline-block;margin-right:6px;vertical-align:-2px;">{svg}</span>'


def quote_block(text: str, speaker: str = "", images: list[Any] | None = None) -> str:
    mark = quote_mark_svg()
    label_html = (
        f'<p style="margin:0 0 4px;color:{ACCENT};font-size:14px;font-weight:700;line-height:1.5;">'
        f'{mark}{esc(speaker)}</p>'
        if speaker
        else ""
    )
    images_html = render_section_images(images or [])
    if CURRENT_TEMPLATE == "notebook":
        return (
            f'<blockquote style="margin:10px 0 0;padding:10px 0 10px 12px;border-left:3px solid {ACCENT};'
            f'border-top:1px solid {LINE};border-bottom:1px solid {LINE};color:{TEXT};line-height:1.75;">'
            f"{label_html}{paragraphs(text, size=14, margin_top=0)}{images_html}"
            "</blockquote>"
        )
    return (
        f'<blockquote style="margin:10px 0 0;padding:11px 13px;border-left:3px solid {ACCENT};'
        f'background:{SOFT};color:{TEXT};line-height:1.75;">'
        f"{label_html}{paragraphs(text, size=14, margin_top=0)}{images_html}"
        "</blockquote>"
    )


def resolve_image_src(src: str) -> tuple[str, bool]:
    """Resolve image src for HTML output.

    Returns (resolved_src, is_placeholder).
    - Remote URLs pass through.
    - Local files: embed as data-uri if EMBED_IMAGES, else return placeholder marker.
    """
    if not src or src.startswith(("http://", "https://", "data:")):
        return src, False
    # Try to resolve relative path against JSON directory
    candidate = Path(src)
    if not candidate.is_absolute() and JSON_DIR:
        candidate = JSON_DIR / src
    if candidate.is_file():
        if EMBED_IMAGES:
            mime = mimetypes.guess_type(str(candidate))[0] or "image/jpeg"
            data = base64.b64encode(candidate.read_bytes()).decode()
            return f"data:{mime};base64,{data}", False
        return src, False
    # File not found — show placeholder
    return src, True


def image_placeholder(src: str) -> str:
    return (
        f'<section style="margin:14px 0;padding:18px 14px;border:1.5px dashed {BORDER};'
        f"border-radius:8px;text-align:center;\">"
        f'<p style="margin:0;color:{MUTED};font-size:13px;line-height:1.6;">'
        f"[ 图片占位 ] {esc(src)} — 请在微信编辑器中手动插入</p>"
        "</section>"
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
    resolved, is_placeholder = resolve_image_src(src)
    if is_placeholder:
        return image_placeholder(src)
    return (
        '<section style="margin:14px 0;text-align:center;">'
        f'<img src="{esc(resolved)}" alt="{esc(alt)}" style="display:block;width:100%;max-width:100%;'
        'height:auto;border-radius:8px;border:0;" />'
        f'{f"<p style=\'margin:6px 0 0;color:{MUTED};font-size:12px;line-height:1.5;text-align:center;\'>{esc(caption)}</p>" if caption else ""}'
        "</section>"
    )


def render_section_images(images: list[Any]) -> str:
    return "".join(render_image(image) for image in images or [])


def render_summary_card(summary: str) -> str:
    if not summary:
        return ""
    if CURRENT_TEMPLATE == "notebook":
        return (
            f'<section style="margin:12px 0 4px;padding:10px 12px;border-left:4px solid {ACCENT};'
            f'background:{SOFT};border-radius:0 8px 8px 0;">'
            f'<p style="margin:0;color:{ACCENT};font-size:14px;font-weight:800;line-height:1.5;">本期导读</p>'
            f'{paragraphs(summary, size=14, margin_top=5)}'
            "</section>"
        )
    if CURRENT_TEMPLATE == "campus":
        return (
            f'<section style="margin:12px 0 4px;padding:14px 15px;border-radius:8px;'
            f'background:{SOFT};border:1px solid {BORDER};">'
            f'<p style="margin:0;color:{ACCENT};font-size:15px;font-weight:900;line-height:1.5;">本期导读</p>'
            f'{paragraphs(summary, size=14, margin_top=5)}'
            "</section>"
        )
    if CURRENT_TEMPLATE == "magazine":
        return (
            f'<section style="margin:14px 0 4px;padding:15px 0 14px;border-top:3px solid {ACCENT};'
            f'border-bottom:1px solid {LINE};">'
            f'<p style="margin:0;color:{ACCENT};font-size:15px;font-weight:900;line-height:1.5;">本期导读</p>'
            f'{paragraphs(summary, size=15, margin_top=5)}'
            "</section>"
        )
    if CURRENT_TEMPLATE == "briefing":
        return (
            f'<section style="margin:12px 0 4px;padding:13px 14px;border-top:2px solid {ACCENT_2};'
            f'border-bottom:1px solid {LINE};background:{WARM};">'
            f'<p style="margin:0;color:{ACCENT_2};font-size:14px;font-weight:800;line-height:1.5;">本期导读</p>'
            f'{paragraphs(summary, size=14, margin_top=5)}'
            "</section>"
        )
    # classic (default)
    return (
        f'<section style="margin:12px 0 4px;padding:13px 14px;border-radius:8px;'
        f'background:{WARM};border:1px solid #efe6cf;">'
        f'<p style="margin:0;color:{ACCENT_2};font-size:14px;font-weight:800;line-height:1.5;">本期导读</p>'
        f'{paragraphs(summary, size=14, margin_top=5)}'
        "</section>"
    )


def insert_badge(label: str) -> str:
    return (
        f'<span style="display:inline-block;margin:0 0 8px;padding:2px 9px;border-radius:999px;'
        f'background:{ACCENT};color:#ffffff;font-size:12px;font-weight:800;line-height:1.6;">{esc(label)}</span>'
    )


def render_custom_insert(item: dict[str, Any]) -> str:
    kind = normalize_choice(
        item.get("type") or item.get("kind"),
        {"honor-news", "honor_news", "announcement", "milestone", "note"},
        "note",
    ).replace("_", "-")
    title = item.get("title") or {
        "honor-news": "喜讯",
        "announcement": "通知",
        "milestone": "进展",
        "note": "插播",
    }.get(kind, "插播")
    text = item.get("text") or item.get("summary") or ""
    if not text and kind != "honor-news":
        return ""

    images_html = render_section_images(item.get("images") or [])
    meta_parts = [item.get("person"), item.get("award"), item.get("organization"), item.get("date")]
    meta_line = " ｜ ".join(str(part).strip() for part in meta_parts if part)
    body = text
    if kind == "honor-news" and not body:
        person = item.get("person") or "同学"
        award = item.get("award") or "相关荣誉"
        body = f"祝贺{person}荣获{award}。"

    if kind == "honor-news":
        return (
            f'<section data-insert="honor-news" style="margin:18px 0;padding:15px 14px;border-radius:8px;'
            f'border:1px solid {BORDER};background:{WARM};">'
            f'<p style="margin:0;color:{ACCENT_2};font-size:14px;font-weight:900;line-height:1.5;">'
            f'{sparkle_mark(20)}{esc(title)}</p>'
            f'{f"<p style=\'margin:5px 0 0;color:{MUTED};font-size:13px;line-height:1.55;\'>{esc(meta_line)}</p>" if meta_line else ""}'
            f'{paragraphs(body, size=14, margin_top=7)}'
            f'{images_html}'
            "</section>"
        )

    if kind == "announcement":
        return (
            f'<section data-insert="announcement" style="margin:16px 0;padding:13px 14px;border-left:4px solid {ACCENT};'
            f'background:{SOFT};">'
            f'{insert_badge("插播通知")}'
            f'<p style="margin:0;color:{TEXT};font-size:17px;font-weight:800;line-height:1.45;">{esc(title)}</p>'
            f'{f"<p style=\'margin:4px 0 0;color:{MUTED};font-size:13px;line-height:1.55;\'>{esc(meta_line)}</p>" if meta_line else ""}'
            f'{paragraphs(body, size=14, margin_top=7)}'
            f'{images_html}'
            "</section>"
        )

    if kind == "milestone":
        return (
            f'<section data-insert="milestone" style="margin:16px 0;padding:13px 0;border-top:1px solid {LINE};'
            f'border-bottom:1px solid {LINE};">'
            f'<p style="margin:0;color:{ACCENT};font-size:14px;font-weight:900;line-height:1.5;">阶段进展</p>'
            f'<p style="margin:3px 0 0;color:{TEXT};font-size:17px;font-weight:800;line-height:1.45;">{esc(title)}</p>'
            f'{f"<p style=\'margin:4px 0 0;color:{MUTED};font-size:13px;line-height:1.55;\'>{esc(meta_line)}</p>" if meta_line else ""}'
            f'{paragraphs(body, size=14, margin_top=7)}'
            f'{images_html}'
            "</section>"
        )

    return (
        f'<section data-insert="note" style="margin:14px 0;padding:12px 13px;border:1px solid {BORDER};'
        f'border-radius:8px;background:#ffffff;">'
        f'<p style="margin:0;color:{ACCENT};font-size:15px;font-weight:800;line-height:1.5;">{esc(title)}</p>'
        f'{paragraphs(body, size=14, margin_top=6)}'
        f'{images_html}'
        "</section>"
    )


def render_custom_sections(article: dict[str, Any], placement: str) -> str:
    inserts = article.get("custom_sections") or article.get("inserts") or []
    if not isinstance(inserts, list):
        return ""
    rendered = []
    for item in inserts:
        if not isinstance(item, dict):
            continue
        item_placement = item.get("placement") or "after_lead"
        if item_placement == placement:
            rendered.append(render_custom_insert(item))
    return "".join(rendered)


AVATAR_COLORS = [
    "#4a90d9",  # blue
    "#5ba55b",  # green
    "#c46b8a",  # pink
    "#d4a04a",  # gold
    "#7a6bb5",  # purple
    "#5a9e9e",  # teal
    "#c47a4a",  # orange
]


def generate_avatar_svg(speaker: str, card_index: int) -> str:
    """Generate an SVG data-uri avatar with the speaker's initial letter."""
    letter = (speaker.strip()[0] if speaker.strip() else "?").upper()
    color = AVATAR_COLORS[(card_index - 1) % len(AVATAR_COLORS)]
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 36 36">'
        f'<circle cx="18" cy="18" r="18" fill="{color}"/>'
        f'<text x="18" y="18" text-anchor="middle" dominant-baseline="central"'
        f' font-family="-apple-system,BlinkMacSystemFont,sans-serif"'
        f' font-size="16" font-weight="700" fill="#ffffff">{letter}</text>'
        f'</svg>'
    )
    return f"data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}"


def render_english(data: dict[str, Any], index: int, branded: bool = False) -> str:
    speeches = data.get("speeches") or []
    parts = [h2(data.get("title") or "英语交流", index, branded)]
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
        photo = item.get("photo") or ""
        photo_html = ""
        if photo:
            resolved_photo, is_ph = resolve_image_src(photo)
            if not is_ph:
                photo_html = (
                    f'<section style="width:36px;height:36px;border-radius:50%;'
                    f'background-image:url({esc(resolved_photo)});'
                    f'background-size:cover;background-position:center;'
                    f'margin-bottom:8px;"></section>'
                )
            else:
                photo_html = (
                    f'<section style="width:36px;height:36px;border-radius:50%;'
                    f'background-image:url({generate_avatar_svg(speaker, card_index)});'
                    f'background-size:cover;margin-bottom:8px;"></section>'
                )
        else:
            photo_html = (
                f'<section style="width:36px;height:36px;border-radius:50%;'
                f'background-image:url({generate_avatar_svg(speaker, card_index)});'
                f'background-size:cover;margin-bottom:8px;"></section>'
            )
        cards.append(
            f'<section style="box-sizing:border-box;display:inline-block;vertical-align:top;width:92%;'
            f'max-width:340px;min-height:220px;margin:8px 12px 8px 0;padding:16px 16px 14px;white-space:normal;'
            f'border:1px solid {BORDER};border-radius:8px;background:#ffffff;">'
            f'<p style="margin:0;color:{MUTED};font-size:12px;line-height:1.4;text-align:right;">{card_index}/{total}</p>'
            f'{photo_html}'
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


def render_literature(data: dict[str, Any], index: int, branded: bool = False) -> str:
    parts = [h2(data.get("title") or "文献分享", index, branded)]
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
            parts.append(quote_block(comment.get("text") or "", comment.get("speaker") or "",
                                     comment.get("images")))
        parts.append("</section>")
    return "".join(parts)


def render_policy(data: dict[str, Any], index: int, branded: bool = False) -> str:
    parts = [h2(data.get("title") or "时政交流", index, branded)]
    parts.append(tag(data.get("topic") or ""))
    parts.append(paragraphs(data.get("summary") or ""))
    parts.append(render_section_images(data.get("images") or []))
    for viewpoint in data.get("viewpoints") or []:
        parts.append(quote_block(viewpoint.get("text") or "", viewpoint.get("speaker") or "",
                                 viewpoint.get("images")))
    return "".join(parts)


def render_free_discussion(data: dict[str, Any], index: int, branded: bool = False) -> str:
    parts = [h2(data.get("title") or "自由讨论与会议总结", index, branded)]
    parts.append(render_section_images(data.get("images") or []))
    for item in data.get("items") or []:
        parts.append(quote_block(item.get("text") or "", item.get("speaker") or "",
                                 item.get("images")))
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
    template_name, palette_name = apply_visual_style(article)
    meta = article.get("meta") or {}
    sections = article.get("sections") or {}
    branded = brand_enabled(article)
    parts = [
        f'<section data-template="{esc(template_name)}" data-palette="{esc(palette_name)}" '
        f'style="margin:0;padding:0;">'
    ]
    parts.extend([
        f'<h1 style="margin:0 0 10px;color:{TEXT};font-size:23px;line-height:1.35;font-weight:800;">'
        f'{esc(meta.get("title") or "组会纪要")}</h1>',
        f'<p style="margin:0 0 12px;color:{MUTED};font-size:13px;line-height:1.6;">'
        f'{esc(meta.get("date") or "")} {esc(meta.get("group") or "")} '
        f'{esc(meta.get("host") and "主持：" + meta.get("host"))}</p>',
    ])
    cover = meta.get("cover_image") or ""
    if cover:
        parts.append(render_image({"url": cover, "caption": meta.get("cover_caption") or ""}))
    if meta.get("summary"):
        parts.append(render_summary_card(meta.get("summary") or ""))
    parts.append(render_custom_sections(article, "after_lead"))

    section_order = [
        ("english_exchange", render_english),
        ("literature_sharing", render_literature),
        ("policy_discussion", render_policy),
        ("free_discussion", render_free_discussion),
    ]
    visible_index = 1
    for key, renderer in section_order:
        parts.append(render_custom_sections(article, f"before_{key}"))
        if sections.get(key):
            parts.append(renderer(sections[key], visible_index, branded))
            visible_index += 1
        parts.append(render_custom_sections(article, f"after_{key}"))
    parts.append(render_custom_sections(article, "before_closing"))
    if branded:
        parts.append(render_brand_signature(meta))
    parts.append("</section>")
    return "".join(parts)


def main() -> None:
    global EMBED_IMAGES, JSON_DIR
    configure_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument("article_json", type=Path)
    parser.add_argument("--out", type=Path, default=Path("dist"))
    parser.add_argument("--embed-images", action="store_true",
                        help="Embed local images as base64 data-uri in HTML output")
    args = parser.parse_args()

    EMBED_IMAGES = args.embed_images
    JSON_DIR = args.article_json.resolve().parent

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
            "Tip: write article.json directly and avoid unescaped Chinese quotes (\"“”\") inside JSON strings. ",
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
