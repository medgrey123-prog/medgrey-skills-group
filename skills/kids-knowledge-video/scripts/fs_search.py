#!/usr/bin/env python3
"""用 Freesound API 搜索 CC0 音效。

需要环境变量 FREESOUND_API_KEY（https://freesound.org/apiv2/apply/ 申请）。
不要把密钥写进脚本、仓库或 AUDIO_SOURCES.md。

用法：
  fs_search.py -q "wind chimes" -q "page turn" --out candidates.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://freesound.org/apiv2/search/text/"


def api_key() -> str:
    key = os.environ.get("FREESOUND_API_KEY", "").strip()
    if not key:
        print("请设置环境变量 FREESOUND_API_KEY（在 https://freesound.org/apiv2/apply/ 申请）。", file=sys.stderr)
        raise SystemExit(2)
    return key


def search(query: str, key: str, limit: int) -> list[dict]:
    params = {
        "query": query,
        "filter": 'license:"Creative Commons 0"',
        "fields": "id,name,username,duration,num_downloads,previews,url,license,tags",
        "sort": "downloads_desc",
        "page_size": str(limit),
    }
    req = urllib.request.Request(
        API + "?" + urllib.parse.urlencode(params),
        headers={"Authorization": f"Token {key}", "User-Agent": "kids-knowledge-video/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    out = []
    for r in data.get("results", []):
        previews = r.get("previews") or {}
        out.append({
            "id": str(r["id"]),
            "user": r.get("username") or "",
            "title": r.get("name") or "",
            "dur": float(r.get("duration") or 0),
            "dl": int(r.get("num_downloads") or 0),
            "mp3": previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3") or "",
            "page": r.get("url") or f"https://freesound.org/people/{r.get('username','')}/sounds/{r['id']}/",
            "license": r.get("license") or "Creative Commons 0",
            "tags": r.get("tags") or [],
        })
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="搜索 Freesound CC0 音效")
    p.add_argument("-q", "--query", action="append", required=True, help="可重复传入多组关键词")
    p.add_argument("--limit", type=int, default=12)
    p.add_argument("--out", type=Path, default=None, help="写入 JSON（默认打印到 stdout）")
    args = p.parse_args()
    key = api_key()
    result = {}
    for q in args.query:
        hits = search(q, key, args.limit)
        result[q] = hits
        print(f"## {q}")
        for r in hits:
            print(f"  {r['id']:>7} {r['dur']:5.1f}s dl={r['dl']:6} {r['title'][:50]} ({r['user']})")
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
