#!/usr/bin/env python3
"""按 sfx_plan.json 下载 Freesound CC0 预览 mp3，并写出 sfx_meta.json。

需要 FREESOUND_API_KEY。下载的是官方 preview-hq-mp3，不是原文件。

用法：
  fs_download.py --plan sfx_plan.json --out-dir sfx_raw --meta sfx_meta.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

API_SOUND = "https://freesound.org/apiv2/sounds/{id}/"


def api_key() -> str:
    key = os.environ.get("FREESOUND_API_KEY", "").strip()
    if not key:
        print("请设置环境变量 FREESOUND_API_KEY。", file=sys.stderr)
        raise SystemExit(2)
    return key


def fetch_sound(sid: str, key: str) -> dict:
    req = urllib.request.Request(
        API_SOUND.format(id=sid) + "?fields=id,name,username,duration,num_downloads,previews,url,license",
        headers={"Authorization": f"Token {key}", "User-Agent": "kids-knowledge-video/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download(url: str, dest: Path, key: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        url, headers={"Authorization": f"Token {key}", "User-Agent": "kids-knowledge-video/1.0"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp, open(dest, "wb") as f:
        f.write(resp.read())


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--meta", type=Path, required=True)
    args = p.parse_args()
    key = api_key()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    ids = []
    for item in plan:
        sid = str(item["id"])
        if sid not in ids:
            ids.append(sid)
    meta = {}
    for sid in ids:
        info = fetch_sound(sid, key)
        previews = info.get("previews") or {}
        mp3 = previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3")
        if not mp3:
            print(f"sound {sid} 没有可下载的预览", file=sys.stderr)
            return 1
        dest = args.out_dir / f"fs{sid}.mp3"
        if not dest.exists():
            print("download", sid, dest.name)
            download(mp3, dest, key)
        else:
            print("exists", dest.name)
        meta[sid] = {
            "id": sid,
            "user": info.get("username") or "",
            "title": info.get("name") or "",
            "dur": float(info.get("duration") or 0),
            "dl": int(info.get("num_downloads") or 0),
            "mp3": mp3,
            "page": info.get("url") or f"https://freesound.org/s/{sid}/",
            "license": info.get("license") or "Creative Commons 0",
        }
    args.meta.parent.mkdir(parents=True, exist_ok=True)
    args.meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", args.meta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
