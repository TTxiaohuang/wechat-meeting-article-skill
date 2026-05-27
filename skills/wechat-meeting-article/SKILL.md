---
name: wechat-meeting-article
description: Generate WeChat Official Account article drafts from weekly research group meeting materials. Use when Codex or another coding agent needs to turn meeting transcripts, audio transcription documents, English speeches, literature PDFs or abstracts, PPT files, policy discussion notes, attendee comments, or meeting summaries into a polished WeChat-ready meeting-minutes article with mobile-friendly formatting, horizontal English speech cards, source-grounded content, optional HTML export, and optional WeChat draft API payloads.
---

# WeChat Meeting Article

## Overview

Use this skill to produce a publication-ready WeChat Official Account draft from weekly group meeting materials. The agent should separate content reasoning from rendering: generate a structured `article.json` first, then use the bundled renderer to create WeChat-compatible HTML and preview HTML.

## Workflow

1. Inventory the input folder and identify available materials: transcript, English speeches, paper PDFs or abstracts, PPT files, policy notes, comments, images, and meeting metadata.
2. Extract source text before writing. For `.docx`, `.pptx`, and `.pdf`, do not rely on raw file reads; use `scripts/extract_materials.py` or equivalent document parsers. Preserve speaker names, paper titles, DOI/URL fields, slide titles, and timestamps when available.
3. Build source-grounded notes before writing. Do not invent attendees, papers, opinions, conclusions, or citations.
4. Apply `references/editorial-style.md` before drafting. Keep sections flexible: omit unsupported sections instead of filling them with generic text.
5. Create `article.json` with AI synthesis from the extracted materials and `references/input-contract.md`. Do not deliver deterministic scaffold output directly. Use `scripts/draft_article_from_materials.py extracted_materials --out article.scaffold.json` only as an optional inventory/scaffold aid, then write a separate expanded `article.json` from the sources.
6. Render HTML:

```bash
python scripts/render_wechat_article.py path/to/article.json --out dist
```

7. Run `scripts/check_article_json.py article.json --html dist/article.wechat.html` and fix any warnings that affect publication quality.
8. Review `dist/article.preview.html` for reading order, missing fields, overlong cards, and mobile layout. Fix `article.json` and rerun the renderer.
9. Tell the user to import by opening `article.preview.html` in a browser, selecting the rendered page, and copying the rendered rich text into WeChat. Do not tell them to paste the raw `article.wechat.html` source into the WeChat editor.
10. Deliver `article.wechat.html` as the primary HTML artifact. Only create a WeChat platform draft when credentials and API access are explicitly available.

## Dependency Setup

The renderer only needs Python 3 standard library. Material extraction needs optional parsers:

```bash
python -m pip install python-docx python-pptx pdfplumber pypdf
```

On Windows, set UTF-8 output if Chinese text becomes garbled:

```powershell
$env:PYTHONIOENCODING="utf-8"
```

For a local extraction pass:

```bash
python scripts/extract_materials.py path/to/material-folder --out extracted_materials
```

Script paths in examples are relative to the skill directory. When an agent is working from another folder, use the absolute path to the script.

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
- Omit any section that lacks source material. Do not force a current-affairs/policy section into older meetings that did not include one.
- English speech cards should show one speaker per card. If the user provides each person's English speech draft, publish the full original text by default; do not summarize or polish it unless explicitly asked.
- Literature sections must distinguish paper facts from meeting comments. Expand paper introductions into background, research question, methods/data, core findings, and discussion value when the source supports it. If paper metadata is incomplete, mark it for confirmation instead of guessing.
- Policy/current-affairs sections should summarize viewpoints neutrally and attribute them to roles or speakers when available.
- Meeting summaries should be concise and avoid unsupported claims about consensus.
- Keep `source` fields for traceability only. Do not display filenames, local paths, or transcript names in the WeChat article body.
- Use provided meeting photos, PPT screenshots, paper figures, or generated cover assets when available and relevant. Do not invent data-bearing academic figures.
- If no usable images are provided, include image placement suggestions in the final response or `source_trace.md` instead of fabricating figures.

## Resource Guide

- Read `references/input-contract.md` when creating or validating `article.json`.
- Read `references/editorial-style.md` before drafting or revising article content.
- Read `references/material-extraction.md` when the task includes `.docx`, `.pptx`, `.pdf`, `.txt`, or `.md` materials.
- Read `references/wechat-formatting.md` when adjusting HTML, SVG, card layout, or editor compatibility.
- Read `references/wechat-api.md` only when the task involves creating a WeChat draft or uploading images/materials.
- Use `scripts/extract_materials.py` to create Markdown text extracts and `materials_manifest.json`.
- Use `scripts/draft_article_from_materials.py` only to create `article.scaffold.json` as an inventory/scaffold aid. Never treat scaffold output as the final article.
- Use `scripts/create_article_json.py` to create a valid starter JSON file.
- Use `scripts/render_wechat_article.py` for deterministic HTML output.
- Use `scripts/check_article_json.py` before delivery to catch source filename leaks, missing literature structure, and suspiciously short English speeches.
- Use `assets/article-template.html` as the HTML template if the renderer needs visual changes.

## Cross-Agent Portability

This skill is intentionally file-based and tool-light. Any capable agent can reuse it by reading `SKILL.md`, generating `article.json`, and running the renderer with Python 3. The WeChat API step is optional and should be isolated from the writing/rendering pipeline so the skill remains usable in Claude Code, Codex, local scripts, or a future web app.
