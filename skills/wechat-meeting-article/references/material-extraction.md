# Material Extraction

Use this reference when the input folder contains `.docx`, `.pptx`, `.pdf`, `.txt`, or `.md` files.

## Recommended Command

```bash
python scripts/extract_materials.py path/to/material-folder --out extracted_materials
```

The script writes:

- one Markdown text file per supported source file
- `materials_manifest.json` with source paths, output paths, status, extraction metadata, and errors

Output filenames are sanitized for agent and shell compatibility. Quote-like characters, path separators, and other fragile punctuation are replaced with underscores. The original source path is preserved in `materials_manifest.json`.

For PDFs, the default is full-document extraction. This keeps the evidence complete for literature sharing. To limit very long files, pass a positive page count:

```bash
python scripts/extract_materials.py path/to/material-folder --out extracted_materials --pdf-pages 10
```

To be explicit about full PDF extraction:

```bash
python scripts/extract_materials.py path/to/material-folder --out extracted_materials --pdf-pages all
```

For each PDF, the manifest records `pdf_pages_total`, `pdf_pages_requested`, `pdf_pages_extracted`, and `pdf_text_pages`. If `pdf_text_pages` is 0, the PDF may be scanned or image-based and should not be treated as fully readable.

After extraction, create budgeted intermediate notes:

```bash
python scripts/prepare_article_notes.py extracted_materials --out article_notes
```

The script writes:

- `paper_notes.json`: paper-level metadata and short excerpts around abstract, methods, results, robustness/mechanism, and conclusion cues.
- `transcript_notes.json`: noisy transcript cues for discussion topics, teacher comments, student questions, and uncertain ASR areas.
- `intake_decision.template.json`: the required intake gate structure to copy into `_meta.intake_gate`.

Use these files as an index. They do not replace source reading; reopen extracted Markdown around relevant headings before making precise claims.

## Dependencies

Install optional parsers only when needed:

```bash
python -m pip install python-docx python-pptx pdfplumber pypdf
```

If the agent runs in a locked environment, ask before installing dependencies. If dependencies cannot be installed, tell the user which formats could not be extracted and continue with available text files.

## Windows Encoding

For Chinese output on Windows, prefer UTF-8:

```powershell
$env:PYTHONIOENCODING="utf-8"
```

Python scripts in this skill also call `sys.stdout.reconfigure(encoding="utf-8")` when supported.

When reading extracted Chinese Markdown in an agent or shell, prefer Python with explicit UTF-8 encoding over plain `cat`/`type` if the terminal displays mojibake:

```bash
python -c "from pathlib import Path; print(Path('extracted_materials/file.md').read_text(encoding='utf-8'))"
```

## Extraction Rules

- Do not use raw file reads for `.docx`, `.pptx`, or `.pdf`; these are binary formats.
- For `.docx`, preserve paragraph order and table rows.
- For `.pptx`, preserve slide order and slide numbers.
- For `.pdf`, default to full extraction so the article can cover title, authors, abstract, methods, results, robustness checks, discussion, and conclusion. Full extraction does not mean the agent must paste the whole PDF into context; read selectively using headings and searches for terms such as 摘要, 引言, 研究设计, 数据, 方法, 结果, 机制, 稳健性, 讨论, 结论, limitations, and conclusion.
- If an extracted Markdown file is long, read `article_notes` first, then use search or targeted reads. Do not read every character into the model context unless the file is short enough to fit comfortably.
- Save extraction errors in the manifest instead of silently skipping files.
- Treat extracted text as raw evidence. The final article still needs source-grounded synthesis and human-readable rewriting.

## Noisy Transcript Handling

Treat audio transcription files as noisy evidence, not authoritative quotations.

- Use transcripts to recover discussion topics, teacher comments, student questions, and action items.
- Cross-check names, paper titles, dates, methods, institutions, awards, and technical terms against PPT files, PDFs, filenames, and user-provided notes.
- Silently repair obvious ASR errors only when the correction is strongly supported by other materials or standard academic terminology.
- Do not quote long transcript passages verbatim unless the wording is clear and useful.
- If a transcript is messy, summarize the stable meaning and avoid over-precise attribution.
- Ask one concise confirmation question when an ASR ambiguity changes a public fact, such as who won an award, the exact award name, a meeting date, or a sensitive personal detail.
- When the model cannot resolve transcript noise, mark the item as uncertain in draft notes or omit it from the public article rather than inventing a polished claim.
