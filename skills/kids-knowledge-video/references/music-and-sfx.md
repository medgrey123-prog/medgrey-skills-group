# 配乐、音效与混音

目标：听起来像「真的乐器 + 真的音效」，而不是代码合成器。音乐托住情绪，音效咬住画面动作，旁白始终最清楚。

## 1. 配乐：MusicGen（已跑通）

本流程使用 Meta **MusicGen-small**（`facebook/musicgen-small`），经 Hugging Face `transformers` 在 **CPU** 上推理。

成片用过的参数：

| 参数 | 取值 | 说明 |
|---|---|---|
| 模型 | facebook/musicgen-small | 权重大约几百 MB，可缓存 |
| guidance_scale | 3 | 过高会死板，过低容易跑题 |
| 时长 | 35–36 秒 | `max_new_tokens ≈ 秒数 × 50`，混音时再截到成片长度 |
| 采样率 | 模型输出 32 kHz 单声道 | mix.py 会重采样到 48 kHz 立体声 |
| 归一 | 峰值 0.9 | 混音阶段再按 RMS 对齐 |

CPU 上生成约 36 秒，大概 90–120 秒。可以先出 2–3 个 seed，用 `scripts/tag_music.py` 抽查后再入混音。

### 提示词怎么写

用英文，写清：给谁听、什么情绪、哪些乐器、速度、不要什么。一定要写 **no drums**，儿童知识片不需要鼓点抢旁白。

科学 / 光之剧场（成片 seed=3，采用）：

```
gentle cinematic ambient for a children's science film, soft felt piano, warm strings, celesta and glockenspiel sparkle, harp, sense of wonder, 84 bpm, no drums, high quality orchestral recording
```

AST 抽查结果倾向：钟琴 / 马林巴 / 新世纪；未检出鼓、人声、合成器。

情绪 / 水彩绘本（成片 seed=2，采用）：

```
gentle warm children's picture book music, soft felt piano, fingerpicked acoustic guitar and ukulele, light warm strings, calm and tender, lullaby, 76 bpm, no drums, intimate high quality acoustic recording
```

AST 抽查结果倾向：温柔、竖琴 / 吉他；seed=1 偏亮偏硬（钟琴 / 马林巴），没有采用。换 seed 比猛改提示词往往更有效。

写作习惯：

- 先定情绪词（wonder / tender / lullaby），再列 3–5 种真实乐器。
- 科学可以稍亮（钢片琴、竖琴刮奏）；情绪课要更暖、更近（毡面钢琴、尼龙吉他、尤克里里）。
- 不要写电子舞曲、trap、epiano 独奏、人声哼唱。
- 生成后听全曲：有没有突然的鼓、人声、电流噪声。有就换 seed。

### 许可（重要）

MusicGen 的**推理代码是 MIT**，**模型权重是 CC-BY-NC 4.0**。用它生成的配乐按非商用处理，不能直接放进要上架的 App。用户若确认只做内部测试、不商用，可以先用。

### 商用替代：ACE-Step 1.5

[ACE-Step 1.5](https://github.com/ace-step/ACE-Step) 的许可是 **Apache-2.0**，更适合将来商用。本机用 `acestep.cpp` 在 CPU 上大约 2 分钟一首，曾经跑通，但按需求没有采用。商用前用它（或其它有商用授权的模型）替换 `scripts/musicgen.py` 即可，后面的混音参数不用改。

## 2. 音效：Freesound CC0，对齐画面事件

音效必须是录来的真实声音（翻页、风铃、谁嗖、铅笔、心跳），不要用振荡器临时做。本流程只搜索 **Creative Commons 0**。

搜索和下载需要环境变量 `FREESOUND_API_KEY`（<https://freesound.org/apiv2/apply/>）。**不要把密钥写进脚本、仓库或文档。**

`sfx_plan.json` 一条是一次播放：

```json
{"id": "419594", "name": "开场风铃（叶子亮起）", "event": 0.80, "align": "peak", "gain": -15}
```

| 字段 | 含义 |
|---|---|
| id | Freesound 数字 id |
| name | 给自己看的用途说明 |
| event | 画面事件的时间（秒），通常取 `timings.json` 里对应 cue，或略提前一点让声音「撞上」动作 |
| align | `peak`：把音效波形最响的地方对到 event；`start`：从 event 起播（刮奏、持续声更合适） |
| gain | 峰值归一后的增益，常见 -11 到 -24 dB，宁可不抢旁白 |
| dur | 可选，截取秒数（心跳、环境火声） |
| env | 可选，用一条包络去乘音量（水彩成片里火苗底噪用了 `flame`） |

设计经验（来自两部成片）：

- **一个视觉动作配一个声音。** 彩虹展开可以同时有竖琴刮奏和闪光，但不要五条叠在同一秒。
- **转场用 whoosh 或风铃**，闪卡用同一条翻牌声，间隔约 0.5 秒。
- **持续声要压低，并尽量跟画面大小走**（火苗底噪 -22 dB，再乘包络）。
- **呼吸、心跳这类身体声音要谨慎。** 水彩版用过一条成人女声的呼吸，听感偏位，以后应换儿童或更中性的吸气声，或干脆不用。
- 选素材时看波形：攻击短的用 `peak` 对齐；本身是扫弦、涨起的用 `start`。

两份已用过的计划在 `examples/sfx_plan.photosynthesis.json` 和 `examples/sfx_plan.anger.json`，可当分类参考，不要原样复用到新题材（时间轴会对不上）。

下载的是官方 **HQ 预览 mp3**，不是原文件。对 CC0 预览用于测试通常没问题；正式发行仍以该条页面上的许可为准，并用 `scripts/make_sources.py` 写出 `AUDIO_SOURCES.md`。

## 3. 混音链（两部成片的实际参数）

`scripts/mix.py` 按下面的顺序工作，采样率 48 kHz，立体声：

1. **旁白** 放在时间 0 起的时间线上，增益 **-3 dB**。
2. **配乐** 先按 RMS 归一到 **-20 dBFS**，再乘淡入淡出和闪避包络。
3. **闪避**：根据旁白是否在说话做包络。帧长 10 ms（hop 480）。攻击系数 0.25、释放系数 0.03，约等于 **起 80 ms / 释 350 ms**。有人声时配乐再压 **10 dB**。
4. **淡入 1.2 s、淡出 1.6 s**，避免头尾劈空。
5. **音效**：每条先峰值归一，再按 `align` 放到 `event`，尾部 0.4 s 淡出，然后加 `gain`。
6. 三路相加，得到 `mix_pre.wav`（同时会写出未闪避的 `music_only.wav` 和 `sfx_only.wav`，方便单独听）。
7. **两遍 loudnorm**：目标 **Integrated -14 LUFS**、**True peak -1.5 dBTP**（`scripts/encode.py loudnorm`）。科学成片复测约为 -14.0 LUFS、LRA 3.6 LU；情绪成片约为 -14.0 LUFS、LRA 1.6 LU，没有削波。

旁白必须始终是前景。如果某条音效盖过人声，先把这条的 gain 降 4–6 dB，而不是再压配乐。

## 4. 建议的听审顺序

1. 独唱旁白，看时长和吐字。
2. 只听配乐，确认没有鼓、人声、破音。
3. 只听音效轨，看事件是否都打在动作上。
4. 听预混，再听 loudnorm 之后的成片。
