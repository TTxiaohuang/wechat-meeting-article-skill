# 输入契约

使用 UTF-8 编码创建 `article.json`。必需的顶级字段是 `_meta`、`meta` 和 `sections`；推荐字段是 `theme`、`template`、`palette`、`custom_sections`，可选字段是 `assets`。

**推荐用文件写入工具直接写 `article.json`。** 写完后立即运行渲染器验证 JSON 语法。避免中文引号导致的编码错误：

- JSON 字符串中的中文引号 `""` 用 Unicode 转义 `“` 和 `”`，或改用 `《》` 替代。
- 始终在写入后立即运行渲染器验证。

如果环境支持 UTF-8 Python 源文件，也可以创建 `article_data.py` 写 Python dict 再转 JSON：

```bash
python scripts/write_article_json.py article_data.py --out article.json
```

使用 `scripts/update_article_gate.py` 给已有的 `article.json` 补充 intake 元数据：

```bash
python scripts/update_article_gate.py article.json --material-folder path/to/material-folder --date 2026-05-28 --editor "推文编辑" --template classic --palette classic
```

已提取素材时可以先生成脚手架用于清点：

```bash
python scripts/draft_article_from_materials.py extracted_materials --out article.scaffold.json
```

不要直接交付 `article.scaffold.json`。它是确定性启发式生成的，会遗漏大量内容。最终 `article.json` 必须由 agent 阅读提取素材后手动扩展完成。

## 最小示例

```json
{
  "_meta": {
    "intake_gate": {
      "material_folder": {"value": "D:/推文素材", "status": "user_provided"},
      "date": {"value": "2026-05-27", "status": "user_provided"},
      "editor": {"value": "推文编辑", "status": "user_provided"},
      "visual_style": {"value": "classic", "status": "default_confirmed"}
    }
  },
  "theme": "zhengeryanzi",
  "template": "classic",
  "palette": "classic",
  "meta": {
    "title": "第 X 周组会纪要",
    "date": "2026-05-27",
    "group": "课题组名称",
    "host": "主持人",
    "editor": "推文编辑",
    "summary": "本次组会围绕英语交流、文献分享、时政交流和自由讨论展开。"
  },
  "sections": {
    "english_exchange": {
      "title": "英语交流",
      "topic": "本周话题",
      "intro": "简要说明交流主题。",
      "images": [],
      "speeches": [
        {
          "speaker": "张三",
          "role": "学生",
          "mode": "full_text",
          "text": "English speech text here.",
          "source": "english_speeches/zhangsan.docx",
          "photo": "zhangsan.jpg"
        }
      ]
    },
    "literature_sharing": {
      "title": "文献分享",
      "intro": "",
      "images": [],
      "papers": [
        {
          "title": "Paper title",
          "authors": "Author A et al.",
          "venue": "Journal, Year",
          "doi": "",
          "presenter": "李四",
          "images": [],
          "background": "文献研究背景。",
          "research_question": "文献试图回答的核心问题。",
          "methods_data": "数据、方法、模型或识别策略。",
          "findings": [
            "核心发现一。",
            "核心发现二。"
          ],
          "discussion_value": "这篇文献对本次组会或课题组研究的启发。",
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
      "images": [],
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
      "intro": "围绕学术工具使用、近期计划和学术活动展开讨论。",
      "images": [],
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
  "custom_sections": [
    {
      "type": "honor_news",
      "placement": "after_lead",
      "title": "喜讯",
      "person": "张三同学",
      "award": "XX 奖",
      "organization": "主办单位",
      "date": "",
      "text": "祝贺张三同学荣获 XX 奖。",
      "images": [],
      "source": "honor.docx"
    }
  ],
  "sessions": [
    {
      "type": "graduation_career_sharing",
      "title": "毕业论文与就业分享",
      "topic": "论文进展与求职经验",
      "intro": "本次环节邀请三位同学分享毕业论文进展和求职心得。",
      "images": [],
      "items": [
        {
          "speaker": "李四",
          "text": "分享内容。",
          "source": "transcript.docx"
        }
      ],
      "closing": ""
    }
  ],
  "assets": {
    "images": []
  }
}
```

## Sessions

`sessions` 数组是 `sections` 的替代方案，用于非标会议结构。当 `sessions` 存在时，渲染器按数组顺序渲染，忽略 `sections`。

- 每个 session 需要 `type`、`title` 和 `items`。
- `type`：任意字符串。预定义类型（`english_exchange`、`literature_sharing`、`policy_discussion`、`free_discussion`）有专用渲染样式；其他 type 走通用渲染（标题 → topic 标签 → 引言 → 图片 → items 引用块 → 小结）。
- `title`：文章中显示的章节标题。
- `topic`（可选）：渲染为标题下方的标签。
- `intro` / `summary`（可选）：引言段落。
- `images`（可选）：章节级图片。
- `items`（必需）：`{speaker, text, source?, images?}` 数组，渲染为引用块。
- `closing`（可选）：渲染为带边框的"小结"卡片。
- Agent 通过数组位置控制顺序。
- 没有素材的 session 直接省略。

## 规则

- `text`、`summary`、`intro`、`closing` 用纯文本，渲染器自动转义 HTML。
- 即使只有一篇论文、一条评论或一段发言，也要用数组。
- 保留 `_meta.intake_gate` 在最终文章中。必需的决策字段是 `material_folder`、`date`、`editor` 和 `visual_style`。
- 如果不需要编辑署名，设 `_meta.intake_gate.editor.status` 为 `omitted_confirmed`；否则设 `meta.editor`。
- 如果接受默认视觉风格，设 `_meta.intake_gate.visual_style.status` 为 `default_confirmed`。
- 不确定的字段留空字符串。当缺失字段影响发布准确性或隐私时，向用户确认。
- 素材有冲突时，在备注中保留冲突并询问用户，不要静默合并。
- `source` 路径尽量相对于素材文件夹。
- `source` 是私有溯源元数据，渲染器不会在微信正文中显示。仅在用户要求时才创建 `source_trace.md`。
- 英语发言的 `mode: "full_text"` 表示卡片保留原始发言稿全文，这是有发言稿时的默认行为。
- 文献分享优先使用 `background`、`research_question`、`methods_data`、`findings`、`discussion_value`，而非简短的 `summary`。
- `images` 可以是字符串或对象 `{"url": "路径或URL", "caption": "图注", "alt": "替代文本"}`。仅使用素材中提供或明确生成的图片。
- 将素材中的图片放入章节级 `images` 或论文级 `images`。微信导入时优先使用已上传到可靠图床的 URL，本地路径仅用于预览。
- 英语发言卡片可用 `photo` 字段指定发言人头像（如 `"photo": "edward.jpg"`）。渲染器显示为姓名上方的小圆形头像。使用相对于素材文件夹的路径。`photo` 为空或文件不存在时，渲染器自动生成 SVG 首字母头像。
- 使用 `--embed-images` 参数将本地图片嵌入为 base64 data-uri，确保浏览器预览正常显示，粘贴到微信时自动上传。不用此参数时，本地图片路径必须从 HTML 文件位置可解析。
- **条目级图片**：评论、讨论条目和观点支持可选的 `images` 数组，渲染在引用块底部。示例：`{"speaker": "同学", "text": "...", "images": ["result.png"]}`。
- **行内图片标记**：文本字段可包含 `{{image:src}}` 或 `{{image:src|caption}}` 标记，在指定位置插入图片。渲染器在标记处分割文本并插入图片。示例：`"text": "结果如下：\n\n{{image:table1.png|回归结果}}\n\n可以看出..."`。行内标记适用于所有由 `paragraphs()` 渲染的文本字段。
- 没有素材的环节直接省略，不要填占位文本。
- 非标会议使用 `sessions`。`sessions` 存在时渲染器忽略 `sections`，按数组顺序渲染。预定义类型有专用样式，其他走通用渲染。
- `custom_sections` 仅用于读书分享会流程中的偶尔插页。支持的插页 `type` 有 `honor_news`、`announcement`、`milestone`、`note`。
- 支持的 `placement` 值：`after_lead`、`before_english_exchange`、`after_english_exchange`、`before_literature_sharing`、`after_literature_sharing`、`before_policy_discussion`、`after_policy_discussion`、`before_free_discussion`、`after_free_discussion`、`before_closing`。省略时默认 `after_lead`。
- `honor_news` 需包含 `person`、`award`、`organization`、`date`、`text`。包含私密照片、证书号、不确定的姓名或不完整的奖项详情时，发布前需确认。
- `"theme": "zhengeryanzi"` 是默认值，直接写入，无需询问。渲染器自动添加章节标记和"本期记录由郑而研资整理"的结尾署名。
- `template` 可选值：`"classic"`、`"notebook"`、`"campus"`、`"magazine"`、`"briefing"`。旧名称通过别名映射。
- `palette` 可选值：`"classic"`、`"forest"`、`"blueprint"`、`"warm"`、`"ink"`、`"sunrise"`、`"mono"`、`"sakura"`、`"ocean"`。每篇文章只用一个配色。
- 交付前运行 `scripts/check_article_json.py article.json --html dist/article.wechat.html`，修复所有报错。除非用户明确接受某个风险，否则所有问题都必须修复。
- `_meta.scaffold_generated` 存在说明这不是最终文章，必须重写或扩展后再渲染。
- JSON 使用标准双引号。不要在字符串中粘贴未转义的引号。大文章优先用 `write_article_json.py` 或 Python `json.dumps(..., ensure_ascii=False, indent=2)`。
- **自由讨论内容分离**：`free_discussion.items` 不能与 `literature_sharing.papers[].comments` 重复。文献特定的反馈（方法论批评、论文评价、主讲人回应）留在文献评论中。自由讨论涵盖更广泛的话题：未来计划、工具推荐、活动通知、通用建议、跨论文反思。
- **自由讨论编辑提炼**：自由讨论条目必须从原始转录稿提炼浓缩。去掉口头禅、重复和跑题。每条保留 2-4 句核心观点，不粘贴原文。**同一发言人的多段发言必须合并为一个 item，不得拆成多张卡片。**
- **自由讨论必须有 `intro`**：始终包含简短的 `intro`（1-2 句话），概括本环节讨论的话题。

## 手动填写的微信字段

将渲染的 HTML 粘贴到微信编辑器只填充了正文。最终回复中还需提供：

- 公众号标题：使用 `meta.title` 或其润色版本
- 摘要：基于 `meta.summary` 的一句话概括
