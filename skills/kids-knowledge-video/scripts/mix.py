#!/usr/bin/env python3
"""把旁白、配乐、音效混成一条预混音。

实测参数（两部成片共用）：
  采样率 48 kHz 立体声；旁白 -3 dB；配乐先按 RMS 归一到 -20 dBFS；
  有人声时配乐自动压低 10 dB（包络攻击系数 0.25 / 释放系数 0.03，约 80 ms / 350 ms）；
  配乐首淡入 1.2 s、尾淡出 1.6 s；音效按 event 对齐 start 或 peak，尾部 0.4 s 淡出。

用法：
  mix.py --music music.wav --voice L/build/narration.wav --plan sfx_plan.json \\
         --sfx-dir sfx_raw --duration 31.5 --out-dir ./mix
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf


def db(g: float) -> float:
    return 10 ** (g / 20)


def load(path: Path, ch: int, sr: int) -> np.ndarray:
    raw = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-i", str(path), "-f", "f32le", "-ac", str(ch), "-ar", str(sr), "-"],
        capture_output=True,
        check=True,
    ).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()


def duck_envelope(voice: np.ndarray, sr: int, hop: int = 480, attack_k: float = 0.25, release_k: float = 0.03, thresh: float = 0.02) -> np.ndarray:
    """voice activity → 0..1 envelope. hop=480 @ 48 kHz = 10 ms。"""
    n = len(voice)
    a = np.abs(voice)
    usable = len(a) // hop * hop
    fr = a[:usable].reshape(-1, hop).max(1)
    act = (fr > thresh).astype(float)
    env = np.zeros_like(act)
    e = 0.0
    for i, x in enumerate(act):
        k = attack_k if x > e else release_k
        e += (x - e) * k
        env[i] = e
    env = np.repeat(env, hop)
    if len(env) < n:
        env = np.pad(env, (0, n - len(env)), mode="edge")
    return env[:n]


def main() -> int:
    p = argparse.ArgumentParser(description="旁白 + 配乐闪避 + 音效混音")
    p.add_argument("--music", type=Path, required=True)
    p.add_argument("--voice", type=Path, required=True)
    p.add_argument("--plan", type=Path, required=True, help="sfx_plan.json")
    p.add_argument("--sfx-dir", type=Path, required=True)
    p.add_argument("--duration", type=float, required=True, help="成片时长（秒）")
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--sr", type=int, default=48000)
    p.add_argument("--voice-gain", type=float, default=-3.0)
    p.add_argument("--music-rms", type=float, default=-20.0, help="配乐 RMS 目标 dBFS")
    p.add_argument("--duck-db", type=float, default=10.0, help="有人声时配乐压低的分贝")
    p.add_argument("--fade-in", type=float, default=1.2)
    p.add_argument("--fade-out", type=float, default=1.6)
    p.add_argument("--sfx-tail", type=float, default=0.4)
    p.add_argument("--env-json", type=Path, default=None, help="可选：给 env 字段用的包络 JSON（如火焰音量）")
    args = p.parse_args()

    sr, dur = args.sr, args.duration
    n = int(dur * sr)
    voice = load(args.voice, 1, sr)[:, 0]
    v = np.zeros(n, np.float32)
    v[: min(n, len(voice))] = voice[:n]

    m = load(args.music, 2, sr)
    mo = np.zeros((n, 2), np.float32)
    L = min(n, len(m))
    mo[:L] = m[:L]
    tt = np.arange(n) / sr
    fade = np.clip(tt / max(args.fade_in, 1e-6), 0, 1) * np.clip((dur - tt) / max(args.fade_out, 1e-6), 0, 1)
    env = duck_envelope(v, sr)
    rms = float(np.sqrt(np.mean(mo ** 2)) + 1e-9)
    mo = mo / rms * db(args.music_rms)
    duck = db(-args.duck_db * env)
    music = mo * (fade * duck)[:, None]

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    env_tables = {}
    if args.env_json and args.env_json.exists():
        # 约定：100 Hz 采样的 0..1 包络数组
        env_tables["default"] = np.array(json.loads(args.env_json.read_text(encoding="utf-8")), np.float32)

    sfx = np.zeros((n, 2), np.float32)
    cache = {}
    for item in plan:
        sid = str(item["id"])
        src = args.sfx_dir / f"fs{sid}.mp3"
        if not src.exists():
            # also accept exact filename if provided
            alt = args.sfx_dir / sid
            if alt.exists():
                src = alt
            else:
                print(f"缺少音效文件: {src}", file=sys.stderr)
                return 1
        if sid not in cache:
            x = load(src, 2, sr)
            pk = float(np.abs(x).max() + 1e-9)
            x = x / pk
            envl = np.abs(x).max(1)
            peak_i = int(np.argmax(np.convolve(envl, np.ones(1024) / 1024, "same")))
            cache[sid] = (x, peak_i)
        x, peak_i = cache[sid]
        x = x.copy()
        st = int(item["event"] * sr) - (peak_i if item.get("align") == "peak" else 0)
        if st < 0:
            x = x[-st:]
            st = 0
        x = x[: n - st].copy()
        if item.get("dur"):
            x = x[: int(float(item["dur"]) * sr)]
        if item.get("env"):
            # env 为 100 Hz 序列时，按时间对齐到本段
            table = env_tables.get(item["env"]) or env_tables.get("default")
            if table is not None:
                e = np.repeat(table, sr // 100)
                e = np.pad(e, (0, n), mode="edge")
                x = x * np.sqrt(e[st : st + len(x)])[:, None]
        fl = min(len(x), int(args.sfx_tail * sr))
        if fl > 0:
            x[-fl:] *= np.linspace(1, 0, fl)[:, None]
        sfx[st : st + len(x)] += x * db(float(item.get("gain", 0)))

    vo = np.stack([v, v], 1) * db(args.voice_gain)
    mix = vo + music + sfx
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    mf = mo * fade[:, None]
    sf.write(str(out / "music_only.wav"), mf / (np.abs(mf).max() + 1e-9) * db(-1), sr, subtype="PCM_24")
    sf.write(str(out / "sfx_only.wav"), sfx, sr, subtype="FLOAT")
    sf.write(str(out / "mix_pre.wav"), mix, sr, subtype="FLOAT")
    peaks = [round(20 * np.log10(float(np.abs(z).max()) + 1e-9), 1) for z in (vo, music, sfx, mix)]
    print("peaks voice/music/sfx/mix", peaks)
    print("wrote", out / "mix_pre.wav")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
