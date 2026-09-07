# medgrey-skills-group

可复用的 AI Agent 技能合集。每个技能独立安装，核心使用 Markdown，不绑定特定操作系统。

## 技能目录

| 技能 | 用途 | 入口 |
|---|---|---|
| book-to-decision | 工具书蒸馏、长期决策知识库、候选方法与适用边界比较 | [使用说明](skills/book-to-decision/README.md) · [技能入口](skills/book-to-decision/SKILL.md) |

## 使用方法

下载本仓库，将所需的单个技能文件夹放入你的 Agent 支持的技能目录，保持内部文件结构。具体安装位置和自动发现方式以宿主 Agent 为准。

支持原生 Skills 的 Agent：

> 使用 book-to-decision，把这本工具书蒸馏为可长期调用的决策知识库。

其他具备文件读取能力的 Agent：

> 读取本地 skills/book-to-decision/SKILL.md 及它要求的参考文件，按流程处理我提供的书籍。

不具备文件读取能力的聊天工具，需要上传或粘贴技能及所需参考文件。纯文本核心可跨系统使用；PDF、OCR、自动检索与离线运行取决于宿主能力，不承诺所有 Agent 均原生兼容。

## 贡献新技能

每个技能放在 `skills/<skill-name>/`，以 `SKILL.md` 为入口。说明触发场景、输入、输出、适用边界及依赖，提供必要参考文件；避免包含个人隐私、账号凭据和书籍原文。

## 授权

本仓库原创技能文件使用 [MIT License](LICENSE)。用户输入的书籍和其他第三方材料不包含在此授权中。
