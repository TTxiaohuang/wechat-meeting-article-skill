# WeChat API Notes

Use this reference only when the user asks to create a WeChat Official Account draft or integrate publication.

## Recommended Flow

1. Obtain and cache `access_token` using the official account `appid` and `secret`.
2. Upload cover images as permanent materials to get `thumb_media_id`.
3. Upload body images with the article image upload endpoint or permanent material endpoint as required by the chosen publishing path.
4. Create a draft with the draft-box API.
5. Send preview or open the platform draft for human review.
6. Publish only after explicit approval.

## Draft Payload Fields

Typical article fields include:

- `title`
- `author`
- `digest`
- `content`
- `content_source_url`
- `thumb_media_id`
- `need_open_comment`
- `only_fans_can_comment`

## Guardrails

- Never hardcode `appid`, `secret`, tokens, cookies, or account credentials into the skill.
- Keep API code separate from the renderer.
- Expect IP allowlists, certification status, rate limits, token expiry, and account permissions to fail in real deployments.
- Save the draft request payload for debugging, but redact secrets in logs.
- Prefer a dry-run mode that writes `wechat_draft_payload.json`.
