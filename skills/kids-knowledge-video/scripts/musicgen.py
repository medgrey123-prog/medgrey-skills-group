#!/usr/bin/env python3
"""用 Meta MusicGen-small 生成配乐（CPU 可跑）。

注意：facebook/musicgen-small 的模型权重是 CC-BY-NC 4.0，生成内容按非商用处理。
商用请改用 ACE-Step 1.5（Apache-2.0）或其他有商用授权的模型，见 references/music-and-sfx.md。

用法：
  musicgen.py --prompt "gentle cinematic ambient..." --seed 3 --seconds 36 --out music.wav
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import scipy.io.wavfile as wavfile
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="MusicGen 生成配乐")
    p.add_argument("--prompt", required=True, help="英文提示词，描述乐器、情绪、速度")
    p.add_argument("--seed", type=int, default=3)
    p.add_argument("--seconds", type=float, default=36, help="目标时长（按 50 token/秒估算）")
    p.add_argument("--guidance", type=float, default=3.0, help="classifier-free guidance")
    p.add_argument("--model", default="facebook/musicgen-small")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--threads", type=int, default=0, help="PyTorch CPU 线程，0 表示默认")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.threads > 0:
        torch.set_num_threads(args.threads)
    torch.manual_seed(args.seed)
    processor = AutoProcessor.from_pretrained(args.model)
    model = MusicgenForConditionalGeneration.from_pretrained(args.model)
    inputs = processor(text=[args.prompt], padding=True, return_tensors="pt")
    tokens = max(50, int(args.seconds * 50))
    t0 = time.time()
    audio = model.generate(**inputs, do_sample=True, guidance_scale=args.guidance, max_new_tokens=tokens)
    sr = model.config.audio_encoder.sampling_rate
    y = audio[0, 0].cpu().numpy()
    y = y / (np.abs(y).max() + 1e-9) * 0.9
    args.out.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(str(args.out), sr, (y * 32767).astype(np.int16))
    print(f"wrote {args.out}  sr={sr}  dur={len(y)/sr:.2f}s  elapsed={time.time()-t0:.1f}s  seed={args.seed}")
    print("license: model weights CC-BY-NC 4.0 — do not use commercially")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
