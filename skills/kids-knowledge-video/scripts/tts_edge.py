#!/usr/bin/env python3
"""edge-tts 配音 → timings.json（逐字时间 chars[]、[[cue]] 时间）+ narration.wav

用法：
  tts_edge.py <lesson_dir> [--lead 0.3] [--gap 0.25] [--voice zh-CN-XiaoxiaoNeural] [--rate -5%]

lesson_dir 下需要有 narration.json。输出写到 lesson_dir/build/。
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

import edge_tts
import numpy as np


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="用 edge-tts 生成旁白和逐字时间轴")
    p.add_argument("lesson_dir", type=Path, help="含 narration.json 的课时目录")
    p.add_argument("--lead", type=float, default=0.3, help="片头静音秒数")
    p.add_argument("--gap", type=float, default=0.25, help="句间默认停顿秒数（可被每句 gap 覆盖）")
    p.add_argument("--voice", default=None, help="覆盖 narration.json 里的音色")
    p.add_argument("--rate", default=None, help="覆盖语速，如 -5%")
    p.add_argument("--pitch", default=None, help="覆盖音高，如 +0Hz")
    return p.parse_args()


async def tts(text: str, mp3: Path, voice_id: str, rate: str, pitch: str):
    comm = edge_tts.Communicate(
        text, voice_id, rate=rate, pitch=pitch, boundary="WordBoundary"
    )
    words = []
    with open(mp3, "wb") as f:
        async for ch in comm.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append((ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7, ch["text"]))
    return words


def load_wav(mp3: Path, sr: int) -> np.ndarray:
    raw = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-i", str(mp3), "-f", "s16le", "-ac", "1", "-ar", str(sr), "-"],
        capture_output=True,
        check=True,
    ).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def main() -> int:
    args = parse_args()
    lesson = args.lesson_dir.resolve()
    src = lesson / "narration.json"
    if not src.exists():
        print(f"找不到 {src}", file=sys.stderr)
        return 2
    build = lesson / "build"
    (build / "audio").mkdir(parents=True, exist_ok=True)
    data = json.loads(src.read_text(encoding="utf-8"))
    voice = dict(data.get("voice") or {})
    if args.voice:
        voice["id"] = args.voice
    if args.rate:
        voice["rate"] = args.rate
    if args.pitch:
        voice["pitch"] = args.pitch
    voice.setdefault("engine", "edge-tts")
    voice.setdefault("id", "zh-CN-XiaoxiaoNeural")
    voice.setdefault("rate", "-5%")
    voice.setdefault("pitch", "+0Hz")

    sr = 48000
    lead, default_gap = args.lead, args.gap
    out, beats, t = [np.zeros(int(lead * sr), np.float32)], {}, lead

    for beat in data["beats"]:
        raw = beat["narration"]
        cues, text = {}, ""
        for part in re.split(r"(\[\[[a-z0-9_]+\]\])", raw):
            m = re.fullmatch(r"\[\[([a-z0-9_]+)\]\]", part)
            if m:
                cues[m.group(1)] = len(text)
            else:
                text += part
        mp3 = build / "audio" / f"{beat['id']}.mp3"
        words = asyncio.run(tts(text, mp3, voice["id"], voice.get("rate", "+0%"), voice.get("pitch", "+0Hz")))
        x = load_wav(mp3, sr)
        nz = np.where(np.abs(x) > 0.01)[0]
        if len(nz) == 0:
            a0, a1 = 0, len(x)
        else:
            a0 = max(0, nz[0] - int(0.03 * sr))
            a1 = min(len(x), nz[-1] + int(0.08 * sr))
        x = x[a0:a1]
        off = a0 / sr
        dur = len(x) / sr
        chars = [None] * len(text)
        pos = 0
        for ws, we, w in words:
            i = text.find(w, pos)
            if i < 0:
                continue
            for k in range(len(w)):
                chars[i + k] = t + max(0, ws - off) + (we - ws) * k / max(len(w), 1)
            pos = i + len(w)
        last = t
        for i in range(len(chars)):
            if chars[i] is None:
                chars[i] = last
            last = chars[i]
        beats[beat["id"]] = {
            "text": text,
            "start": round(float(t), 3),
            "end": round(float(t + dur), 3),
            "chars": [round(float(c), 3) for c in chars],
            "cues": {k: round(float(chars[min(v, len(chars) - 1)]), 3) for k, v in cues.items()},
            "words": [w for _, _, w in words],
        }
        gap = float(beat.get("gap", default_gap))
        out += [x, np.zeros(int(gap * sr), np.float32)]
        t += dur + gap

    y = np.concatenate(out)
    y = y / max(1e-6, float(np.abs(y).max())) * 0.89
    wav_path = build / "narration.wav"
    with wave.open(str(wav_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((y * 32767).astype(np.int16).tobytes())
    timings = {"voice": voice, "beats": beats, "total": round(t, 3)}
    (build / "timings.json").write_text(json.dumps(timings, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, v in beats.items():
        print(k, v["start"], v["end"], v["cues"], "/".join(v["words"]))
    print("total", round(t, 3))
    print("wrote", wav_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
