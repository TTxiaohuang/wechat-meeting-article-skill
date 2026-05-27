# WeChat Meeting Article Skill

This repository hosts a portable AI Agent skill for turning weekly research group meeting materials into WeChat Official Account article drafts.

The skill helps an agent process transcripts, English speeches, literature sharing materials, PPT notes, policy discussion notes, and meeting summaries, then generate:

- `article.json`: structured article source
- `article.wechat.html`: WeChat-friendly HTML
- `article.preview.html`: local preview HTML
- `source_trace.md`: source-to-claim notes

## Repository Layout

```text
skills/
  wechat-meeting-article/
    SKILL.md
    agents/openai.yaml
    references/
    scripts/
    assets/
```

## Install In Codex

If Codex has the skill installer available, install from GitHub with:

```text
Use $skill-installer to install OWNER/REPO path skills/wechat-meeting-article
```

Replace `OWNER/REPO` with the final GitHub repository owner and name.

Manual install on Windows:

```powershell
git clone https://github.com/OWNER/REPO.git
Copy-Item -Recurse -LiteralPath .\REPO\skills\wechat-meeting-article -Destination "$env:USERPROFILE\.codex\skills"
```

Restart Codex after installation.

## Use In Claude Code Or Other Agents

Clone the repository and tell the agent:

```text
Read skills/wechat-meeting-article/SKILL.md and use it to generate a WeChat-ready weekly meeting article from my materials.
```

The workflow is intentionally file-based so it does not depend on a single agent runtime.

## Render HTML

After an agent creates `article.json`, run:

```powershell
python skills\wechat-meeting-article\scripts\render_wechat_article.py article.json --out dist
```

Outputs:

```text
dist/article.wechat.html
dist/article.preview.html
```

## Notes

- Do not commit WeChat credentials, app secrets, tokens, cookies, meeting recordings, or unpublished private meeting materials.
- Default to creating WeChat-ready HTML or a draft-box payload. Direct automatic publishing should require explicit human approval.
