#!/usr/bin/env python3
"""自助入库：处理 incoming/ 下的文件，或通过 --url 指定的链接。

能力：
  - mp4/mov/webm/m4v/mkv -> GIF（宽 ≤560、15fps、调色板优化）
  - GIF 过大（>2MB）自动额外生成 {slug}-lite.gif（宽 ≤320、10fps）
  - 现有 gif/webp/apng 超宽自动缩放
  - svg/png/jpg 归静态，json/lottie 归 Lottie
  - slug 自动清洗（小写、空格转连字符），重名自动加 -2/-3
  - 处理完删除 incoming/ 源文件

用法：
  python3 scripts/ingest.py --url "https://..." --slug xxx --zh 中文名 --category character
  python3 scripts/ingest.py            # 扫描 incoming/，slug 取文件名
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INCOMING = ROOT / "incoming"
INDEX = ROOT / "icons.json"
TMP = Path("/tmp/ingest")
ADD = ROOT / "scripts" / "add_icon.py"

VIDEO_EXT = {".mp4", ".mov", ".webm", ".m4v", ".mkv", ".avi"}
IMAGE_EXT = {".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".apng"}
LOTTIE_EXT = {".json", ".lottie"}

LITE_THRESHOLD = 2 * 1024 * 1024  # 2MB


def sanitize(text: str) -> str:
    s = text.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "icon"


def unique_slug(slug: str) -> str:
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    used = {i["slug"] for i in data.get("icons", [])}
    if slug not in used:
        return slug
    n = 2
    while f"{slug}-{n}" in used:
        n += 1
    return f"{slug}-{n}"


def run(cmd: list) -> None:
    subprocess.run(cmd, check=True)


def gif_filter(width: int, fps: int) -> str:
    return (
        f"fps={fps},scale='min({width},iw)':-2:flags=lanczos,"
        "split[s0][s1];[s0]palettegen=stats_mode=diff[p];"
        "[s1][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle"
    )


def video_to_gif(src: Path, dst: Path, width: int = 560, fps: int = 15) -> None:
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
         "-vf", gif_filter(width, fps), "-loop", "0", str(dst)])


def gif_rescale(src: Path, dst: Path, width: int = 560, fps: int = 15) -> None:
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
         "-vf", gif_filter(width, fps), "-loop", "0", str(dst)])


def gif_width(path: Path) -> int:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    try:
        return int(out.stdout.strip().split(",")[0])
    except ValueError:
        return 0


def download(url: str) -> Path:
    TMP.mkdir(parents=True, exist_ok=True)
    name = Path(urllib.parse.urlparse(url).path).name or "download.bin"
    if not Path(name).suffix:
        name += ".bin"
    dst = TMP / name
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://x.com/"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dst, "wb") as f:
        shutil.copyfileobj(r, f)
    print(f"下载完成 {dst.name} ({dst.stat().st_size} bytes)")
    return dst


def guarantee_ext(src: Path, given_slug: str) -> tuple:
    """bin 或无扩展名时按文件头猜后缀，返回 (可处理路径, 建议 slug)。"""
    if src.suffix.lower() in VIDEO_EXT | IMAGE_EXT | LOTTIE_EXT:
        return src, given_slug
    head = src.read_bytes()[:16]
    if head[4:8] == b"ftyp":
        new = src.with_suffix(".mp4")
    elif head[:3] == b"GIF":
        new = src.with_suffix(".gif")
    elif head[:2] == b"\xff\xd8":
        new = src.with_suffix(".jpg")
    elif head[:8] == b"\x89PNG\r\n\x1a\n":
        new = src.with_suffix(".png")
    elif head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        new = src.with_suffix(".webp")
    else:
        raise SystemExit(f"无法识别文件类型：{src.name}")
    src.rename(new)
    return new, given_slug


def add(target: Path, slug: str, zh: str, category: str) -> None:
    run([sys.executable, str(ADD), str(target), "--slug", slug,
         "--zh", zh or slug, "--category", category, "--no-push", "--no-commit"])


def make_lite(slug: str) -> None:
    main = ROOT / "animated" / "gif" / f"{slug}.gif"
    if not main.exists() or main.stat().st_size <= LITE_THRESHOLD:
        return
    lite = main.with_name(f"{slug}-lite.gif")
    gif_rescale(main, lite, width=320, fps=10)
    print(f"  轻量版 → {lite.name} ({lite.stat().st_size / 1024:.0f} KB)")


def process(src: Path, slug: str, zh: str, category: str) -> None:
    src, _ = guarantee_ext(src, slug)
    ext = src.suffix.lower()
    TMP.mkdir(parents=True, exist_ok=True)

    if ext in VIDEO_EXT:
        gif = TMP / f"{slug}.gif"
        video_to_gif(src, gif)
        print(f"  视频转 GIF → {slug}.gif ({gif.stat().st_size / 1024:.0f} KB)")
        add(gif, slug, zh, category)
        make_lite(slug)
    elif ext == ".gif":
        if gif_width(src) > 560:
            gif = TMP / f"{slug}.gif"
            gif_rescale(src, gif)
            print(f"  缩放 GIF 至 560 宽 → {slug}.gif")
            add(gif, slug, zh, category)
        else:
            add(src, slug, zh, category)
        make_lite(slug)
    else:
        add(src, slug, zh, category)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="")
    ap.add_argument("--slug", default="")
    ap.add_argument("--zh", default="")
    ap.add_argument("--category", default="misc")
    args = ap.parse_args()

    processed = 0

    if args.url:
        src = download(args.url)
        slug = unique_slug(sanitize(args.slug or Path(urllib.parse.urlparse(args.url).path).stem or "icon"))
        print(f"→ 收录 {slug}")
        process(src, slug, args.zh, args.category)
        processed += 1
    else:
        INCOMING.mkdir(exist_ok=True)
        files = [p for p in sorted(INCOMING.iterdir()) if p.is_file() and not p.name.startswith(".")]
        if not files:
            print("incoming/ 里没有待处理文件，也没有传 --url。")
            return
        for f in files:
            slug = unique_slug(sanitize(args.slug or f.stem))
            print(f"→ 收录 {f.name} as {slug}")
            try:
                process(f, slug, args.zh, args.category)
                f.unlink()
                processed += 1
            except subprocess.CalledProcessError as e:
                print(f"  失败，保留源文件：{e}")

    print(f"\n完成：{processed} 个")


if __name__ == "__main__":
    main()
