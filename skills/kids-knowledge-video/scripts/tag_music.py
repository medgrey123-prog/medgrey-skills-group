#!/usr/bin/env python3
"""用 MIT AST AudioSet 分类器抽查配乐：应听到目标乐器，不应出现鼓、人声、电子合成器。

用法：
  tag_music.py music.wav [more.wav...]
"""
from __future__ import annotations

import argparse
import subprocess
import sys

import numpy as np
import torch
from transformers import ASTFeatureExtractor, ASTForAudioClassification

WANT = [
    "Piano", "Strings", "String section", "Violin, fiddle", "Cello", "Orchestra",
    "Harp", "Glockenspiel", "Bell", "Chime", "Synthesizer", "Drum", "Drum kit",
    "Percussion", "Singing", "Speech", "Choir", "Electronic music", "Ambient music",
    "Classical music", "Music for children", "Guitar", "Electric piano", "New-age music",
    "Tender music", "Zither",
]
WARN = {"Synthesizer", "Drum", "Drum kit", "Percussion", "Singing", "Speech", "Choir", "Electronic music"}


def load_16k(path: str) -> np.ndarray:
    raw = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
        capture_output=True,
        check=True,
    ).stdout
    return np.frombuffer(raw, np.float32)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("files", nargs="+")
    args = p.parse_args()
    name = "MIT/ast-finetuned-audioset-10-10-0.4593"
    fe = ASTFeatureExtractor.from_pretrained(name)
    model = ASTForAudioClassification.from_pretrained(name).eval()
    lab = model.config.id2label
    idx = {l: [k for k, v in lab.items() if v == l][0] for l in WANT if l in lab.values()}
    for f in args.files:
        x = load_16k(f)
        print("==", f)
        for s in range(0, int(len(x) / 16000) - 5, 10):
            seg = x[s * 16000 : (s + 10) * 16000]
            with torch.no_grad():
                prob = torch.sigmoid(model(**fe(seg, sampling_rate=16000, return_tensors="pt")).logits)[0]
            top = torch.topk(prob, 6)
            t = ", ".join(f"{lab[int(i)]}:{float(v):.2f}" for v, i in zip(top.values, top.indices))
            sel = " | ".join(f"{l}:{float(prob[i]):.2f}" for l, i in idx.items() if float(prob[i]) > 0.08)
            warn = [l for l in WARN if l in idx and float(prob[idx[l]]) > 0.15]
            print(f" {s:2d}-{s+10}s TOP {t}")
            print(f"         SEL {sel}")
            if warn:
                print(f"         WARN {warn}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
