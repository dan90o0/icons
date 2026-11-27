#!/usr/bin/env python3
"""收录一个图标到图标库：归档文件 -> 更新 icons.json -> 重建 README 表格 -> git commit & push。

用法:
    python3 scripts/add_icon.py <源文件或URL> --slug arrow-left --zh 左箭头 \
        --category arrow --type static

参数:
    source        本地图片路径，或 http(s) 图片链接
    --slug        英文文件名（必填，kebab-case）
    --zh          中文名（必填，用于 README 对照）
    --category    分类（如 arrow / emoji / social / file / weather）
    --type        static | animated，默认按扩展名自动判断
    --no-push     只提交，不推送
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "icons.json"

ANIMATED_EXT = {".gif", ".webp", ".apng", ".json", ".lottie"}
STATIC_EXT = {".svg", ".png", ".jpg", ".jpeg"}

# 扩展名 -> 目标目录
DEST = {
    ".svg": ("static", "svg"),
    ".png": ("static", "png"),
    ".jpg": ("static", "png"),
    ".jpeg": ("static", "png"),
    ".gif": ("animated", "gif"),
    ".webp": ("animated", "webp"),
    ".apng": ("animated", "webp"),
    ".json": ("animated", "lottie"),
    ".lottie": ("animated", "lottie"),
}


def fetch_source(src: str) -> Path:
    """本地文件直接返回，URL 先下载到临时目录。"""
    if src.startswith(("http://", "https://")):
        tmp = Path("/tmp") / os.path.basename(src.split("?")[0])
        req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r, open(tmp, "wb") as f:
            f.write(r.read())
        return tmp
    p = Path(src).expanduser()
    if not p.is_file():
        sys.exit(f"找不到源文件: {src}")
    return p


def detect_ext(path: Path, src: str) -> str:
    ext = path.suffix.lower()
    if ext in DEST:
        return ext
    # URL 无扩展名时按 content-type 兜底
    if src.startswith(("http://", "https://")):
        lowered = src.lower()
        for guess in (".gif", ".webp", ".svg", ".png", ".json"):
            if guess in lowered:
                return guess
    sys.exit(f"无法识别的格式: {ext or '(无扩展名)'}，请确认是 svg/png/gif/webp/lottie")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--zh", required=True)
    ap.add_argument("--category", default="misc")
    ap.add_argument("--type", choices=["static", "animated"])
    ap.add_argument("--no-push", action="store_true")
    args = ap.parse_args()

    slug = args.slug.strip().lower()
    src_path = fetch_source(args.source)
    ext = detect_ext(src_path, args.source)

    bucket, sub = DEST[ext]
    kind = args.type or ("animated" if ext in ANIMATED_EXT or bucket == "animated" else "static")

    dest_dir = ROOT / bucket / sub
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_name = f"{slug}{ext}"
    dest = dest_dir / dest_name
    shutil.copyfile(src_path, dest)

    rel = f"{bucket}/{sub}/{dest_name}"
    size = dest.stat().st_size

    data = json.loads(INDEX.read_text(encoding="utf-8"))
    icons = [i for i in data.get("icons", []) if i.get("slug") != slug]
    icons.append(
        {
            "slug": slug,
            "name_zh": args.zh,
            "category": args.category,
            "type": kind,
            "format": ext.lstrip("."),
            "path": rel,
            "size": size,
            "added": date.today().isoformat(),
        }
    )
    icons.sort(key=lambda i: (i["category"], i["slug"]))
    data["icons"] = icons
    data["count"] = len(icons)
    data["updated"] = date.today().isoformat()
    INDEX.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_readme.py")], check=True)

    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-m", f"add icon: {slug} ({args.zh})"], cwd=ROOT, check=True)
    if not args.no_push:
        subprocess.run(["git", "push", "origin", "HEAD"], cwd=ROOT, check=True)

    print(f"✓ {rel}  ({size} bytes)  {args.zh} / {slug}  [{kind}]")


if __name__ == "__main__":
    main()
