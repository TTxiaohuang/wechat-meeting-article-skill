# Material Extraction

Use this reference when the input folder contains `.docx`, `.pptx`, `.pdf`, `.txt`, or `.md` files.

## Recommended Command

```bash
python scripts/extract_materials.py path/to/material-folder --out extracted_materials
```

The script writes:

- one Markdown text file per supported source file
- `materials_manifest.json` with source paths, output paths, status, and errors

Output filenames are sanitized for agent and shell compatibility. Quote-like characters, path separators, and other fragile punctuation are replaced with underscores. The original source path is preserved in `materials_manifest.json`.

For long PDFs, the default is the first 5 pages:

```bash
python scripts/extract_materials.py path/to/material-folder --out extracted_materials --pdf-pages 10
```

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
- For `.pdf`, extract enough pages to identify title, authors, abstract, methods, results, and discussion points. Increase `--pdf-pages` when needed.
- Save extraction errors in the manifest instead of silently skipping files.
- Treat extracted text as raw evidence. The final article still needs source-grounded synthesis and human-readable rewriting.
