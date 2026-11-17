#!/usr/bin/env python3
"""根据混音用到的素材，生成 AUDIO_SOURCES.md 署名清单。

用法：
  make_sources.py --title "叶子为什么是绿的" --style 光之剧场 \\
    --narration-voice zh-CN-XiaoxiaoNeural --narration-rate -5% \\
    --music-file music_mg_3.wav --music-model facebook/musicgen-small \\
    --music-prompt "gentle cinematic..." --music-seed 3 --music-license CC-BY-NC \\
    --plan sfx_plan.json --meta sfx_meta.json --out AUDIO_SOURCES.md
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--title", required=True)
    p.add_argument("--style", required=True)
    p.add_argument("--file-name", default="", help="成片文件名，仅用于标题")
    p.add_argument("--narration-engine", default="edge-tts")
    p.add_argument("--narration-voice", default="zh-CN-XiaoxiaoNeural")
    p.add_argument("--narration-rate", default="-5%")
    p.add_argument("--music-file", default="")
    p.add_argument("--music-model", default="facebook/musicgen-small")
    p.add_argument("--music-prompt", default="")
    p.add_argument("--music-seed", default="")
    p.add_argument("--music-license", default="CC-BY-NC 4.0")
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--meta", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--commercial-note", action="store_true", default=True)
    args = p.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    meta = json.loads(args.meta.read_text(encoding="utf-8"))
    fn = f" ({args.file_name})" if args.file_name else ""
    lines = [
        f"# AUDIO_SOURCES — 《{args.title}》{args.style}版{fn}",
        "",
        "**请按实际用途填写商用声明。** 若配乐来自 MusicGen，模型权重为 CC-BY-NC 4.0，**不能用于商业产品**。edge-tts 没有明确的商用授权，商用应改用 Azure TTS 付费 API 或其他有授权的引擎。",
        "",
        "## 1. 旁白",
        f"- 引擎：{args.narration_engine}，音色 {args.narration_voice}，语速 {args.narration_rate}。",
        "- 文案：L/narration.json；逐字时间：L/build/timings.json。",
        "",
        "## 2. 配乐",
        f"- 文件：{args.music_file or '（填写生成文件名）'}",
        f"- 模型：{args.music_model}，seed={args.music_seed or '（填写）'}",
        f"- 提示词：{args.music_prompt or '（填写）'}",
        f"- 许可：{args.music_license}",
        "",
        "## 3. 音效（Freesound）",
        "来源：freesound.org。下表按 sfx_plan.json 列出。请核对该条许可确为 CC0 后再用于发行。",
        "",
        "| 时间点(s) | 用途 | Freesound ID | 标题 | 作者 | 增益 dB | 链接 |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in plan:
        sid = str(item["id"])
        info = meta.get(sid) or {}
        lines.append(
            f"| {item.get('event','')} | {item.get('name','')} | {sid} | "
            f"{info.get('title','')} | {info.get('user','')} | {item.get('gain','')} | {info.get('page','')} |"
        )
    lines += [
        "",
        "## 4. 混音",
        "- mix.py：旁白默认 -3 dB；配乐 RMS 归一到 -20 dBFS；有人声时自动压低 10 dB（攻击 / 释放约 80 ms / 350 ms），首尾淡入淡出；音效峰值或起点对齐到画面事件。",
        "- 最终响度：encode.py loudnorm 两遍，目标 Integrated -14 LUFS、True peak -1.5 dBTP。",
        "",
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
