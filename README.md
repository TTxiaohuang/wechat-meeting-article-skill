# 组会公众号推文生成技能

把课题组组会、读书分享会、文献汇报的会议材料整理成微信公众号推文草稿。

## 这个技能能做什么？

每次开完组会后，你可能有一堆材料：录音转录稿、英语发言稿、文献 PDF、PPT、会议照片……手动把这些整理成一篇排版好看的公众号推文，既费时又费力。

这个技能让 AI Agent 帮你完成这件事：**把原始素材变成一篇可以直接粘贴到微信公众号编辑器的推文**。

### 输入（你提供）

| 素材类型 | 格式 | 必要性 |
|----------|------|--------|
| 录音转录稿 | `.docx`、`.txt`、`.md` | 推荐 |
| 英语交流发言稿 | `.docx`、`.txt` | 推荐 |
| 分享的论文 | `.pdf` | 推荐 |
| 组会 PPT | `.pptx` | 推荐 |
| 会议照片、证书图片等 | `.jpg`、`.png` | 可选 |

> 转录稿是噪声源——ASR 识别常有错误。PPT 和 PDF 能提供准确的论文信息，建议至少准备这两样。

### 输出（技能生成）

| 文件 | 说明 |
|------|------|
| `article.json` | 结构化数据源，所有内容的中间格式 |
| `article.wechat.html` | 微信兼容的 HTML，可直接粘贴到公众号 |
| `article.preview.html` | 浏览器预览版，方便检查排版效果 |
| `article_notes/` | 长材料的中间笔记（可选） |

## 整体流程一览

技能运行时，AI 会分**两轮**向你提问，中间自动处理素材：

```
准备素材文件夹
       │
       ▼
┌─────────────────────────────────────┐
│  第一轮提问（5 个问题）              │
│  ① 素材文件夹路径                    │
│  ② 会议类型（标准/有额外/完全不同）  │
│  ③ 文章模板（5 种可选）              │
│  ④ 配色方案（9 种可选）              │
│  ⑤ 编辑姓名（用于署名）              │
└─────────────────────────────────────┘
       │
       ▼
  AI 自动提取素材文字（安装依赖、扫描文件）
       │
       ▼
┌─────────────────────────────────────┐
│  第二轮提问                          │
│  ① 确认日期、主持人                  │
│  ② 逐张确认图片内容和放置位置        │
│  ③ 可选插页（喜报、通知、里程碑）    │
└─────────────────────────────────────┘
       │
       ▼
  AI 自动编写推文 → 渲染排版 → 质检
       │
       ▼
  交付：预览 HTML + 复核建议
```

> **注意：** 不是点一下就完事。两轮提问之间需要你配合回答问题，特别是图片确认——AI 不会自己猜图片内容，每张都会问你。

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

> 这些库用于从 Word、PPT、PDF 中提取文字。AI 在首次运行时也会自动安装，但提前装好可以避免等待。

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

### 方式一：Agent 自动安装（最简单）

在 Claude Code、Codex 或 WorkBuddy 中发送：

```
请帮我安装这个skill：https://github.com/TTxiaohuang/wechat-meeting-article-skill
```

安装只需一次，以后每次使用无需重复安装。

### 方式二：Git 克隆手动安装

```bash
git clone https://github.com/TTxiaohuang/wechat-meeting-article-skill.git
```

然后把克隆下来的文件夹复制到你的 Agent 技能目录：

- **Claude Code**: `~/.claude/skills/wechat-meeting-article/`
- **Codex**: `~/.codex/skills/wechat-meeting-article/`

> `~` 在 Windows 上通常是 `C:\Users\你的用户名\`

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

### 方式一：让 Agent 自动引导（推荐）

在 Claude Code 或 Codex 中告诉 Agent：

```
我要制作推文
```

Agent 会：

1. **第一轮提问**：素材路径 → 会议类型 → 模板 → 配色 → 编辑姓名
2. **自动提取素材**：扫描文件夹、安装依赖、提取文字
3. **第二轮提问**：确认日期主持人 → 逐张确认图片 → 可选插页
4. **自动编写推文**：阅读编辑规范、撰写 `article.json`、渲染 HTML
5. **自动质检**：运行 `check_article_json.py`，发现问题自动修复
6. **交付**：告诉你预览文件位置，建议公众号标题和摘要

**你只需要回答 Agent 的问题，其他全自动。**

### 方式二：命令行手动执行

如果你想手动控制每一步：

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

> **重要：** 不要手写 JSON 字符串——中文引号会导致编码错误。用 `scripts/write_article_json.py` 写 Python dict 再转 JSON，或用 `json.dump()`。

**第五步：渲染 HTML**

```bash
python scripts/render_wechat_article.py article.json --out dist
```

如果文章中有本地图片，加 `--embed-images` 让图片嵌入 HTML：

```bash
python scripts/render_wechat_article.py article.json --out dist --embed-images
```

> **注意：** 使用 `--embed-images` 时，必须在素材文件夹目录下运行渲染命令，否则相对路径的图片无法嵌入。

**第六步：质量检查**

```bash
python scripts/check_article_json.py article.json --html dist/article.wechat.html
```

检查项包括：scaffold 是否已展开、文件名是否泄漏到正文、文献字段是否完整、文章是否过短等。

**如果有问题，必须修复后再交付。**

## 导入微信公众号

### 复制粘贴（推荐）

1. 用浏览器打开 `dist/article.preview.html` 预览效果
2. 用浏览器打开 `dist/article.wechat.html`（这个版本专门用于复制）
3. `Ctrl+A` 全选页面内容
4. `Ctrl+C` 复制
5. 打开微信公众号后台编辑器，点击**正文输入区域**
6. `Ctrl+V` 粘贴

> **注意：** 不要直接复制 `article.wechat.html` 的源码！那样会把 HTML 标签也复制进去。一定要在浏览器中打开，复制渲染后的富文本。

### 记得填写这些字段

粘贴正文后，还需要在微信公众号后台手动填写：

- **公众号标题**：来自 AI 建议的标题，或 `article.json` 的 `meta.title`
- **摘要**：基于 AI 建议的摘要，或 `meta.summary` 的一句话概括

## 会议类型说明

技能支持三种会议类型，AI 在第一轮提问时会让你选择：

| 类型 | 说明 | 文章结构 |
|------|------|----------|
| **标准流程** | 英语交流、文献分享、时政交流、自由讨论等常规环节 | 使用 `sections`，按固定顺序排列 |
| **有额外环节** | 在标准流程基础上增加了毕业分享、开题报告等 | 使用 `sessions`，AI 会追问具体新增了哪些环节 |
| **完全不同的流程** | 与常规读书分享会完全不一样的安排 | 使用 `sessions`，AI 会请用户描述完整环节列表 |

> 时政交流环节如果本次没有，选"标准流程"后告诉 AI 跳过即可。

## 模板和配色

技能内置 5 种模板和 9 种配色，可以自由搭配。AI 在第一轮提问时会让你选择，也可以选"更多"查看全部选项。

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

国内加速：

```bash
python -m pip install python-docx python-pptx pdfplumber pypdf -i https://pypi.tuna.tsinghua.edu.cn/simple
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
2. **没在素材文件夹目录下运行**：使用 `--embed-images` 时，必须在素材文件夹目录下运行渲染命令，否则相对路径的图片无法嵌入。

### Q: 微信编辑器里排版和预览不一样

微信编辑器会清理部分 CSS 样式。建议：

- 使用本技能内置的保守 inline styles（已针对微信优化）
- 粘贴后用手机预览检查
- 避免使用复杂的 CSS 特性

### Q: AI 为什么要问那么多问题？

AI 需要确认会议类型（决定文章结构）、模板配色（决定视觉风格）、图片内容（不猜只问）。这些信息直接影响推文质量，跳过会导致排版错误或内容遗漏。两轮提问加起来大约 10 个问题，回答起来很快。

### Q: 生成的推文可以直接发吗？

不建议直接发。AI 生成的是高质量草稿，但仍需人工复核人名、论文信息等关键内容。特别是 ASR 转录的发言内容，可能有识别错误。AI 会提供复核建议清单，按照清单检查即可。

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
| `references/intake-gate-ui.md` | Intake Gate UI 约束（`AskUserQuestion` 选项格式） |
