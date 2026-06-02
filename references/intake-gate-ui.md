# Intake Gate UI Constraints

`AskUserQuestion` 每个问题最多显示 4 个选项按钮。当选项超过 4 个时，常用选项放按钮，全部选项清单写在第 4 个按钮的 `description` 中。

**所有 label 必须用中文。** 英文名仅用于写入 `article.json` 的值。

## Template Selection

### Round 1（3 buttons + "更多模板"）

- question: "选择文章模板"
- options:
  1. `{label: "经典简洁", description: "默认简洁风格"}`
  2. `{label: "笔记风格", description: "左侧色条+柔和背景"}`
  3. `{label: "校园清新", description: "明亮校园风格"}`
  4. `{label: "更多模板", description: "还有：编辑排版、报告风格"}`
- header: "模板"

### Round 2（用户选"更多模板"后触发，3 buttons）

- question: "选择更多模板"
- options:
  1. `{label: "编辑排版", description: "更强的开头节奏与编辑版式"}`
  2. `{label: "报告风格", description: "类报告风格，分隔线与编号标签更突出"}`
  3. `{label: "经典简洁", description: "回到默认简洁风格"}`
- header: "更多模板"

Round 2 展示 Round 1 未显示的选项，同时提供一个回退选项让用户可以选回 Round 1 的常用项。

### Label 到 article.json 值映射

| 中文 label | article.json 值 |
|-----------|----------------|
| 经典简洁 | classic |
| 笔记风格 | notebook |
| 校园清新 | campus |
| 编辑排版 | magazine |
| 报告风格 | briefing |

## Palette Selection

### Round 1（3 buttons + "更多配色"）

- question: "选择配色方案"
- options:
  1. `{label: "森林绿", description: "学术绿+柔和米色"}`
  2. `{label: "蓝图蓝", description: "蓝色报告色调"}`
  3. `{label: "樱花粉", description: "樱花粉+暖白"}`
  4. `{label: "更多配色", description: "还有：经典蓝、暖棕绿、灰黑学术、珊瑚暖绿、近单色、深海蓝"}`
- header: "配色"

### Round 2（用户选"更多配色"后触发，3 buttons）

- question: "选择更多配色"
- options:
  1. `{label: "经典蓝", description: "柔和蓝色+暖色注记"}`
  2. `{label: "暖棕绿", description: "克制的棕绿色读书笔记色调"}`
  3. `{label: "灰黑学术", description: "灰黑色学术风格"}`
- header: "更多配色"

### Round 3（用户再次选"更多"时触发，3 buttons）

- question: "更多配色方案"
- options:
  1. `{label: "珊瑚暖绿", description: "暖珊瑚+绿色，适合清新校园推文"}`
  2. `{label: "近单色", description: "接近单色的极简色调"}`
  3. `{label: "深海蓝", description: "深海蓝+浅青色"}`
- header: "更多配色"

每轮展示上一轮未显示的选项，末尾选项可作为"返回"让用户选回前面的常用项。

### Label 到 article.json 值映射

| 中文 label | article.json 值 |
|-----------|----------------|
| 森林绿 | forest |
| 蓝图蓝 | blueprint |
| 樱花粉 | sakura |
| 经典蓝 | classic |
| 暖棕绿 | warm |
| 灰黑学术 | ink |
| 珊瑚暖绿 | sunrise |
| 近单色 | mono |
| 深海蓝 | ocean |

## Round 1 Questions (before inspecting folder)

Split into separate questions (one per field), do not combine:

1. **素材文件夹路径** — 直接询问
2. **会议类型** — 3 选项：标准流程 / 有额外环节 / 完全不同的流程。这决定了后续用 `sections` 还是 `sessions`
3. **模板** — 按上述模板格式提问（选"更多"则触发第二轮）
4. **配色** — 按上述配色格式提问（选"更多"则触发第二轮、第三轮）
5. **编辑** — 2 选项: 提供名字 / 留空

## Round 2 Questions (after inventory)

1. **环节确认**（仅当 Round 1 选了"有额外环节"或"完全不同的流程"时）：请用户列出具体环节和顺序
2. **日期/主持人**: 从素材推断，有歧义时确认
3. **图片**: 列出每个图片文件，问用户是什么、放哪里。**不要尝试自己识别图片内容，必须问用户。**
4. **可选插页**: 喜讯、通知、里程碑 — 确认是否收录
