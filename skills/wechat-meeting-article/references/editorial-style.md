# Editorial Style

Use this reference before drafting or revising the article content.

## Editorial Priorities

1. Preserve factual accuracy and speaker attribution.
2. Make the article read like a polished WeChat post, not an extraction report.
3. Keep source filenames and local paths out of the visible article.
4. Use flexible sections: omit unsupported meeting sections instead of forcing a template.
5. Keep `source_trace.md` detailed enough for verification.

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

## Visual Materials

Use images only when they help the reader understand the meeting:

- meeting photos
- PPT title slide or key slide screenshots
- paper framework/机制图/核心结果图 when supplied
- a clean cover image generated or provided by the user

Do not invent data charts, regression tables, or paper figures. If no suitable image exists, add image suggestions in the final response rather than fabricating visuals.

Useful image placement suggestions:

- cover: meeting title slide, meeting photo, or a clean generated cover
- English exchange: optional topic card
- literature sharing: supplied paper framework figure, PPT key slide, or method flow diagram
- discussion summary: meeting photo or reading list image

## WeChat Body Style

- Use a short lead summary under the title.
- Prefer compact section headings and clear paragraph rhythm.
- Use quote blocks for meeting comments. Avoid putting every literature subfield into a colored card; ordinary text with small headings is usually easier to read.
- Avoid visible technical labels such as `source`, local filenames, JSON keys, extraction notes, or script names.
- Keep wording warm and academic: accessible enough for public reading, but not marketing-like.
