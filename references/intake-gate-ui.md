# Intake Gate UI Constraints

`AskUserQuestion` 每个问题最多显示 4 个选项按钮。当选项超过 4 个时，常用选项放按钮，全部选项清单写在第 4 个按钮的 `description` 中。

## Template Selection (5 options, 3 buttons + "more")

- question: "选择文章模板"
- options:
  1. `{label: "经典简洁", description: "classic — 默认简洁风格"}`
  2. `{label: "笔记风格", description: "notebook — 左侧色条+柔和背景"}`
  3. `{label: "校园清新", description: "campus — 明亮校园风格"}`
  4. `{label: "更多模板", description: "可选: magazine(编辑排版), briefing(报告风格)。输入模板名称即可"}`
- header: "模板"

## Palette Selection (9 options, 3 buttons + "more")

- question: "选择配色方案"
- options:
  1. `{label: "森林绿", description: "forest — 学术绿+柔和米色"}`
  2. `{label: "蓝图蓝", description: "blueprint — 蓝色报告色调"}`
  3. `{label: "樱花粉", description: "sakura — 樱花粉+暖白"}`
  4. `{label: "更多配色", description: "可选: classic(经典蓝), warm(暖棕绿), ink(灰黑学术), sunrise(珊瑚暖绿), mono(近单色), ocean(深海蓝)。输入配色名称即可"}`
- header: "配色"

**关键：第4个选项的 description 必须列出所有剩余选项的名称和简短说明，这样用户就知道可以通过 "Other" 输入哪些值。不要只写"更多"两个字。**

## Round 1 Questions (before inspecting folder)

Split into separate questions (one per field), do not combine:

1. **素材文件夹路径** — 直接询问
2. **模板** — 按上述模板格式提问
3. **配色** — 按上述配色格式提问
4. **编辑** — 2 选项: 提供名字 / 留空

## Round 2 Questions (after inventory)

1. **日期/主持人**: 从素材推断，有歧义时确认
2. **图片**: 列出每个图片文件，问用户是什么、放哪里
3. **封面风格** — 3 选项: `无封面` / `PPT标题页` / `自选图片`
4. **可选插页**: 喜讯、通知、里程碑 — 确认是否收录
