#!/usr/bin/env python3
"""把某个风格模板拷到新的工作目录，准备开始做一集。

用法：
  init_project.py --skill-root . --style cinematic-light --out ./work/leaf \\
                  --narration examples/narration.photosynthesis.json
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

STYLES = {
    "cinematic-light": "templates/cinematic-light",
    "watercolor-book": "templates/watercolor-book",
}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--skill-root", type=Path, required=True, help="本 skill 仓库根目录")
    p.add_argument("--style", required=True, choices=sorted(STYLES))
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--narration", type=Path, default=None, help="可选，拷到 out/L/narration.json")
    args = p.parse_args()
    src = (args.skill_root / STYLES[args.style]).resolve()
    if not src.exists():
        print(f"找不到模板 {src}", file=sys.stderr)
        return 2
    dest = args.out.resolve()
    if dest.exists() and any(dest.iterdir()):
        print(f"{dest} 已存在且非空，拒绝覆盖", file=sys.stderr)
        return 2
    shutil.copytree(src, dest, dirs_exist_ok=True)
    lesson = dest / "L"
    lesson.mkdir(exist_ok=True)
    if args.narration:
        shutil.copy2(args.narration, lesson / "narration.json")
    print("created", dest)
    print("下一步：改 film.html 里的 LESSON 文案和绘制逻辑，写 L/narration.json，再跑旁白和单帧确认。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
