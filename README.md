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
- `source_trace.md`：来源追踪说明

当前版本默认会保留英语发言原文，不在正文中显示本地 source 文件名，并把文献分享整理成“研究背景、研究问题、方法与数据、核心发现、讨论价值、讨论摘录”等阅读笔记式结构。

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

### 3. 编写 article.json

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

空模板或 scaffold 都只是辅助工具。最终 `article.json` 应当体现 AI 对材料的完整阅读、归纳和写作。

### 4. 渲染微信公众号 HTML

```powershell
python skills\wechat-meeting-article\scripts\render_wechat_article.py article.json --out dist
```

输出：

```text
dist/article.wechat.html
dist/article.preview.html
```

### 5. 发布前质量检查

```powershell
python skills\wechat-meeting-article\scripts\check_article_json.py article.json --html dist\article.wechat.html
```

该检查会提示：

- 正文是否泄露 `.docx`、`.pdf`、`.pptx` 等 source 文件名
- 文献分享是否缺少研究背景、研究问题、方法与数据、核心发现、讨论价值
- 英语发言是否过短，可能没有保留完整原文
- 是否误把 scaffold 当成最终稿
- 正文字数是否异常偏少

### 6. 导入微信公众号

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
- 来源追踪：source 文件名只用于 `article.json` 和 `source_trace.md`，不出现在公众号正文。
- 图片使用：优先使用用户提供的会议照片、PPT 截图、论文图示或封面图；不要编造数据图和论文图。
- 章节灵活：没有时政交流或某个环节时，直接省略，不硬凑模板。

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
