---
name: wechat-meeting-article
description: Generate WeChat Official Account article drafts from weekly research group meeting materials. Use when Codex or another coding agent needs to turn meeting transcripts, audio transcription documents, English speeches, literature PDFs or abstracts, PPT files, policy discussion notes, attendee comments, or meeting summaries into a polished WeChat-ready meeting-minutes article with mobile-friendly formatting, horizontal English speech cards, source-grounded content, optional HTML export, and optional WeChat draft API payloads.
---

# WeChat Meeting Article

## Overview

Use this skill to produce a publication-ready WeChat Official Account draft from weekly group meeting materials. The agent should separate content reasoning from rendering: generate a structured `article.json` first, then use the bundled renderer to create WeChat-compatible HTML and preview HTML.

## Workflow

1. Inventory the input folder and identify available materials: transcript, English speeches, paper PDFs or abstracts, PPT files, policy notes, comments, images, and meeting metadata.
2. Extract source text with appropriate local tools. Preserve speaker names, paper titles, DOI/URL fields, slide titles, and timestamps when available.
3. Build source-grounded notes before writing. Do not invent attendees, papers, opinions, conclusions, or citations.
4. Generate `article.json` using `references/input-contract.md`.
5. Render HTML:

```bash
python scripts/render_wechat_article.py path/to/article.json --out dist
```

6. Review `dist/article.preview.html` for reading order, missing fields, overlong cards, and mobile layout. Fix `article.json` and rerun the renderer.
7. Deliver `article.wechat.html` as the primary publishable artifact. Only create a WeChat platform draft when credentials and API access are explicitly available.

## Output Policy

Default to these deliverables:

- `article.json`: structured, editable source of truth.
- `article.wechat.html`: WeChat-compatible HTML for copy/import into WeChat, doocs/md, 135, Xiumi, or a custom uploader.
- `article.preview.html`: browser preview wrapper for checking layout before import.
- `source_trace.md`: brief mapping from major claims to source files or transcript excerpts.

Prefer "create draft, then human review" over direct publishing. Do not directly publish through the WeChat API unless the user explicitly asks for automated publication and provides/approves the required credentials.

## Content Rules

- Keep the article suitable for mobile reading: short paragraphs, clear section headings, readable line spacing, and restrained emphasis.
- Preserve the four expected meeting sections when materials support them: English exchange, literature sharing, current affairs or policy discussion, free discussion and meeting summary.
- English speech cards should show one speaker per card. Keep long speeches concise unless the user asks to publish full transcripts.
- Literature sections must distinguish paper facts from meeting comments. If paper metadata is incomplete, mark it for confirmation instead of guessing.
- Policy/current-affairs sections should summarize viewpoints neutrally and attribute them to roles or speakers when available.
- Meeting summaries should be concise and avoid unsupported claims about consensus.

## Resource Guide

- Read `references/input-contract.md` when creating or validating `article.json`.
- Read `references/wechat-formatting.md` when adjusting HTML, SVG, card layout, or editor compatibility.
- Read `references/wechat-api.md` only when the task involves creating a WeChat draft or uploading images/materials.
- Use `scripts/render_wechat_article.py` for deterministic HTML output.
- Use `assets/article-template.html` as the HTML template if the renderer needs visual changes.

## Cross-Agent Portability

This skill is intentionally file-based and tool-light. Any capable agent can reuse it by reading `SKILL.md`, generating `article.json`, and running the renderer with Python 3. The WeChat API step is optional and should be isolated from the writing/rendering pipeline so the skill remains usable in Claude Code, Codex, local scripts, or a future web app.
