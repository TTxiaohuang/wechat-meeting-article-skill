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

## English Speech Cards

Default to horizontal scrolling HTML cards:

- Container: `overflow-x:auto; white-space:nowrap;`
- Card: `display:inline-block; vertical-align:top; width:82%; max-width:320px; white-space:normal;`
- One speaker per card.
- Keep the full text available, but summarize overly long speeches if the article becomes hard to read.

## SVG Guidance

Use SVG only when the user specifically wants a WeChat SVG interaction style and accepts extra testing. Keep SVG self-contained, avoid scripts, external assets, filters, and fragile IDs. Provide a non-SVG HTML card fallback.

## Visual Tone

Use a restrained academic style:

- Main text: near-black, not pure black.
- Accent color: one muted blue or green plus light neutral backgrounds.
- Section headers: clear but compact.
- Quotes/comments: left border or subtle background, not oversized decorative cards.
