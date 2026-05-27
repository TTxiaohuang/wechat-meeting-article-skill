# 组会公众号推文 Skill

把课题组组会、读书分享会、文献汇报的会议材料整理成微信公众号推文草稿。

## 处理的材料

- 会议录音转文字（`.docx`）
- 英语交流发言稿
- 文献 PDF / 摘要 / 笔记
- PPT 文本内容
- 讨论观点、会议总结
- 会议照片、截图、证书等图片素材

## 输出

| 文件 | 用途 |
|------|------|
| `article.json` | 结构化推文数据源（可二次编辑） |
| `article.wechat.html` | 微信公众号兼容 HTML |
| `article.preview.html` | 浏览器预览版 |
| `article_notes/` | 长材料 / 噪声转写的中间笔记（按需） |

## 特性

- **两轮结构化提问**：第一轮收集素材路径、模板、配色、编辑、主题；第二轮盘点后确认日期、主持人、图片、封面
- **9 种模板 × 7 种配色**：`classic`、`notebook`、`journal`、`campus`、`minimal`、`magazine`、`warm-note`、`briefing`、`fieldnote`，搭配 `classic`、`forest`、`blueprint`、`warm`、`ink`、`sunrise`、`mono`
- **文献结构化**：研究背景、研究问题、方法与数据、核心发现、讨论价值、讨论摘录
- **ASR 发言人识别**：利用 PPT 分享人、英语交流顺序、交互模式等线索匹配发言人
- **日期推断优先级**：转录时间戳 > 用户提供 > PPT 元数据 > 文件名 > 文件修改时间
- **图片处理**：用途不明时主动询问用户，不假设、不跳过
- **品牌主题**：`zhengeryanzi` 静态 SVG 标记 + 结尾签名
- **质量检查**：自动检测 source 文件名泄露、文献字段缺失、英语发言过短、scaffold 误用等

## 仓库结构

```
SKILL.md                          # 主技能文档
agents/openai.yaml                # Codex 跨 agent 配置
assets/article-template.html      # 渲染器 HTML 模板
references/
  input-contract.md               # article.json 规范
  editorial-style.md              # 编辑风格指南
  material-extraction.md          # 素材提取 + ASR 策略
  wechat-formatting.md            # HTML/SVG 兼容性
  wechat-api.md                   # 微信 API（按需）
scripts/
  extract_materials.py            # 素材文本提取
  prepare_article_notes.py        # 中间笔记生成
  render_wechat_article.py        # HTML 渲染
  check_article_json.py           # 质量检查
  write_article_json.py           # Python dict → JSON
  update_article_gate.py          # 元数据补丁
  draft_article_from_materials.py # scaffold 辅助（可选）
tests/
  test_skill_scripts.py           # 单元测试
```

## 安装

### Codex

```
Use $skill-installer to install TTxiaohuang/wechat-meeting-article-skill path skills/wechat-meeting-article
```

### Claude Code / 手动安装

```bash
git clone https://github.com/TTxiaohuang/wechat-meeting-article-skill.git
```

把 `SKILL.md`、`references/`、`scripts/`、`assets/`、`agents/` 复制到 Agent 的 skills 目录：

- Claude Code: `~/.claude/skills/wechat-meeting-article/`
- Codex: `~/.codex/skills/wechat-meeting-article/`

### 安装可选依赖

```bash
python -m pip install python-docx python-pptx pdfplumber pypdf
```

Windows 中文环境建议设置：

```powershell
$env:PYTHONIOENCODING="utf-8"
```

## 使用方式

### 在 Agent 中使用

告诉 Agent：

```
请读取 wechat-meeting-article 技能，帮我把组会材料生成微信公众号推文。
```

Agent 会按照 SKILL.md 的两轮提问流程引导你完成。

### 命令行手动执行

```bash
# 1. 提取材料
python scripts/extract_materials.py D:\推文素材 --out extracted_materials

# 2. 生成笔记（可选，长材料时推荐）
python scripts/prepare_article_notes.py extracted_materials --out article_notes

# 3. 写 article.json（由 Agent 或手动完成）

# 4. 渲染 HTML
python scripts/render_wechat_article.py article.json --out dist

# 5. 质量检查
python scripts/check_article_json.py article.json --html dist/article.wechat.html
```

### 导入微信公众号

1. 浏览器打开 `dist/article.preview.html`
2. 选中渲染后的正文，复制富文本
3. 粘贴到微信公众号后台编辑器
4. 手机预览后发布

也可以导入 doocs/md、135 编辑器、秀米等支持 HTML 的排版工具。

## 内容原则

- 英语发言默认保留完整原文
- 文献分享写成结构化阅读笔记，不是几句摘要
- 讨论观点保留学生和老师的差异，不合并成模糊总结
- 录音转文字视为 noisy transcript，公开事实交叉核对
- 没有时政交流等环节时直接省略，不硬凑
- `source` 文件名仅内部核对，不出现在正文

## 测试

```bash
python -m unittest discover -s tests -v
```

## 注意事项

- 不要提交微信公众号凭据（appid、secret、token）
- 不要提交未公开的录音、转录稿、内部 PPT 或私人材料
- 默认只生成 HTML 草稿，自动发布需明确人工确认
