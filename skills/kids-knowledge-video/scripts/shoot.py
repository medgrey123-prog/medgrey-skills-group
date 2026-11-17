#!/usr/bin/env python3
"""用 Playwright 无头浏览器调用 window.render(t)，截单帧或导出帧序列。

画面是 1080×1920 竖屏。HTML 必须提供 window.render(t)，可选 window.ready Promise。

用法：
  shoot.py frame  --root templates/cinematic-light --html film.html --time 5.5 --out shot.png
  shoot.py stills --root DIR --html film.html --out DIR --times 1 5 12 20
  shoot.py frames --root DIR --html film.html --out frames --start 0 --end 90 --fps 30 --workers 2
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import functools
import http.server
import os
import socketserver
import sys
import threading
from pathlib import Path

from playwright.async_api import async_playwright

CHROME_ARGS = [
    "--use-gl=angle",
    "--use-angle=swiftshader",
    "--enable-unsafe-swiftshader",
    "--ignore-gpu-blocklist",
]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args) -> None:
        pass


def serve(root: Path) -> int:
    handler = functools.partial(QuietHandler, directory=str(root))
    server = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server.server_address[1]


async def open_page(browser, port: int, html: str, width: int, height: int, fonts: list[str]):
    page = await browser.new_page(viewport={"width": width, "height": height})
    page.on("pageerror", lambda e: print("ERR:", e, file=sys.stderr))
    await page.goto(f"http://127.0.0.1:{port}/{html}")
    await page.wait_for_function("typeof window.render==='function'", timeout=60000)
    await page.evaluate(
        """async (fonts) => {
          await document.fonts.ready;
          if (window.ready) await window.ready;
          for (const f of fonts) { try { await document.fonts.load(f); } catch (e) {} }
        }""",
        fonts,
    )
    return page


async def render_times(page, times: list[float], out_paths: list[Path]) -> None:
    for t, dest in zip(times, out_paths):
        dest.parent.mkdir(parents=True, exist_ok=True)
        await page.evaluate(f"window.render({t})")
        await page.screenshot(path=str(dest))
        print("still", dest, t, flush=True)


async def render_frames(pages, start: int, end: int, fps: int, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    idx = list(range(start, end))
    workers = len(pages)

    async def run(page, frames: list[int]) -> None:
        for f in frames:
            await page.evaluate(f"window.render({f / fps})")
            data = await page.evaluate("document.getElementById('c').toDataURL('image/png')")
            (outdir / f"f{f:05d}.png").write_bytes(base64.b64decode(data.split(",", 1)[1]))
            if f % 30 == 0:
                print("frame", f, flush=True)

    await asyncio.gather(*[run(pages[i], idx[i::workers]) for i in range(workers)])


async def async_main(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    if not (root / args.html).exists():
        print(f"找不到 {root / args.html}", file=sys.stderr)
        return 2
    port = serve(root)
    fonts = args.font or [
        '900 96px "Noto Sans CJK SC"',
        '700 54px "Noto Sans CJK SC"',
        '500 28px "IBM Plex Mono"',
        '900 96px "Noto Serif CJK SC"',
        '40px WK, "Noto Sans CJK SC"',
    ]
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=CHROME_ARGS)
        if args.cmd == "frames":
            pages = [await open_page(browser, port, args.html, args.width, args.height, fonts) for _ in range(args.workers)]
            await render_frames(pages, args.start, args.end, args.fps, args.out)
        else:
            page = await open_page(browser, port, args.html, args.width, args.height, fonts)
            if args.cmd == "frame":
                await render_times(page, [args.time], [args.out])
            else:
                paths = [args.out / f"s_{t:05.2f}.png" for t in args.times]
                await render_times(page, args.times, paths)
        await browser.close()
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Playwright 截取 render(t) 帧")
    p.add_argument("--root", type=Path, required=True, help="静态文件根目录（film.html、common.js、L/ 所在处）")
    p.add_argument("--html", default="film.html")
    p.add_argument("--width", type=int, default=1080)
    p.add_argument("--height", type=int, default=1920)
    p.add_argument("--font", action="append", default=None, help="额外 document.fonts.load 参数，可重复")
    sub = p.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("frame", help="单帧")
    f.add_argument("--time", type=float, required=True)
    f.add_argument("--out", type=Path, required=True)

    s = sub.add_parser("stills", help="多张静帧")
    s.add_argument("--times", type=float, nargs="+", required=True)
    s.add_argument("--out", type=Path, required=True)

    r = sub.add_parser("frames", help="连续帧序列")
    r.add_argument("--start", type=int, default=0, help="起始帧号（含）")
    r.add_argument("--end", type=int, required=True, help="结束帧号（不含）")
    r.add_argument("--fps", type=int, default=30)
    r.add_argument("--workers", type=int, default=2)
    r.add_argument("--out", type=Path, required=True)

    args = p.parse_args()
    return asyncio.run(async_main(args))


if __name__ == "__main__":
    raise SystemExit(main())
