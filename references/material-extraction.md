# 素材提取

当输入文件夹包含 `.docx`、`.pptx`、`.pdf`、`.txt`、`.md`、`.html` 或 `.htm` 文件时参考本文件。

## 推荐命令

```bash
python scripts/extract_materials.py path/to/material-folder --out extracted_materials
```

脚本输出：

- 每个支持的源文件对应一个 Markdown 文本文件
- `materials_manifest.json`：源路径、输出路径、状态、提取元数据和错误信息

默认递归扫描所有子目录。仅扫描顶层文件：

```bash
python scripts/extract_materials.py path/to/material-folder --out extracted_materials --no-recursive
```

不同子目录下同名文件会自动在输出文件名前加子目录路径前缀以避免冲突（如 `subdir/paper.md` 变为 `subdir_paper.md`）。

输出文件名会清理特殊字符以兼容 agent 和 shell。引号类字符、路径分隔符等替换为下划线。原始源路径保留在 `materials_manifest.json` 中。

所有支持的文件类型默认全量提取。PDF 会在 manifest 中额外记录页数。限制 PDF 提取页数：

```bash
python scripts/extract_materials.py path/to/material-folder --out extracted_materials --pdf-pages 10
```

明确全量提取：

```bash
python scripts/extract_materials.py path/to/material-folder --out extracted_materials --pdf-pages all
```

每个 PDF 的 manifest 记录 `pdf_pages_total`、`pdf_pages_requested`、`pdf_pages_extracted` 和 `pdf_text_pages`。`pdf_text_pages` 为 0 说明该 PDF 可能是扫描件或纯图片，不应视为可读。

提取后，生成带预算的中间笔记：

```bash
python scripts/prepare_article_notes.py extracted_materials --out article_notes
```

脚本输出：

- `paper_notes.json`：论文级元数据和围绕摘要、方法、结果、稳健性/机制、结论的短摘录
- `transcript_notes.json`：转录稿中讨论话题、老师评论、学生问题和不确定 ASR 区域的线索
- `intake_decision.template.json`：需要复制到 `_meta.intake_gate` 的 intake 门控结构

这些文件用作索引，不能替代原文阅读；在做出精确判断前仍需回到提取的 Markdown 中查看相关段落。

## 依赖安装

按需安装可选解析器：

```bash
python -m pip install python-docx python-pptx pdfplumber pypdf
```

如果 agent 在受限环境中运行，安装依赖前先询问用户。如果无法安装，告知用户哪些格式无法提取，继续使用可用的文本文件。

## Windows 编码

中文输出优先使用 UTF-8：

```powershell
$env:PYTHONIOENCODING="utf-8"
```

本技能的 Python 脚本在支持的情况下会调用 `sys.stdout.reconfigure(encoding="utf-8")`。

当 agent 或 shell 读取提取的中文 Markdown 出现乱码时，用 Python 显式指定 UTF-8 编码：

```bash
python -c "from pathlib import Path; print(Path('extracted_materials/file.md').read_text(encoding='utf-8'))"
```

## 提取规则

- `.docx`、`.pptx`、`.pdf` 是二进制格式，不要直接读取原始文件。
- `.docx`：保留段落顺序和表格行。
- `.pptx`：保留幻灯片顺序和编号。
- `.pdf`：默认全量提取，以便文章覆盖标题、作者、摘要、方法、结果、稳健性检验、讨论和结论。全量提取不意味着 agent 必须把整个 PDF 放入上下文；通过标题和关键词搜索（如 摘要、引言、研究设计、数据、方法、结果、机制、稳健性、讨论、结论、limitations、conclusion）有选择地阅读。
- `.html`/`.htm`：提取正文文本，自动去除 `<script>`、`<style>`、`<svg>` 等非内容标签。对 reveal.js、Slidev 等演示框架生成的 HTML，自动按 `<section>` 或 `<div class="slide">` 拆分为幻灯片。
- 提取的 Markdown 文件较长时，先读 `article_notes`，再用搜索或定向读取。除非文件足够短能放进上下文，否则不要逐字读入。
- 提取错误记录到 manifest 中，不要静默跳过文件。
- 将提取的文本视为原始证据。最终文章仍需要基于来源的综合和可读的改写。

## 转录稿噪声处理

将录音转录文件视为噪声证据，而非权威引用。

- 用转录稿恢复讨论话题、老师评论、学生问题和待办事项。
- 将姓名、论文标题、日期、方法、机构、奖项和技术术语与 PPT、PDF、文件名和用户提供的笔记交叉校验。
- 仅在有其他材料强支撑或属于标准学术术语时，静默修复明显的 ASR 错误。
- 不要大段逐字引用转录稿，除非措辞清晰且有价值。
- 转录稿质量差时，总结稳定含义，避免过度精确的归属。
- 当 ASR 歧义影响公开事实（如谁获奖、确切奖项名称、会议日期、敏感个人信息）时，向用户确认一次。
- 模型无法解决转录稿噪声时，在草稿中标记为不确定，或从公开文章中省略，而非编造精炼的表述。

### ASR 发言人识别策略

ASR 转录通常产生通用标签（`发言人1`、`发言人2` 等）而非真实姓名。用以下策略匹配发言人：

1. **PPT 主讲人匹配**：PPT 的 `分享人` 字段标识会议主持人/主讲人。此人通常是 `发言人1`（第一位发言、开场和主持的人）。通过检查 `发言人1` 是否介绍会议结构和引导环节转换来验证。
2. **英语交流顺序匹配**：如果英语发言稿单独提供了真实姓名，将其与转录稿中的英语交流发言顺序匹配。转录稿中的发言顺序应与发言稿中的顺序一致。
3. **互动模式**：主持人通常会点名叫其他发言人（如"XX同学你有什么看法?"）。利用这些点名来识别后续发言人。
4. **角色标记**：老师通常给出较长的评价性意见、引用评分标准、布置任务。学生提问和讨论作业。
5. **不确定时**：用"同学"或"老师"归属，而非猜测具体姓名。仅在有多个交叉参考点支撑时才用具体姓名。

### 日期推断优先级

当有多个日期来源时，按以下优先级：

1. **用户提供日期**（最高）：用户明确说明的会议日期，覆盖所有其他来源。
2. **转录稿时间戳**：音频转录文件中嵌入的日期/时间戳，是用户未指定时最可靠的会议日期。
3. **PPT 元数据日期**：PPT 文件的创建/修改日期。注意——这可能是 PPT 的创建日期，而非会议日期。
4. **文件名日期**：文件名中嵌入的日期（如"4月27日编辑组会录音.mp3"）。
5. **文件修改日期**（最低）：操作系统文件修改时间戳，可能不可靠。

来源有冲突时，记录冲突并请用户确认使用哪个日期。始终优先使用用户提供的信息而非自动推断。
