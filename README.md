# 组会公众号推文 Skill

这是一个可迁移的 AI Agent Skill，用于把课题组组会、读书分享会、文献汇报等会议材料整理成微信公众号推文草稿。

它适合处理以下材料：

- 会议录音转文字文档
- 每个人的英语交流发言稿
- 文献 PDF、摘要或笔记
- PPT 文本内容
- 学生和老师的讨论观点
- 会议总结、自由讨论记录

默认输出：

- `article.json`：结构化推文数据源
- `article.wechat.html`：微信公众号友好的 HTML
- `article.preview.html`：浏览器预览版
- `article_notes/`：长材料/噪声转写的中间笔记，按需生成

`source_trace.md` 不再默认生成；只有需要审稿核对、引用对应或严格溯源时才生成。

当前版本默认会保留英语发言原文，不在正文中显示本地 source 文件名，并把文献分享整理成“研究背景、研究问题、方法与数据、核心发现、讨论价值、讨论摘录”等阅读笔记式结构。

默认主题为 `zhengeryanzi`，会加入章节 SVG 小标记和结尾签名。默认简介模板为 `template: "classic"`，不使用顶部大品牌卡或复杂动画，优先保证微信公众号编辑器兼容性。

可选读书分享会视觉风格和配色：

- `template`: `classic`、`notebook`、`journal`、`campus`、`minimal`、`magazine`、`warm-note`、`briefing`、`fieldnote`
- `palette`: `classic`、`forest`、`blueprint`、`warm`、`ink`、`sunrise`、`mono`

## 仓库结构

```text
skills/
  wechat-meeting-article/
    SKILL.md
    agents/openai.yaml
    references/
    scripts/
    assets/
tests/
  test_skill_scripts.py
```

## 在 Codex 中安装

如果 Codex 可使用 `skill-installer`，可以直接从 GitHub 安装：

```text
Use $skill-installer to install TTxiaohuang/wechat-meeting-article-skill path skills/wechat-meeting-article
```

Windows 手动安装：

```powershell
git clone https://github.com/TTxiaohuang/wechat-meeting-article-skill.git
Copy-Item -Recurse -LiteralPath .\wechat-meeting-article-skill\skills\wechat-meeting-article -Destination "$env:USERPROFILE\.codex\skills"
```

安装后重启 Codex，让它重新扫描 Skill。

## 在其他 Agent 中使用

其他 Agent 不一定有 Codex 的 Skill 自动发现机制，但仍然可以复用这个仓库。

先克隆仓库：

```powershell
git clone https://github.com/TTxiaohuang/wechat-meeting-article-skill.git
```

然后在 Agent 中说明：

```text
请读取 skills/wechat-meeting-article/SKILL.md，并按照该 Skill 将我的组会材料生成微信公众号推文。
```

这个 Skill 的流程刻意设计成文件驱动，因此可以在 Codex、Claude Code、WorkBuddy 或未来自建 Web 应用中复用。

## 推荐工作流

以下命令假设在仓库根目录执行。如果 Agent 当前工作目录不在仓库中，请使用脚本的绝对路径。

交互上应当分阶段进行：第一轮只问材料文件夹路径；盘点材料后，再确认少量真正需要人工判断的信息，例如编辑署名、是否接受默认风格、敏感图片或喜讯是否发布。不要在开头一次性抛出日期、主持人、编辑、风格、图片等完整清单。

### 1. 安装可选依赖

只有需要解析 `.docx`、`.pptx`、`.pdf` 时才需要：

```powershell
python -m pip install python-docx python-pptx pdfplumber pypdf
```

### 2. 提取材料文本

```powershell
python skills\wechat-meeting-article\scripts\extract_materials.py D:\推文素材 --out extracted_materials
```

输出：

```text
extracted_materials/
  materials_manifest.json
  *.md
```

脚本会安全化输出文件名，避免中文引号、路径分隔符等特殊字符导致 Agent 或 shell 读取失败。原始文件名会保留在 `materials_manifest.json` 中。

PDF 默认全文抽取，并在 manifest 中记录总页数、抽取页数和可抽取文本页数。扫描版或图片版 PDF 会提示可能无法读取。

### 3. 生成中间笔记

```powershell
python skills\wechat-meeting-article\scripts\prepare_article_notes.py extracted_materials --out article_notes
```

输出：

```text
article_notes/
  paper_notes.json
  transcript_notes.json
  intake_decision.template.json
```

这些文件用于节省上下文：先读笔记和索引，再按需回到 extracted Markdown 查原文。不要把长 PDF 和长转写稿一次性塞进模型上下文。

### 4. 编写 article.json

默认做法：让 Agent 阅读 `extracted_materials/` 中的材料，根据 `SKILL.md` 和 `references/input-contract.md` 写出完整的 `article.json`。

如果需要一个材料清单式脚手架，可以生成 `article.scaffold.json`：

```powershell
python skills\wechat-meeting-article\scripts\draft_article_from_materials.py extracted_materials --out article.scaffold.json
```

注意：`article.scaffold.json` 不是成稿，不能直接发布。它由确定性规则生成，可能严重遗漏英语发言、文献介绍和讨论观点。最终必须由 Agent 阅读材料后扩写成单独的 `article.json`。

如果想从空模板开始：

```powershell
python skills\wechat-meeting-article\scripts\create_article_json.py --out article.json
```

如果当前 Agent 能稳定写 UTF-8 Python 文件，推荐让 Agent 编写 `article_data.py` 中的 Python `ARTICLE` 字典，再安全导出 JSON：

```powershell
python skills\wechat-meeting-article\scripts\write_article_json.py article_data.py --out article.json
```

这样可以避免中文正文或论文题名中的英文引号破坏 JSON。空模板或 scaffold 都只是辅助工具。最终 `article.json` 应当体现 AI 对材料的完整阅读、归纳和写作。

如果在 Claude Code / Windows Bash 环境中出现中文源码乱码，不要反复尝试大型 heredoc 或超长内联 Python。可以直接写 `article.json`，立即运行渲染器检查 JSON 语法，然后用脚本补齐 intake gate：

```powershell
python skills\wechat-meeting-article\scripts\update_article_gate.py article.json `
  --material-folder D:\推文素材 `
  --date 2025-06-06 `
  --editor 黄俊曦 `
  --template campus `
  --palette sunrise
```

### 5. 渲染微信公众号 HTML

```powershell
python skills\wechat-meeting-article\scripts\render_wechat_article.py article.json --out dist
```

输出：

```text
dist/article.wechat.html
dist/article.preview.html
```

### 6. 发布前质量检查

```powershell
python skills\wechat-meeting-article\scripts\check_article_json.py article.json --html dist\article.wechat.html
```

该检查会提示：

- 是否缺少 intake gate 中的材料路径、日期、编辑署名/省略确认、视觉风格确认
- 正文是否泄露 `.docx`、`.pdf`、`.pptx` 等 source 文件名
- 文献分享是否缺少研究背景、研究问题、方法与数据、核心发现、讨论价值
- 英语发言是否过短，可能没有保留完整原文
- 是否误把 scaffold 当成最终稿
- 正文字数是否异常偏少

检查失败应视为阻塞项，除非用户明确接受具体风险。

### 7. 导入微信公众号

不要把 `article.wechat.html` 的源码直接粘贴到微信公众号编辑器，否则可能显示成代码。

推荐方式：

1. 用浏览器打开 `dist/article.preview.html`
2. 在浏览器中选中渲染后的正文
3. 复制富文本
4. 粘贴到微信公众号后台编辑器
5. 手机预览后再发布

也可以把 `article.wechat.html` 导入 doocs/md、135 编辑器、秀米等支持 HTML 的公众号排版工具。

## 内容与排版原则

- 英语交流：如果提供了每个人的发言稿，默认完整保留英文原文，不擅自提炼。
- 文献分享：优先写成结构化阅读笔记，而不是只写几句摘要。
- 讨论观点：保留学生和老师的观点差异，避免把所有观点合并成模糊总结。
- 来源追踪：source 文件名只用于 `article.json` 的内部核对，不出现在公众号正文；`source_trace.md` 仅在用户要求时生成。
- 长材料：先读 `article_notes/`，再按需查原文，不要求模型记住整篇 PDF 或长转写。
- 转写稿：录音转文字视为 noisy transcript，优先提炼稳定含义，涉及人名、奖项、日期、论文题名等公开事实时要交叉核对。
- 图片使用：优先使用用户提供的会议照片、PPT 截图、论文图示或封面图；不要编造数据图和论文图。
- 章节灵活：没有时政交流或某个环节时，直接省略，不硬凑模板。
- 品牌视觉：默认使用 `theme: zhengeryanzi` 的静态品牌视觉；SVG 动画和交互效果应作为实验功能单独测试。
- 模板选择：默认保留 `template: classic`；需要变化时可改为其他读书分享会视觉风格，并搭配 `palette` 控制整体配色。
- 署名信息：必须填写 `meta.editor`，或在 `_meta.intake_gate.editor.status` 中记录 `omitted_confirmed`。结尾会显示为“主持：... ｜ 推文编辑：...”。
- 图片添加：把图片放入 `cover_image`、章节 `images` 或文献 `images`。微信公众号正式发布时，图片最好先上传到公众号/排版编辑器，再使用稳定 URL 或在编辑器中手动替换。

## 测试

仓库包含标准库 `unittest` 测试，不需要额外安装 pytest：

```powershell
python -m unittest discover -s tests -v
```

Skill 结构校验：

```powershell
python C:\Users\Puleya\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills\wechat-meeting-article
```

## 注意事项

- 不要提交微信公众号 `appid`、`secret`、token、cookie 或其他凭据。
- 不要提交未公开的原始会议录音、转录稿、内部 PPT 或私人材料。
- 默认只生成 HTML 或草稿箱 payload。直接自动发布公众号文章必须经过明确人工确认。
