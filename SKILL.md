---
name: wechat-meeting-article
description: Generate WeChat Official Account article drafts from weekly research group meeting materials such as transcripts, English speeches, literature PDFs, PPT files, policy notes, and meeting summaries.
---

# WeChat Meeting Article

## Overview

Produce a publication-ready WeChat Official Account draft from weekly reading-sharing meeting materials. Separate content reasoning from rendering: generate a structured `article.json` first, then use the bundled renderer to create WeChat-compatible HTML and preview HTML.

## Intake Gate

Present choices to the user instead of silently applying defaults. **Ask the user directly for information; do not search the filesystem to guess folder locations.**

### Round 1 — before inspecting the folder:

Ask in a single question block:
- **Material folder path**
- **Template** (9 options): `classic`(经典简洁), `notebook`(读书笔记), `journal`(学术笔记), `campus`(校园清新), `minimal`(极简), `magazine`(编辑排版), `warm-note`(温暖笔记), `briefing`(报告风格), `fieldnote`(田野笔记)
- **Palette** (7 options): `classic`(蓝灰暖色), `forest`(森林绿), `blueprint`(蓝图蓝), `warm`(暖棕绿), `ink`(水墨灰黑), `sunrise`(日出珊瑚), `mono`(近单色)
- **Editor**: name, or confirm omission
- **Brand theme**: confirm `zhengeryanzi` (SVG section marks + closing signature)

### Round 2 — after inventory:

- **Date/Host**: infer from materials, confirm if ambiguous
- **Images**: list every image file, ask user what each is and where to place it
- **Cover**: supplied image, PPT title slide, or omit
- **Optional inserts**: honor news, announcements, milestones — confirm inclusion

Do not silently skip any decision. If the user does not respond to a field, confirm the default.

## Workflow

1. **Round 1 intake** (see Intake Gate above).
2. **Inventory** the material folder: transcript, English speeches, paper PDFs, PPT files, images, certificates, honor-news documents.
3. **Round 2 intake** (see Intake Gate above).
4. **Extract** source text with `scripts/extract_materials.py`. All file types (`.docx`, `.pptx`, `.pdf`, `.txt`, `.md`) are fully extracted by default. Do not rely on raw file reads for binary formats. Read selectively from the extracted Markdown for long files.
5. **Prepare notes**:
   ```bash
   python scripts/prepare_article_notes.py extracted_materials --out article_notes
   ```
   Use `paper_notes.json` as a table of contents, then reopen relevant excerpts. For noisy transcripts, `transcript_notes.json` may be sparse — read the full extracted transcript directly in that case.
6. **Scan** for optional inserts (honor news, announcements, milestones). Auto-include when clear; ask when ambiguous.
7. **Read** `references/editorial-style.md` before drafting.
8. **Write `article.json`** directly with the file-writing tool, then immediately run the renderer to validate. To avoid JSON errors with Chinese text, replace `””` inside JSON strings with `””` or rephrase to avoid nested quotes.
   ```bash
   python scripts/render_wechat_article.py article.json --out dist
   ```
   If JSON parse fails, fix the quotes and re-render. Alternative: use `scripts/write_article_json.py article_data.py --out article.json` when UTF-8 Python files are reliable.
   To embed local images as base64 data-uri (so they display in browser preview and auto-upload to WeChat when pasted), add `--embed-images`:
   ```bash
   python scripts/render_wechat_article.py article.json --out dist --embed-images
   ```
   Without `--embed-images`, local image paths must be resolvable from the HTML file; otherwise a placeholder is shown.
9. **Check** quality:
   ```bash
   python scripts/check_article_json.py article.json --html dist/article.wechat.html
   ```
   Treat any issue as blocking unless the user explicitly accepts the risk.
10. **Review** `dist/article.preview.html` for reading order, missing fields, and mobile layout. Fix and re-render if needed.
11. **Deliver**: tell the user to open `article.preview.html` in a browser, select the rendered page, and copy rich text into WeChat. Include suggested title, digest, and cover in the final response.

## Content Rules

- Mobile reading: short paragraphs, clear headings, readable line spacing.
- Meeting flow: lead summary → English exchange → literature sharing → [policy discussion if present] → free discussion → closing. Omit sections without source material.
- **English cards**: one speaker per card, full original text by default. Use `photo` field for speaker portraits (displayed as small circular avatars).
- **Literature**: distinguish paper facts from meeting comments. Expand into background, research question, methods, findings, discussion value. Mark incomplete metadata for confirmation.
- **Transcripts**: treat as noisy evidence. Cross-check names, dates, paper titles, and technical terms against PPT/PDF/filenames. For ASR speaker identification, use these strategies:
  - PPT's `分享人` → likely `发言人1` (the moderator)
  - English exchange speaker order → match against provided speech drafts
  - Interaction patterns ("XX同学你有什么看法?") → identify who calls on whom
  - Teachers: longer evaluative comments, assign tasks. Students: ask questions, discuss assignments
  - When uncertain: use "同学"/"老师" instead of guessing names
- **Date inference priority**: transcript timestamp > user-provided > PPT metadata > filename date > file modification date. Ask to confirm when sources conflict.
- **Images**: never assume what images are from filenames alone. Ask the user what each image is and where to place it. If no usable images, include placement suggestions in the final response. Use `--embed-images` to embed local images as base64 in HTML for reliable browser preview and WeChat paste auto-upload.
- `source` fields are for traceability only; never display filenames or paths in the article body.
- `custom_sections` for occasional inserts (honor news, announcements, milestones). Do not turn the article into a separate news piece.
- Default theme `zhengeryanzi`: static SVG marks, subtle dividers, closing signature with host/editor credits.

## Dependency Setup

Renderer needs only Python 3 stdlib. Material extraction needs optional parsers:

```bash
python -m pip install python-docx python-pptx pdfplumber pypdf
```

On Windows, set `PYTHONIOENCODING=utf-8` if Chinese text becomes garbled.

## Context Budget

- Extract full PDFs to disk, then read selectively.
- If a single extracted file exceeds ~12,000 Chinese chars or ~8,000 English words, use notes as an index and reopen targeted sections.
- Write intermediate conclusions to files so shorter-context models can continue without re-reading.

## Resource Guide

- `references/input-contract.md` — `article.json` schema and rules
- `references/editorial-style.md` — drafting and content style
- `references/material-extraction.md` — `.docx`/`.pptx`/`.pdf` extraction and ASR handling
- `references/wechat-formatting.md` — HTML/SVG/compatibility adjustments
- `references/wechat-api.md` — WeChat API draft/upload (only when needed)
- `scripts/extract_materials.py` — text extraction + manifest
- `scripts/prepare_article_notes.py` — paper/transcript notes
- `scripts/render_wechat_article.py` — deterministic HTML output
- `scripts/check_article_json.py` — quality checks before delivery
- `scripts/update_article_gate.py` — patch intake metadata in existing `article.json`
- `scripts/write_article_json.py` — alternative: Python dict → JSON
- `scripts/draft_article_from_materials.py` — scaffold aid only, not final output
- `assets/article-template.html` — HTML template for renderer visual changes

## Output Policy

Deliverables: `article.json`, `article.wechat.html`, `article.preview.html`. Create `source_trace.md` only when explicitly requested. Prefer draft-then-review over direct publishing.

## Cross-Agent Portability

File-based and tool-light. Any capable agent can reuse by reading `SKILL.md`, generating `article.json`, and running the renderer with Python 3.
