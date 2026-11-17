#!/usr/bin/env python3
"""把帧序列压成 H.264 yuv420p，两遍 loudnorm 到 -14 LUFS，再和音频合成。

子命令：
  encode.py video  --frames DIR --fps 30 --out video_noaudio.mp4
  encode.py loudnorm --input mix_pre.wav --out mix_final.wav
  encode.py mux --video video_noaudio.mp4 --audio mix_final.wav --out film.mp4 [--duration 31.5]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    print("+", " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def cmd_video(args: argparse.Namespace) -> int:
    frames = args.frames.resolve()
    # accept f00000.png
    pattern = str(frames / "f%05d.png")
    first = frames / "f00000.png"
    if not first.exists():
        pngs = sorted(frames.glob("f*.png"))
        if not pngs:
            print(f"{frames} 里没有 fXXXXX.png", file=sys.stderr)
            return 2
        print("警告：缺少 f00000.png，ffmpeg 可能无法按序号开编", file=sys.stderr)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-framerate", str(args.fps),
        "-i", pattern,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", args.preset,
        "-crf", str(args.crf),
        "-movflags", "+faststart",
        str(args.out),
    ]
    subprocess.run(cmd, check=True)
    print("wrote", args.out)
    return 0


def loudnorm_measure(path: Path, i: float, tp: float, lra: float) -> dict:
    cmd = [
        "ffmpeg", "-hide_banner", "-i", str(path),
        "-af", f"loudnorm=I={i}:TP={tp}:LRA={lra}:print_format=json",
        "-f", "null", "-",
    ]
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    text = proc.stderr
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        print(text, file=sys.stderr)
        raise SystemExit("loudnorm 没有输出 JSON")
    return json.loads(m.group(0))


def cmd_loudnorm(args: argparse.Namespace) -> int:
    meas = loudnorm_measure(args.input, args.i, args.tp, args.lra)
    print("measured", {k: meas.get(k) for k in ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")})
    filt = (
        f"loudnorm=I={args.i}:TP={args.tp}:LRA={args.lra}"
        f":measured_I={meas['input_i']}:measured_TP={meas['input_tp']}"
        f":measured_LRA={meas['input_lra']}:measured_thresh={meas['input_thresh']}"
        f":offset={meas['target_offset']}:linear=true:print_format=summary"
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(args.input), "-af", filt, str(args.out)],
        check=True,
    )
    print("wrote", args.out)
    return 0


def cmd_mux(args: argparse.Namespace) -> int:
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(args.video),
        "-i", str(args.audio),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", args.audio_bitrate, "-ac", "2", "-ar", "48000",
        "-movflags", "+faststart",
    ]
    if args.duration:
        cmd += ["-t", str(args.duration)]
    else:
        cmd += ["-shortest"]
    cmd.append(str(args.out))
    subprocess.run(cmd, check=True)
    print("wrote", args.out)
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="视频编码 / 响度归一 / 合成")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("video", help="帧序列 → H.264 yuv420p")
    v.add_argument("--frames", type=Path, required=True)
    v.add_argument("--fps", type=int, default=30)
    v.add_argument("--crf", type=int, default=18)
    v.add_argument("--preset", default="medium")
    v.add_argument("--out", type=Path, required=True)
    v.set_defaults(func=cmd_video)

    l = sub.add_parser("loudnorm", help="两遍 loudnorm 到 -14 LUFS")
    l.add_argument("--input", type=Path, required=True)
    l.add_argument("--out", type=Path, required=True)
    l.add_argument("--i", type=float, default=-14.0)
    l.add_argument("--tp", type=float, default=-1.5)
    l.add_argument("--lra", type=float, default=11.0)
    l.set_defaults(func=cmd_loudnorm)

    m = sub.add_parser("mux", help="无声音视频 + 混音 → 成片")
    m.add_argument("--video", type=Path, required=True)
    m.add_argument("--audio", type=Path, required=True)
    m.add_argument("--out", type=Path, required=True)
    m.add_argument("--duration", type=float, default=None)
    m.add_argument("--audio-bitrate", default="192k")
    m.set_defaults(func=cmd_mux)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
