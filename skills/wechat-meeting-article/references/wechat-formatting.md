# WeChat Formatting Notes

WeChat Official Account articles are mobile-first and the editor may filter HTML and CSS. Prefer conservative inline styles and avoid JavaScript.

## Recommended Delivery

1. Primary: `article.wechat.html` copied into WeChat, doocs/md, 135 editor, Xiumi, or a custom importer.
2. Safer automation: create a WeChat draft through the API, then preview and manually publish.
3. Avoid direct automatic publishing unless the user explicitly asks and accepts the operational risk.

## Import Into WeChat

Do not paste the raw source code from `article.wechat.html` into the WeChat editor. That may show visible HTML code.

Recommended manual import:

1. Open `article.preview.html` in a browser.
2. Select the rendered article content in the browser.
3. Copy the rendered rich text.
4. Paste into the WeChat Official Account editor.
5. Preview on mobile before publishing.

Alternative workflow:

- Import or paste `article.wechat.html` into doocs/md, 135 editor, Xiumi, or another WeChat editor that supports HTML source import.
- Recheck horizontal cards and comments after import because editors may sanitize styles.

## Layout Rules

- Use inline styles only.
- Use simple block elements: `section`, `p`, `span`, `strong`, `em`, `blockquote`, `img`.
- Avoid external CSS, JavaScript, iframes, complex positioning, and remote font dependencies.
- Keep paragraphs short and use line-height around `1.75`.
- Do not rely on desktop width. Test around 360-430 px wide.
- Do not show extraction metadata, source filenames, or local file paths in the visible body.
- Use a lead summary card, numbered section headings, paper information blocks, and quote blocks to avoid a raw report-like layout.

## English Speech Cards

Default to horizontal scrolling HTML cards:

- Container: `overflow-x:auto; white-space:nowrap;`
- Card: `display:inline-block; vertical-align:top; width:86%; max-width:340px; white-space:normal;`
- One speaker per card.
- If source speech drafts are provided, keep the full original English text in the card body.
- Add a short "左右滑动查看完整英文发言" hint before the cards.

## Literature Blocks

Prefer a paper card sequence:

- paper title and metadata
- optional supplied image or PPT/paper figure
- research background
- research question
- methods and data
- core findings list
- discussion value
- meeting comments as quote blocks

This makes the literature section feel like a public-facing academic reading note instead of a short meeting log.

## SVG Guidance

Use SVG only when the user specifically wants a WeChat SVG interaction style and accepts extra testing. Keep SVG self-contained, avoid scripts, external assets, filters, and fragile IDs. Provide a non-SVG HTML card fallback.

## Visual Tone

Use a restrained academic style:

- Main text: near-black, not pure black.
- Accent color: one muted blue or green plus light neutral backgrounds.
- Section headers: clear but compact.
- Quotes/comments: left border or subtle background, not oversized decorative cards.
- For the `zhengeryanzi` theme, keep inline SVG decorations static and restrained: section marks and closing signature. Avoid a large top brand card. Avoid animation unless explicitly requested and preview-tested.
- Supported layouts are `classic`, `notebook`, `briefing`, and `fieldnote`; supported palettes are `classic`, `forest`, `blueprint`, and `warm`. These are inline-style variants intended to survive WeChat editor import.
