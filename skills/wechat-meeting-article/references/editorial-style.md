# Editorial Style

Use this reference before drafting or revising the article content.

## Editorial Priorities

1. Preserve factual accuracy and speaker attribution.
2. Make the article read like a polished WeChat post, not an extraction report.
3. Keep source filenames and local paths out of the visible article.
4. Use flexible sections: omit unsupported meeting sections instead of forcing a template.
5. Keep `source_trace.md` detailed enough for verification.
6. Treat deterministic scaffold files as inventory aids only. The final article must be synthesized by reading the extracted materials.

## English Exchange

- If individual English speech drafts are provided, use the original English text as the card body.
- Do not summarize, translate, correct, or heavily polish the English speech unless the user asks.
- Keep one speaker per horizontal card.
- A short Chinese intro before the cards is acceptable.
- Keep source filenames only in `article.json.source` or `source_trace.md`; do not render them in the article.

## Literature Sharing

For each paper, write a substantive but concise academic introduction. Prefer this structure:

- `background`: why the paper matters and what research context it enters
- `research_question`: the central question or hypothesis
- `methods_data`: data, model, identification strategy, sample, or analytical method
- `findings`: 2-4 concrete findings
- `discussion_value`: why the paper is useful for the group discussion or future research
- `comments`: student/teacher views from the meeting

Avoid vague lines such as "this paper has important reference value" unless followed by specifics. Do not overclaim causal conclusions when the paper design does not support them.

## Completeness Checks

Before rendering, compare the final article against the extracted materials:

- If the English draft contains many speakers but `article.json` only contains one or two, revisit the extraction and do not publish.
- If a transcript is long but the final free discussion contains only one generic sentence, revisit the transcript.
- If paper extracts are thousands of characters but each paper section contains only a few short lines, expand the literature notes.
- If `article.json` contains `_meta.scaffold_generated`, rewrite it into a final article JSON before rendering.

## Visual Materials

Use images only when they help the reader understand the meeting:

- meeting photos
- PPT title slide or key slide screenshots
- paper framework/机制图/核心结果图 when supplied
- a clean cover image generated or provided by the user

Do not invent data charts, regression tables, or paper figures. If no suitable image exists, add image suggestions in the final response rather than fabricating visuals.

## Brand Theme

Use `"theme": "zhengeryanzi"` for the default account style. The renderer adds small inline SVG section marks and a closing signature. Do not add a large top brand card by default. Keep decorations static because WeChat editor compatibility is more predictable than animated SVG interactions.

Only use SVG animation or interaction when the user explicitly asks for an experimental version and agrees to test it in WeChat preview.

For the closing signature, prefer `meta.host` and `meta.editor`, rendered as "主持：..." and "推文编辑：...". Do not use a generic slogan when credit metadata is available.

Useful image placement suggestions:

- cover: meeting title slide, meeting photo, or a clean generated cover
- English exchange: optional topic card
- literature sharing: supplied paper framework figure, PPT key slide, or method flow diagram
- discussion summary: meeting photo or reading list image

## WeChat Body Style

- Use a short lead summary under the title.
- Prefer compact section headings and clear paragraph rhythm.
- Use quote blocks for meeting comments. Avoid putting every literature subfield into a colored card; ordinary text with small headings is usually easier to read.
- Use decoration sparingly: thin dividers, small SVG marks, subtle quote backgrounds, and occasional image separators. Avoid Xiumi-style dense frames, sticker-like ornaments, flashing effects, and decorative clutter.
- Avoid visible technical labels such as `source`, local filenames, JSON keys, extraction notes, or script names.
- Keep wording warm and academic: accessible enough for public reading, but not marketing-like.
