# 许可说明

本仓库自己的脚本、模板和文档是 MIT，版权声明见根目录 `LICENSE`。

下面这些部件**不在** MIT 范围内，使用或发行前要单独判断。

## 配乐模型

- **MusicGen-small**（`facebook/musicgen-small`）：Hugging Face 上的模型权重为 **CC-BY-NC 4.0**。用它生成的音频按非商用处理，不能放入要收费或上架的产品。推理代码本身是 MIT，但这不能改变权重的非商用限制。
- **ACE-Step 1.5**：Apache-2.0，可作为商用配乐的替代，本仓库未打包该模型或推理代码。

## 旁白

- **edge-tts** 调用的是微软 Edge 在线朗读接口，没有给出明确的商用授权。内部试片可以用。商业产品请改用 Azure TTS 付费 API，或其他带商用授权的音色。

## 音效

- 搜索脚本默认加上 `license:"Creative Commons 0"`。CC0 通常可商用、无需署名，但**每一条都要在 Freesound 页面再看一次**再发行。
- 下载的是官方 HQ 预览 mp3。把使用过的条目写入 `AUDIO_SOURCES.md`（`scripts/make_sources.py`）。

## 字体

- 模板默认使用系统里常见的 Noto CJK、IBM Plex Mono（它们有自己的许可，一般需按 SIL OFL / 对应协议保留声明）。
- 水彩手写感可选用 LXGW WenKai（OFL）。字体文件不包含在本仓库中。

## 上游技能

「用代码写 `render(t)`，再用无头浏览器逐帧拍摄」的思路来自：

- [xiazhuo123456789/vibe-knowledge-video](https://github.com/xiazhuo123456789/vibe-knowledge-video)（MIT）
- [andyhuo520/vibe-knowledge](https://github.com/andyhuo520/vibe-knowledge)（MIT，Copyright Berryxia）

本仓库没有整仓拷贝它们的代码。若你在自己的衍生工作里复制了其中的实质部分，请保留对方的版权声明与 MIT 文本。他们的原始技能是横屏；本流程改成了 1080×1920 竖屏，并加上儿童内容方法和配乐混音链。
