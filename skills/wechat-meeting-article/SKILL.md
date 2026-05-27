---
name: wechat-meeting-article
description: Generate WeChat Official Account article drafts from weekly research group meeting materials. Use when Codex or another coding agent needs to turn meeting transcripts, audio transcription documents, English speeches, literature PDFs or abstracts, PPT files, policy discussion notes, attendee comments, or meeting summaries into a polished WeChat-ready meeting-minutes article with mobile-friendly formatting, horizontal English speech cards, source-grounded content, optional HTML export, and optional WeChat draft API payloads.
---

# WeChat Meeting Article

## Overview

Use this skill to produce a publication-ready WeChat Official Account draft from weekly group meeting materials. The article is always a reading-sharing meeting article; visual templates change the style, not the core meeting structure. Separate content reasoning from rendering: generate a structured `article.json` first, then use the bundled renderer to create WeChat-compatible HTML and preview HTML.

## Intake Gate

Before drafting, collect only the metadata that affects publication quality:

- Material folder path.
- Meeting date, or permission to infer it from materials.
- Host when not obvious from materials.
- Article editor, or explicit confirmation that editor credit should be omitted.
- Preferred visual style, or explicit confirmation that the default `classic` style is acceptable.
- Whether provided images, PPT screenshots, certificates, or cover assets should be used.

Do not ask a long questionnaire, but do not skip editor and visual-style decisions. Infer obvious details from filenames, PPT titles, transcripts, or user-provided choices. Ask one confirmation question only when a detail is missing, sensitive, contradictory, or likely to change the article emphasis. Record decisions in `_meta.intake_gate`; if editor is intentionally omitted, set `_meta.intake_gate.editor.status` to `omitted_confirmed`.

## Workflow

1. Inventory the input folder and identify available materials: transcript, English speeches, paper PDFs or abstracts, PPT files, policy notes, comments, images, certificates, honor-news documents, and meeting metadata.
2. Apply the Intake Gate. Do not keep asking once details are clear, inferable, or the user has accepted defaults.
3. Extract source text before writing. For `.docx`, `.pptx`, and `.pdf`, do not rely on raw file reads; use `scripts/extract_materials.py` or equivalent document parsers. PDFs are extracted in full by default; read selectively from the extracted text instead of stuffing entire long papers into context. Preserve speaker names, paper titles, DOI/URL fields, slide titles, and timestamps when available.
4. Create intermediate notes before drafting:

```bash
python scripts/prepare_article_notes.py extracted_materials --out article_notes
```

Read `article_notes/paper_notes.json`, `article_notes/transcript_notes.json`, and `article_notes/intake_decision.template.json` first. For long extracted files, use the notes as an index and reopen only relevant excerpts instead of reading every extracted character into context.
5. Scan extracted materials and notes for optional inserts such as honor news, announcements, project milestones, paper acceptances, activity notices, or supplied photos. Auto-include clearly publication-ready inserts; ask one confirmation question when they are ambiguous, sensitive, or incomplete.
6. Build source-grounded notes before writing. Do not invent attendees, papers, opinions, conclusions, awards, or citations.
7. Apply `references/editorial-style.md` before drafting. Keep sections flexible: omit unsupported sections instead of filling them with generic text.
8. Create `article.json` with AI synthesis from the extracted materials and `references/input-contract.md`. Do not deliver deterministic scaffold output directly. Use `scripts/draft_article_from_materials.py extracted_materials --out article.scaffold.json` only as an optional inventory/scaffold aid. Do not handwrite large raw JSON. Prefer writing `article_data.py` with an `ARTICLE` dict and generating JSON with:

```bash
python scripts/write_article_json.py article_data.py --out article.json
```

9. Render HTML:

```bash
python scripts/render_wechat_article.py path/to/article.json --out dist
```

10. Run `scripts/check_article_json.py article.json --html dist/article.wechat.html`. Treat any issue as blocking unless the user explicitly accepts the specific risk. Do not say a failed check "does not affect publishing" on your own.
11. Review `dist/article.preview.html` for reading order, missing fields, overlong cards, and mobile layout. Fix `article.json` and rerun the renderer.
12. Tell the user to import by opening `article.preview.html` in a browser, selecting the rendered page, and copying the rendered rich text into WeChat. Do not tell them to paste the raw `article.wechat.html` source into the WeChat editor.
13. Deliver `article.wechat.html` as the primary HTML artifact. Include the suggested WeChat title, digest, and cover suggestion in the final response. Only create a WeChat platform draft when credentials and API access are explicitly available.

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

## Context Budget

Do not rely on the model remembering whole PDFs or long transcripts.

- Always extract full PDFs to disk, then read selectively.
- If a single extracted file is longer than about 12,000 Chinese characters or 8,000 English words, use `prepare_article_notes.py` and search/reopen targeted sections instead of reading the whole file in one context pass.
- Use `paper_notes.json` as a table of contents, not as a replacement for source evidence.
- Use `transcript_notes.json` to locate stable discussion themes and noisy ASR areas.
- Write intermediate conclusions into `article_data.py` or notes files so shorter-context models can continue without re-reading everything.

## Output Policy

Default to these deliverables:

- `article.json`: structured, editable source of truth.
- `article.wechat.html`: WeChat-compatible HTML for copy/import into WeChat, doocs/md, 135, Xiumi, or a custom uploader.
- `article.preview.html`: browser preview wrapper for checking layout before import.
- `article_notes/`: budgeted paper/transcript notes and an intake decision template when materials are long or noisy.

Do not create `source_trace.md` by default. Create it only when the user asks for traceability, audit notes, reviewer checking, citation mapping, or a rigorous verification package. Keep `source` fields in `article.json` for private agent verification.

Prefer "create draft, then human review" over direct publishing. Do not directly publish through the WeChat API unless the user explicitly asks for automated publication and provides/approves the required credentials.

## Content Rules

- Keep the article suitable for mobile reading: short paragraphs, clear section headings, readable line spacing, and restrained emphasis.
- Preserve the expected reading-sharing meeting flow when materials support it: lead summary, English exchange, literature sharing, current affairs or policy discussion when present, free discussion and meeting summary.
- Omit any section that lacks source material. Do not force a current-affairs/policy section into older meetings that did not include one.
- Use `custom_sections` for occasional inserts within the meeting flow, such as a student award, project milestone, paper acceptance, announcement, or photo note. Do not turn the article into a separate news article unless the user asks.
- English speech cards should show one speaker per card. If the user provides each person's English speech draft, publish the full original text by default; do not summarize or polish it unless explicitly asked.
- Literature sections must distinguish paper facts from meeting comments. Expand paper introductions into background, research question, methods/data, core findings, and discussion value when the source supports it. If paper metadata is incomplete, mark it for confirmation instead of guessing.
- Treat audio transcription files as noisy evidence. Use them to recover stable discussion meaning, but cross-check names, dates, paper titles, awards, technical terms, and strong claims against PPT/PDF/filenames. Silently repair only obvious ASR errors; ask one confirmation question when ambiguity changes a public fact.
- Policy/current-affairs sections should summarize viewpoints neutrally and attribute them to roles or speakers when available.
- Meeting summaries should be concise and avoid unsupported claims about consensus.
- Keep `source` fields for traceability only. Do not display filenames, local paths, or transcript names in the WeChat article body.
- Use provided meeting photos, PPT screenshots, certificates, paper figures, or generated cover assets when available and relevant. Do not invent data-bearing academic figures.
- If the active model cannot inspect images, use text extraction and filenames to identify image candidates, then list placement suggestions instead of blocking the draft.
- If no usable images are provided, include image placement suggestions in the final response instead of fabricating figures.
- Keep the default `zhengeryanzi` theme restrained: no top brand card, static section marks, subtle dividers, and a closing signature with host/editor credits.
- Use `template: "classic"` as the default concise layout. Supported reading-sharing styles are `classic`, `notebook`, `journal`, `campus`, `minimal`, `magazine`, `warm-note`, `briefing`, and `fieldnote`. Pair with one palette from `classic`, `forest`, `blueprint`, `warm`, `ink`, `sunrise`, or `mono`.

## Reusable Components

The renderer provides reusable components that templates style differently:

- `lead_summary`: the opening guide card.
- `section_heading`: numbered meeting section headings.
- `english_speech_cards`: horizontal English speech cards.
- `paper_digest`: literature paper blocks.
- `teacher_comment` and `student_discussion`: quote blocks.
- `honor_insert`, `announcement_insert`, and `milestone_insert`: optional meeting-flow inserts.
- `image_caption`: supplied image with caption.
- `closing_signature`: account and host/editor credits.

Keep components conservative and WeChat-friendly. Static SVG marks, thin dividers, number chips, soft backgrounds, and small badges are safe. Use animation only with `experimental_motion: true`; every animated element must remain readable if animation is stripped by WeChat.

## Resource Guide

- Read `references/input-contract.md` when creating or validating `article.json`.
- Read `references/editorial-style.md` before drafting or revising article content.
- Read `references/material-extraction.md` when the task includes `.docx`, `.pptx`, `.pdf`, `.txt`, or `.md` materials.
- Read `references/wechat-formatting.md` when adjusting HTML, SVG, card layout, or editor compatibility.
- Read `references/wechat-api.md` only when the task involves creating a WeChat draft or uploading images/materials.
- Use `scripts/extract_materials.py` to create Markdown text extracts and `materials_manifest.json`.
- Use `scripts/prepare_article_notes.py` after extraction to create `paper_notes.json`, `transcript_notes.json`, and `intake_decision.template.json`.
- Use `scripts/draft_article_from_materials.py` only to create `article.scaffold.json` as an inventory/scaffold aid. Never treat scaffold output as the final article.
- Use `scripts/create_article_json.py` to create a valid starter JSON file.
- Use `scripts/write_article_json.py` to generate `article.json` from a Python `ARTICLE` dict instead of hand-writing large raw JSON.
- Use `scripts/render_wechat_article.py` for deterministic HTML output.
- Use `scripts/check_article_json.py` before delivery to catch source filename leaks, missing literature structure, suspiciously short English speeches, duplicate English speeches, empty publication metadata, and incomplete optional inserts.
- Use `assets/article-template.html` as the HTML template if the renderer needs visual changes.

## Cross-Agent Portability

This skill is intentionally file-based and tool-light. Any capable agent can reuse it by reading `SKILL.md`, generating `article.json`, and running the renderer with Python 3. The WeChat API step is optional and should be isolated from the writing/rendering pipeline so the skill remains usable in Claude Code, Codex, local scripts, or a future web app.
