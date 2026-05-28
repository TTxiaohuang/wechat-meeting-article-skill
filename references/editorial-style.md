# Editorial Style

Use this reference before drafting or revising the article content.

## Editorial Priorities

1. Preserve factual accuracy and speaker attribution.
2. Make the article read like a polished WeChat post, not an extraction report.
3. Keep source filenames and local paths out of the visible article.
4. Use flexible sections: omit unsupported meeting sections instead of forcing a template.
5. Keep `source` fields in `article.json` for private verification. Create `source_trace.md` only when the user asks for traceability, audit notes, or citation mapping.
6. Treat deterministic scaffold files and `article_notes` as inventory aids only. The final article must be synthesized by reading the extracted materials.
7. Treat a failed `check_article_json.py` result as a stop signal. Fix the issue or ask the user to accept the exact risk; do not waive it silently.

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

- If `_meta.intake_gate` is missing or incomplete, stop before rendering and record the missing decisions.
- If the English draft contains many speakers but `article.json` only contains one or two, revisit the extraction and do not publish.
- If a transcript is long but the final free discussion contains only one generic sentence, revisit the transcript.
- If paper extracts are thousands of characters but each paper section contains only a few short lines, expand the literature notes.
- If a PDF manifest shows fewer pages extracted than total pages, do not assume the whole paper was read. Increase extraction or state the limitation.
- If a PDF manifest shows zero text pages, treat the PDF as unreadable without OCR or user-provided text.
- If `article.json` contains `_meta.scaffold_generated`, rewrite it into a final article JSON before rendering.
- If extracted materials contain clear honor news, announcements, project milestones, paper acceptances, or certificates, include them as `custom_sections` unless they are ambiguous or sensitive.

## Noisy Transcripts

Audio transcription files often contain recognition errors. Do not polish ASR noise into confident facts.

- Prefer paraphrased discussion summaries over long direct transcript quotes.
- Cross-check participant names, paper titles, award names, methods, dates, and institutions against non-ASR materials.
- Attribute remarks as "老师", "同学讨论", or "会议讨论" when speaker identity is uncertain.
- Keep exact names and award details only when supported by multiple sources or clearly stated in a prepared document.
- Ask for confirmation when a noisy transcript affects a public-facing fact or privacy-sensitive detail.

## Optional Inserts

Use inserts sparingly. The article remains a reading-sharing meeting article; inserts should feel like brief moments inside the meeting flow.

- `honor_news`: student award, competition result, project approval, paper acceptance, or similar good news. Prefer placement after the lead or before literature sharing when it is celebratory.
- `announcement`: meeting notice, upcoming activity, submission reminder, or administrative update. Prefer placement before free discussion or before closing.
- `milestone`: group project progress, publication milestone, data release, or event completion. Place near the section it relates to.
- `note`: short contextual aside that does not deserve a full regular section.

Auto-include inserts when filenames or extracted text clearly indicate publication intent, such as "喜讯", "祝贺", "获奖", "立项", "入选", "录用", "证书", or "通知". Ask one confirmation question when names, award levels, certificate images, privacy, or public-release permission are unclear.

## Visual Materials

Use images only when they help the reader understand the meeting:

- meeting photos
- PPT title slide or key slide screenshots
- paper framework/机制图/核心结果图 when supplied
- a clean cover image generated or provided by the user

Do not invent data charts, regression tables, or paper figures. If no suitable image exists, add image suggestions in the final response rather than fabricating visuals.

When the material folder contains images whose purpose is not obvious (e.g., `.jpg`/`.png` files with names that could be anything), list the filenames and ask the user:
1. What are these images? (meeting photos, screenshots, figures, certificates, etc.)
2. Where should they be placed in the article? (cover, English cards, literature section, closing, etc.)

Never assume what images are based on filenames alone. Never silently skip images because their purpose is unclear.

## Brand Theme

Use `"theme": "zhengeryanzi"` for the default account style. The renderer adds small inline SVG section marks and a closing signature. Do not add a large top brand card by default. Keep decorations static because WeChat editor compatibility is more predictable than animated SVG interactions.

Template choices:

- `classic`: default concise intro layout; closest to the current stable style.
- `notebook`: reading-note style with soft section bands and a left accent rule.
- `campus`: brighter campus account style while keeping the same meeting structure.
- `magazine`: stronger opening rhythm and editorial section treatment.
- `briefing`: more report-like, with stronger section dividers and number chips.

Legacy names (`journal`, `minimal`, `warm-note`, `fieldnote`) are accepted via aliases and map to the closest remaining template.

Palette choices:

- `classic`: muted blue plus warm note color.
- `forest`: academic green and soft cream.
- `blueprint`: blue report tone.
- `warm`: restrained brown/green reading-note tone.
- `ink`: gray-black academic tone.
- `sunrise`: warm coral and green, suitable for friendlier campus posts.
- `mono`: nearly monochrome minimal tone.
- `sakura`: cherry blossom pink and warm white.
- `ocean`: deep sea blue and light cyan.

SVG is used by the renderer for built-in decorative elements (section marks, quote marks, avatars, cover card). No user action needed. For custom SVG animation, only use when explicitly requested and tested in WeChat preview.

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
- In the final response, include the suggested WeChat title, digest, and cover suggestion because the WeChat editor title and digest fields must be filled manually after body paste.
