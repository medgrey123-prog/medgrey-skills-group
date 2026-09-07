# Book to Decision｜工具书蒸馏与决策准备

把实用类书籍变成 AI 可反复调用的判断材料：什么时候用、何时不能用、怎么执行、有什么替代和风险。最终由人决定。

## 一句话使用

安装到支持 Skills 的 Agent 后：

> 使用 book-to-decision，把这本工具书蒸馏成可长期调用的决策知识库。

调用已有知识库：

> 使用 book-to-decision，根据 decision-kb 分析这个问题，比较候选方法和适用边界，供我决定：……

任何能读取本地文件并遵循指令的 Agent，可用显式入口：

> 读取本地 book-to-decision/SKILL.md 及它要求的参考文件，将我提供的书籍蒸馏到 decision-kb。

请将相对路径替换成你的实际路径。不支持文件读取的聊天工具，需要上传或粘贴 SKILL.md 及对应 references 内容；它不会凭名称自动获得技能。

## 本地部署

整个 `book-to-decision` 文件夹就是技能包，保持内部结构不变。

- 支持 Skills 的 Agent：将整个文件夹放入该 Agent 文档指定的技能目录，或使用它的导入功能。
- 其他可读文件的 Agent：放在任意可读目录，用上面的显式入口调用。
- 核心为 UTF-8 Markdown，无 Python、Node、Shell、Docker、API Key 或数据库依赖。
- Windows、macOS、Linux 及其他能读 UTF-8 文本的环境均可承载核心文件。是否支持自动发现、文件工具、PDF/OCR，取决于宿主 Agent。并未对所有操作系统及所有 Agent 做实机测试。

本地部署指技能和知识文件可本地保存；使用云端模型仍可能将输入发送给模型服务。纯离线处理需要本地模型和本地解析能力。

## 上传 GitHub

可直接把本文件夹的内容作为一个仓库的根目录；或放进现有多技能仓库的 `skills/book-to-decision/`。保持 SKILL.md 和 references 的相对关系。

使用 GitHub 网页创建仓库并上传这些文件即可。命令行用户在该文件夹打开终端，已安装 Git 且已设置身份后逐条执行：

```sh
git init
git add SKILL.md README.md LICENSE agents references
git commit -m "Add book-to-decision skill"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

`YOUR_GITHUB_REPOSITORY_URL` 替换成你创建的仓库地址。若目录已有 Git 仓库或 origin，沿用现有配置，不重复初始化或添加远端。这里仅提供发布步骤，未替你建立或发布 GitHub 仓库。

## 产物与边界

输出在独立的 `decision-kb/`，包括检索索引、知识单元、来源覆盖和处理进度，必要时增加概念词典、跨书冲突表。不要把私人知识库或书籍原文混入公开技能仓库。

需要提供可读书籍内容。只有书名不能完成忠实蒸馏。扫描件与复杂文件需要 Agent 的解析能力。写出知识库不等于宿主已配置自动长期记忆；未来调用时仍需给出目录或配置宿主检索入口。

技能的核心不是“原则/立场/概念/方法论”的平铺摘要。这四者嵌入情境和条件：原则约束判断，立场体现取舍，概念帮助辨析，方法包含操作和失效信号。证据与反例可缺，但必须诚实标注。

## 授权

本技能原创文件采用 MIT License，可使用、修改、再分发。书籍原文及蒸馏时输入的其他材料不在此授权范围内。
