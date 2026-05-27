# Input Contract

Create `article.json` with UTF-8 encoding. Required top-level keys are `meta`, `sections`, and optionally `assets`.

Prefer creating the starter file with:

```bash
python scripts/create_article_json.py --out article.json
```

Then edit values while preserving JSON syntax.

## Minimal Example

```json
{
  "meta": {
    "title": "第 X 周组会纪要",
    "date": "2026-05-27",
    "group": "课题组名称",
    "host": "主持人",
    "cover_image": "",
    "summary": "本次组会围绕英语交流、文献分享、时政交流和自由讨论展开。"
  },
  "sections": {
    "english_exchange": {
      "title": "英语交流",
      "topic": "本周话题",
      "intro": "简要说明交流主题。",
      "speeches": [
        {
          "speaker": "张三",
          "role": "学生",
          "text": "English speech text here.",
          "source": "english_speeches/zhangsan.docx"
        }
      ]
    },
    "literature_sharing": {
      "title": "文献分享",
      "papers": [
        {
          "title": "Paper title",
          "authors": "Author A et al.",
          "venue": "Journal, Year",
          "doi": "",
          "presenter": "李四",
          "summary": "文献核心问题、方法和主要发现。",
          "comments": [
            {
              "speaker": "王老师",
              "text": "观点评论。",
              "source": "transcript.docx"
            }
          ]
        }
      ]
    },
    "policy_discussion": {
      "title": "时政交流",
      "topic": "政策或时事主题",
      "summary": "背景和讨论焦点。",
      "viewpoints": [
        {
          "speaker": "参会者",
          "text": "观点整理。",
          "source": "transcript.docx"
        }
      ]
    },
    "free_discussion": {
      "title": "自由讨论与会议总结",
      "items": [
        {
          "speaker": "主持人",
          "text": "讨论事项或总结。",
          "source": "transcript.docx"
        }
      ],
      "closing": "会议总结。"
    }
  },
  "assets": {
    "images": []
  }
}
```

## Rules

- Keep `text`, `summary`, `intro`, and `closing` as plain text. The renderer escapes HTML.
- Use arrays even when there is only one paper, comment, speech, or viewpoint.
- Put incomplete or uncertain fields as empty strings and add a note in `source_trace.md`.
- If source materials conflict, preserve the conflict in notes and ask for confirmation instead of silently merging.
- Keep source paths relative to the input material folder when possible.
- JSON requires standard double quotes around keys and string values. Do not paste unescaped quotes inside strings. For example, write `围绕'最近最想做的事情'展开分享` or escape quotes as `围绕\"最近最想做的事情\"展开分享`.
- Do not handwrite large JSON blocks when a script can generate them. Use `json.dumps(..., ensure_ascii=False, indent=2)` in Python when building `article.json` programmatically.
