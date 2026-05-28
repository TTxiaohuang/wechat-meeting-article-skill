# 组会公众号推文生成技能

把课题组组会、读书分享会、文献汇报的会议材料整理成微信公众号推文草稿。

## 这个技能能做什么？

每次开完组会后，你可能有一堆材料：录音转录稿、英语发言稿、文献 PDF、PPT、会议照片……手动把这些整理成一篇排版好看的公众号推文，既费时又费力。

这个技能让 AI Agent 帮你完成这件事：**把原始素材变成一篇可以直接粘贴到微信公众号编辑器的推文**。

### 输入（你提供）

- 录音转录稿（`.docx`、`.txt`、`.md`）
- 英语交流发言稿（`.docx`、`.txt`）
- 文献 PDF / PPT（`.pdf`、`.pptx`）
- 会议照片（`.jpg`、`.png`）
- 其他材料（获奖喜讯、通知等）

### 输出（技能生成）

| 文件 | 说明 |
|------|------|
| `article.json` | 结构化数据源，所有内容的中间格式 |
| `article.wechat.html` | 微信兼容的 HTML，可直接粘贴到公众号 |
| `article.preview.html` | 浏览器预览版，方便检查排版效果 |
| `article_notes/` | 长材料的中间笔记（可选） |

## 环境准备

### 1. 安装 Python

本技能需要 **Python 3.8 或更高版本**。

**检查是否已安装：**

打开终端（Windows 按 `Win+R` 输入 `cmd` 回车），输入：

```bash
python --version
```

如果显示 `Python 3.x.x` 就说明已安装。如果提示"不是内部命令"，需要先安装 Python：

- 去 [python.org](https://www.python.org/downloads/) 下载最新版
- **安装时务必勾选 "Add Python to PATH"**（很重要！）

### 2. 安装依赖库

在终端中运行：

```bash
python -m pip install python-docx python-pptx pdfplumber pypdf
```

> 这些库用于从 Word、PPT、PDF 中提取文字。如果只需要处理 `.txt` 和 `.md` 文件，可以跳过这一步。

**国内加速**（如果下载很慢）：

```bash
python -m pip install python-docx python-pptx pdfplumber pypdf -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. Windows 用户额外设置

如果后续出现中文乱码，在终端中运行：

```powershell
$env:PYTHONIOENCODING="utf-8"
```

或者在 PowerShell 配置文件中永久添加，避免每次都设置。

## 安装技能

### 方式一：Git 克隆（推荐）

```bash
git clone https://github.com/TTxiaohuang/wechat-meeting-article-skill.git
```

然后把克隆下来的文件夹复制到你的 Agent 技能目录：

- **Claude Code**: `~/.claude/skills/wechat-meeting-article/`
- **Codex**: `~/.codex/skills/wechat-meeting-article/`

> `~` 在 Windows 上通常是 `C:\Users\你的用户名\`

### 方式二：Codex 一键安装

```
Use $skill-installer to install TTxiaohuang/wechat-meeting-article-skill path skills/wechat-meeting-article
```

### 安装后的目录结构

```
wechat-meeting-article/
  SKILL.md                          # 主技能文档（Agent 读这个）
  README.md                         # 本文件
  agents/openai.yaml                # Codex 配置
  assets/article-template.html      # 渲染器 HTML 模板
  references/                       # 参考文档（Agent 写文章时查阅）
    input-contract.md               # article.json 数据格式规范
    editorial-style.md              # 编辑风格指南
    material-extraction.md          # 素材提取策略
    wechat-formatting.md            # HTML/微信兼容性
    wechat-api.md                   # 微信 API（高级用法）
  scripts/                          # Python 脚本
    extract_materials.py            # 从素材中提取文字
    prepare_article_notes.py        # 生成中间笔记
    render_wechat_article.py        # 渲染为 HTML
    check_article_json.py           # 质量检查
    write_article_json.py           # Python dict 转 JSON
    update_article_gate.py          # 补充元数据
    draft_article_from_materials.py # scaffold 辅助（可选）
  tests/                            # 单元测试
    test_skill_scripts.py
```

## 使用方式

### 方式一：让 Agent 自动引导（最简单）

在 Claude Code 或 Codex 中告诉 Agent：

```
请读取 wechat-meeting-article 技能，帮我把组会材料生成微信公众号推文。
```

Agent 会：

1. 问你几个问题（素材在哪里、选什么模板和配色等）
2. 扫描你的素材文件夹
3. 再问你几个问题（日期、图片用途、封面样式等）
4. 自动提取文字、生成文章、渲染 HTML
5. 告诉你怎么把文章粘贴到微信公众号

**你只需要回答 Agent 的问题，其他全自动。**

### 方式二：命令行手动执行

如果你想手动控制每一步，或者想了解底层流程：

**第一步：准备素材文件夹**

把所有素材文件放在同一个文件夹里，例如 `D:\推文素材\`。子文件夹也可以，会自动递归扫描。

```
D:\推文素材\
  英语交流稿子.docx
  文献1-公共数据开放.pdf
  组会PPT.pptx
  录音转录稿.docx
  照片\
    合影.jpg
    讨论.jpg
```

**第二步：提取素材文字**

```bash
python scripts/extract_materials.py D:\推文素材 --out extracted_materials
```

这会把所有 Word、PPT、PDF、TXT、Markdown 文件转成纯文本 Markdown，并生成一个 `materials_manifest.json` 清单。

> 如果素材文件夹有子文件夹，会自动递归扫描。加 `--no-recursive` 只扫描顶层。

**第三步：生成中间笔记（可选但推荐）**

```bash
python scripts/prepare_article_notes.py extracted_materials --out article_notes
```

这会生成论文笔记和转录稿笔记，帮助 Agent 更好地理解长材料。

**第四步：创建 article.json**

这是核心步骤——由 Agent（或你手动）根据提取的文字创建结构化的 `article.json`。

`article.json` 包含：
- `meta`：标题、日期、主持人、编辑等元信息
- `sections`：英语交流、文献分享、时政交流、自由讨论等板块
- `custom_sections`：喜讯、通知等插入内容

完整的格式规范见 `references/input-contract.md`。

**第五步：渲染 HTML**

```bash
python scripts/render_wechat_article.py article.json --out dist
```

生成两个文件：
- `dist/article.wechat.html` — 微信兼容 HTML
- `dist/article.preview.html` — 浏览器预览版

如果文章中有本地图片，加 `--embed-images` 让图片嵌入 HTML：

```bash
python scripts/render_wechat_article.py article.json --out dist --embed-images
```

**第六步：质量检查**

```bash
python scripts/check_article_json.py article.json --html dist/article.wechat.html
```

检查项包括：scaffold 是否已展开、文件名是否泄漏到正文、文献字段是否完整、文章是否过短等。

**如果有问题，必须修复后再交付。**

## 导入微信公众号

### 方法一：浏览器复制（推荐）

1. 用浏览器打开 `dist/article.preview.html`
2. `Ctrl+A` 全选页面内容
3. `Ctrl+C` 复制
4. 打开微信公众号后台编辑器
5. `Ctrl+V` 粘贴
6. 手机预览确认排版无误后发布

> **注意：** 不要直接打开 `article.wechat.html` 的源码复制！那样会把 HTML 标签也复制进去。一定要打开 `article.preview.html`，复制**渲染后的富文本**。

### 方法二：使用第三方编辑器

也可以导入以下工具后再复制到微信：

- [doocs/md](https://github.com/doocs/md) — Markdown 编辑器
- 135 编辑器 — 支持 HTML 源码导入
- 秀米 — 支持 HTML 导入

导入后检查横滑卡片和引用块，因为编辑器可能会清理部分样式。

### 记得填写这些字段

粘贴正文后，还需要在微信公众号后台手动填写：

- **公众号标题**：来自 `article.json` 的 `meta.title`
- **摘要**：基于 `meta.summary` 的一句话概括
- **封面图**：用会议照片、PPT 标题页、或自动生成的封面卡

## 模板和配色

技能内置 5 种模板和 9 种配色，可以自由搭配：

### 模板

| 名称 | 风格 | 适合场景 |
|------|------|----------|
| `classic` | 经典简洁 | 默认选择，稳重百搭 |
| `notebook` | 笔记风格 | 像读书笔记，左侧竖线装饰 |
| `campus` | 校园清新 | 适合学生课题组公众号 |
| `magazine` | 编辑排版 | 更有杂志感，标题处理突出 |
| `briefing` | 报告风格 | 更正式，适合汇报型内容 |

### 配色

| 名称 | 色调 | 适合搭配 |
|------|------|----------|
| `classic` | 蓝色 + 暖色 | 百搭 |
| `forest` | 学术绿 | 学术氛围 |
| `blueprint` | 蓝图蓝 | 正式报告 |
| `warm` | 棕绿暖色 | 温馨阅读感 |
| `ink` | 灰黑墨色 | 沉稳学术 |
| `sunrise` | 珊瑚暖色 | 活泼校园风 |
| `mono` | 近乎单色 | 极简主义 |
| `sakura` | 樱花粉 | 柔和清新 |
| `ocean` | 深海蓝 | 沉静专业 |

## 常见问题

### Q: 报错 "python 不是内部或外部命令"

Python 没有加入系统 PATH。重新安装 Python，安装时勾选 **"Add Python to PATH"**。

### Q: 报错 "No module named 'docx'" 或类似错误

没装依赖库。运行：

```bash
python -m pip install python-docx python-pptx pdfplumber pypdf
```

### Q: 中文输出变成乱码

Windows 终端默认编码不是 UTF-8。运行：

```powershell
$env:PYTHONIOENCODING="utf-8"
```

然后再执行之前的命令。

### Q: 质量检查报错 "scaffold-generated article must be expanded"

你用了 `draft_article_from_materials.py` 生成的 scaffold JSON，它只是个骨架，内容不完整。需要让 Agent 或手动把内容补全后再渲染。

### Q: 渲染后图片不显示

两种情况：

1. **没加 `--embed-images`**：本地图片需要嵌入才能在浏览器预览中显示。加上这个参数重新渲染。
2. **图片路径不对**：检查 `article.json` 中图片路径是否正确。路径相对于 `article.json` 所在目录。

### Q: 微信编辑器里排版和预览不一样

微信编辑器会清理部分 CSS 样式。建议：

- 使用本技能内置的保守 inline styles（已针对微信优化）
- 粘贴后用手机预览检查
- 避免使用复杂的 CSS 特性

### Q: 素材文件夹里有子文件夹，文件没被提取

默认会递归扫描子文件夹。如果仍然没有，请检查文件扩展名是否为 `.docx`、`.pptx`、`.pdf`、`.txt`、`.md` 中的一种。

## 运行测试

```bash
cd wechat-meeting-article
python -m unittest discover -s tests -v
```

## 注意事项

- **不要提交微信凭据**（appid、secret、token）
- **不要提交未公开的录音、转录稿、内部 PPT 或私人材料**到公开仓库
- 本技能**只生成 HTML 草稿**，不会自动发布到微信公众号
- 自动发布需要通过微信 API，需明确人工确认

## 相关文档

| 文档 | 内容 |
|------|------|
| `SKILL.md` | Agent 主文档，完整工作流程 |
| `references/input-contract.md` | `article.json` 数据格式规范 |
| `references/editorial-style.md` | 编辑风格和写作指南 |
| `references/material-extraction.md` | 素材提取和 ASR 处理策略 |
| `references/wechat-formatting.md` | HTML/SVG 微信兼容性说明 |
| `references/wechat-api.md` | 微信公众号 API（高级用法） |
