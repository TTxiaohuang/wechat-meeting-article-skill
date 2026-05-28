---
name: wechat-meeting-article
description: Use when preparing WeChat Official Account article drafts from research group meeting materials such as transcripts, English speeches, literature PDFs, PPT files, policy notes, and meeting summaries. Triggers on keywords like 组会推文, 公众号文章, 读书分享会, meeting article, weekly report.
---

# WeChat Meeting Article

## When to Use

- 组会/读书分享会结束后需要制作公众号推文
- 素材文件夹中有录音转录稿、PPT、文献 PDF、英语发言稿、会议照片等
- 需要把会议内容整理成结构化的微信公众号文章

## When NOT to Use

- 只有一份简单会议纪要，没有录音/PPT/PDF 等原始素材
- 需要直接自动发布到微信公众号（本技能只生成草稿，不自动发布）
- 不需要公众号格式，只需要普通 Markdown 笔记

## Overview

Produce a publication-ready WeChat Official Account draft from weekly reading-sharing meeting materials. Separate content reasoning from rendering: generate a structured `article.json` first, then use the bundled renderer to create WeChat-compatible HTML and preview HTML.

## Quick Reference

| 步骤 | 命令 | 说明 |
|------|------|------|
| 1. 提取素材 | `python scripts/extract_materials.py 素材文件夹 --out extracted_materials` | 递归扫描所有子文件夹 |
| 2. 生成笔记 | `python scripts/prepare_article_notes.py extracted_materials --out article_notes` | 长材料时推荐 |
| 3. 写 article.json | 由 Agent 或手动完成 | 结构化数据源 |
| 4. 渲染 HTML | `python scripts/render_wechat_article.py article.json --out dist` | 生成微信兼容 HTML |
| 4b. 嵌入图片 | `python scripts/render_wechat_article.py article.json --out dist --embed-images` | 本地图片嵌入为 base64 |
| 5. 质量检查 | `python scripts/check_article_json.py article.json --html dist/article.wechat.html` | 必须通过 |

## Intake Gate

Present choices to the user instead of silently applying defaults. **Ask the user directly for information; do not search the filesystem to guess folder locations.**

**UI constraint**: Claude Code 的 `AskUserQuestion` 工具每个问题最多显示 4 个选项按钮。当选项超过 4 个时，**必须**把常用选项放在按钮里，把**全部选项清单**写在按钮的 `description` 中，让用户通过 "Other" 输入其余选项。

**模板和配色的选项展示规则**（选项多于按钮上限时的强制格式）：

**模板（5个选项，展示3个按钮）** — 使用 `AskUserQuestion`，结构如下：
- question: "选择文章模板"
- options（4个，其中第4个是汇总入口）:
  1. `{label: "经典简洁", description: "classic — 默认简洁风格"}`
  2. `{label: "笔记风格", description: "notebook — 左侧色条+柔和背景"}`
  3. `{label: "校园清新", description: "campus — 明亮校园风格"}`
  4. `{label: "更多模板", description: "可选: magazine(编辑排版), briefing(报告风格)。输入模板名称即可"}`
- header: "模板"

**配色（9个选项，展示3个按钮）** — 使用 `AskUserQuestion`，结构如下：
- question: "选择配色方案"
- options（4个，其中第4个是汇总入口）:
  1. `{label: "森林绿", description: "forest — 学术绿+柔和米色"}`
  2. `{label: "蓝图蓝", description: "blueprint — 蓝色报告色调"}`
  3. `{label: "樱花粉", description: "sakura — 樱花粉+暖白"}`
  4. `{label: "更多配色", description: "可选: classic(经典蓝), warm(暖棕绿), ink(灰黑学术), sunrise(珊瑚暖绿), mono(近单色), ocean(深海蓝)。输入配色名称即可"}`
- header: "配色"

**关键：第4个选项的 description 必须列出所有剩余选项的名称和简短说明，这样用户就知道可以通过 "Other" 输入哪些值。不要只写"更多"两个字。**

### Round 1 — before inspecting the folder:

Split into separate questions (one per field), do not combine into a single block:

1. **Material folder path** — ask directly
2. **Template** — 按上述"模板"格式提问（3个常用按钮 + "更多模板"汇总入口）
3. **Palette** — 按上述"配色"格式提问（3个常用按钮 + "更多配色"汇总入口）
4. **Editor** — ask for name, or confirm omission (2 options: provide name / 留空)

### Round 2 — after inventory:

1. **Date/Host**: infer from materials, confirm if ambiguous
2. **Images**: list every image file, ask user what each is and where to place it
3. **Cover style** — 3 options:
   - `无封面` — no cover, plain title text
   - `PPT标题页` — use PPT first slide as cover image
   - `自选图片` — user provides an image path or URL
4. **Optional inserts**: honor news, announcements, milestones — confirm inclusion

Do not silently skip any decision. If the user does not respond to a field, confirm the default.

## Workflow

1. **Round 1 intake** (see Intake Gate above).
2. **Inventory** the material folder: transcript, English speeches, paper PDFs, PPT files, images, certificates, honor-news documents.
3. **Round 2 intake** (see Intake Gate above).
4. **Extract** source text with `scripts/extract_materials.py`. All file types (`.docx`, `.doc`, `.pptx`, `.pdf`, `.txt`, `.md`, `.rtf`) are fully extracted by default. `.doc` files are auto-converted to `.docx` via Microsoft Word (pywin32) or LibreOffice; if neither is available, the script reports an error. `.rtf` files are extracted as plain text. Subdirectories are scanned recursively; use `--no-recursive` to limit to top-level files only. Do not rely on raw file reads for binary formats. Read selectively from the extracted Markdown for long files.
5. **Prepare notes**:
   ```bash
   python scripts/prepare_article_notes.py extracted_materials --out article_notes
   ```
   Use `paper_notes.json` as a table of contents, then reopen relevant excerpts. For noisy transcripts, `transcript_notes.json` may be sparse — read the full extracted transcript directly in that case.
6. **Scan** for optional inserts (honor news, announcements, milestones). Auto-include when clear; ask when ambiguous.
7. **Read** `references/editorial-style.md` before drafting.
8. **Write `article.json`** directly with the file-writing tool, then immediately run the renderer to validate. To avoid JSON errors with Chinese text, replace Chinese quotation marks `””` inside JSON strings with their Unicode escapes `“”`, or rephrase to avoid nested quotes entirely.
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
- **Transcripts**: treat as noisy evidence. Cross-check names, dates, paper titles, and technical terms against PPT/PDF/filenames. See `references/material-extraction.md` for ASR speaker identification strategies and date inference priority.
- **Images**: never assume what images are from filenames alone. Ask the user what each image is and where to place it. Use `--embed-images` for reliable browser preview and WeChat paste.
- `source` fields are for traceability only; never display filenames or paths in the article body.
- `custom_sections` for occasional inserts (honor news, announcements, milestones). Do not turn the article into a separate news piece.
- Default theme `zhengeryanzi`（公众号名称：郑而研资）。**品牌主题是默认设置，无需询问用户是否使用。** See `references/editorial-style.md` for template and palette options.

## Dependency Setup

Renderer needs only Python 3 stdlib. Material extraction needs optional parsers:

```bash
python -m pip install python-docx python-pptx pdfplumber pypdf
```

For `.doc` files (old Word format), auto-conversion requires one of:
- **Microsoft Word + pywin32**: `python -m pip install pywin32`（Windows，需已安装 Word）
- **LibreOffice**: add `libreoffice` / `soffice` to PATH（跨平台）

On Windows, set `PYTHONIOENCODING=utf-8` if Chinese text becomes garbled.

## Context Budget

- Extract full PDFs to disk, then read selectively.
- If a single extracted file exceeds ~12,000 Chinese chars or ~8,000 English words, use notes as an index and reopen targeted sections.
- Write intermediate conclusions to files so shorter-context models can continue without re-reading.

## Common Mistakes

| 错误 | 正确做法 |
|------|----------|
| 直接把 `article.wechat.html` 源码粘贴到微信编辑器 | 打开 `article.preview.html`，选中渲染后的正文，复制富文本粘贴 |
| 忘记安装依赖就跑 `extract_materials.py` | 先 `pip install python-docx python-pptx pdfplumber pypdf` |
| 把 scaffold JSON（`article.scaffold.json`）直接交付 | 必须先展开为完整的 `article.json` |
| 不检查图片就直接渲染 | 清单中每个图片都要问用户是什么、放哪里 |
| 跳过 `check_article_json.py` 质量检查 | 每次渲染后必须跑质量检查，有问题就修 |
| JSON 字符串里直接用中文引号 `""` | 替换为 Unicode 转义 `“”` 或改用 `《》` |
| 在正文里出现文件名或本地路径 | `source` 字段仅用于溯源，不显示在正文中 |
| 假设图片文件名能说明图片内容 | 永远问用户，不要猜测 |

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
