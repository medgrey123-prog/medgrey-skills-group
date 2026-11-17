---
name: kids-knowledge-video
description: 把一个儿童知识点做成约 30 秒竖屏知识短视频（1080×1920）。先理解内容并写分镜，再做风格单帧确认，然后用确定性 HTML/Canvas 动画渲染，并配上旁白、AI 真乐器配乐和与画面同步的真实音效。适合大班到六年级的科学或情绪/社交主题，以及需要批量生成「刷着学」视频卡的场景。
---

# 儿童知识短视频流程

把一个知识点做成约 30 秒、1080×1920 竖屏的「刷着学」短视频。核心有两块：

1. **对内容的理解**：把知识点写成孩子听得懂的旁白和分镜，而不是把课文念出来。
2. **配乐与音效**：用 AI 生成真乐器感的配乐，再把真实音效对齐到画面事件，和旁白一起混音。

画面用确定性的 HTML/Canvas 动画（`window.render(t)`），Playwright 逐帧截取，ffmpeg 压成 H.264 yuv420p。不要用 Remotion 或 FFmpeg 模板拼片。

完整方法见 `references/`。本文件只写调用顺序。

## 适用与限制

- 年龄：大班到六年级。
- 时长：旁白加片尾闪卡，目标约 30 秒。宁可少讲一句，也不要塞两个知识点。
- 已确认可直接用的风格：**科学用「光之剧场」**，**情绪用「水彩绘本」**。换风格必须先出单帧给用户看，再渲染成片。
- 家庭隐私资料不要写进任何云端记忆库。

## 输入

用户给一个知识点即可。写成 JSON 更稳，示例见 `examples/knowledge-point.*.json`：

```json
{
  "title": "叶子为什么是绿的",
  "category": "science",
  "age": "大班-六年级",
  "core_idea": "叶子看起来是绿色，是因为绿光被弹回眼睛",
  "style": "cinematic-light"
}
```

`style` 可选 `cinematic-light`（光之剧场）或 `watercolor-book`（水彩绘本）。不确定就先出风格单帧。

## 步骤

### 1. 理解内容，写旁白和分镜

按 `references/content-understanding.md` 写，不要跳过：

- 只保留一个核心观念。
- 开头 3 秒用问句钩住。
- 用具体比喻，不堆术语。
- 科学：提问 → 机制 → 所以才这样。情绪：先接纳感受，再给三步办法，不要责备。
- 结尾三张闪卡复习。
- 旁白写成 `L/narration.json`。需要和画面对齐的瞬间，用 `[[cue]]` 标在词前面，例如 `[[green]]绿色`。

仓库里有两份已拍过的完整文案：`examples/narration.photosynthesis.json`、`examples/narration.anger.json`。

### 2. 风格先确认（先单帧，后成片）

从 `templates/style-frames/` 选一张风格页，或直接改工作模板里的 `LESSON` 文案后截关键帧：

```bash
python scripts/shoot.py --root templates/style-frames --html science-cinematic-light.html \
  frame --time 4.6 --out /tmp/style.png
```

把单帧给用户看。没点头之前，不要跑完整 30 秒。

### 3. 建立工作目录，写动画

```bash
python scripts/init_project.py --skill-root . --style cinematic-light --out ./work/leaf \
  --narration examples/narration.photosynthesis.json
```

模板里的 `film.html` 是可运行的参数化成片（光之剧场=光合作用，水彩绘本=生气怎么办）。换新知识点时：

- 先改文件顶部的 `LESSON`（标题、闪卡、总结句）。
- 再改绘制逻辑。风格规则（光、颗粒、水彩晕染、构图）留着，比喻对应的图形要重画。
- 必须导出 `window.render(t)`，画布 id 为 `c`，尺寸 1080×1920。时间要跟着 `L/build/timings.json` 里的 `cues` 走。

### 4. 旁白

默认音色 `zh-CN-XiaoxiaoNeural`（比 Xiaoyi 更温柔）。需要联网。

```bash
python scripts/tts_edge.py ./work/leaf/L --lead 0.3 --gap 0.25
```

得到 `L/build/narration.wav` 和 `L/build/timings.json`。用总时长决定画面和混音长度；片尾闪卡大约再留 4–5 秒。

### 5. 渲染画面

先截 4–6 张关键帧检查，再出全片帧：

```bash
python scripts/shoot.py --root ./work/leaf --html film.html stills \
  --times 1.0 5.5 12.0 16.4 20.2 27.5 --out ./work/leaf/stills

python scripts/shoot.py --root ./work/leaf --html film.html frames \
  --start 0 --end 945 --fps 30 --workers 2 --out ./work/leaf/frames

python scripts/encode.py video --frames ./work/leaf/frames --fps 30 --out ./work/leaf/video_noaudio.mp4
```

### 6. 配乐、音效、混音

方法与提示词见 `references/music-and-sfx.md`。

```bash
python scripts/musicgen.py --prompt "gentle cinematic ambient for a children's science film, soft felt piano, warm strings, celesta and glockenspiel sparkle, harp, sense of wonder, 84 bpm, no drums, high quality orchestral recording" \
  --seed 3 --seconds 36 --out ./work/leaf/music.wav

# 为每个画面事件选一条 CC0 音效，写入 sfx_plan.json（event 对 timings 的 cue）
# 需要环境变量 FREESOUND_API_KEY，不要写进仓库
python scripts/fs_search.py -q "wind chimes" -q "harp glissando" --out ./work/leaf/fs_candidates.json
python scripts/fs_download.py --plan ./work/leaf/sfx_plan.json --out-dir ./work/leaf/sfx_raw --meta ./work/leaf/sfx_meta.json

python scripts/mix.py --music ./work/leaf/music.wav --voice ./work/leaf/L/build/narration.wav \
  --plan ./work/leaf/sfx_plan.json --sfx-dir ./work/leaf/sfx_raw \
  --duration 31.5 --out-dir ./work/leaf/mix

python scripts/encode.py loudnorm --input ./work/leaf/mix/mix_pre.wav --out ./work/leaf/mix/mix_final.wav
python scripts/encode.py mux --video ./work/leaf/video_noaudio.mp4 --audio ./work/leaf/mix/mix_final.wav \
  --duration 31.5 --out ./work/leaf/film.mp4

python scripts/make_sources.py --title "叶子为什么是绿的" --style 光之剧场 \
  --music-file music.wav --music-prompt "..." --music-seed 3 \
  --plan ./work/leaf/sfx_plan.json --meta ./work/leaf/sfx_meta.json \
  --out ./work/leaf/AUDIO_SOURCES.md
```

MusicGen-small 是 **CC-BY-NC**，不能商用。商用配乐改用 ACE-Step 1.5（Apache-2.0）或其它有授权的模型。

### 7. 交付前检查

- 成片约 30 秒，竖屏 1080×1920，H.264 yuv420p，响度约 -14 LUFS。
- 口播和画面事件对齐（光撞上、火苗变小、闪卡翻开都要有音效）。
- 附上 `AUDIO_SOURCES.md`。
- 已知成片里不必重复的瑕疵：超时、人物只有一个正面姿势、画幅裁切、呼吸音效听着像成人，发现了要改，不要原样留下。

## 许可（必读）

| 部件 | 许可 | 注意 |
|---|---|---|
| 本仓库脚本和模板 | MIT | 见 `LICENSE` |
| MusicGen-small 权重 | CC-BY-NC 4.0 | 非商用；商用换模型 |
| edge-tts | 无明确商用授权 | 商用改 Azure TTS 等 |
| Freesound 音效 | 本流程只搜 CC0 | 发行前再核对该条许可 |
| 上游技能 | MIT | 致谢 xiazhuo123456789/vibe-knowledge-video、andyhuo520/vibe-knowledge，未整仓拷入 |

详细说明见 `references/licenses.md`。
