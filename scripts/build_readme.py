#!/usr/bin/env python3
"""根据 icons.json 重写 README.md 中的图标清单区块（<!-- ICONS:START --> 与 <!-- ICONS:END --> 之间）。"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "icons.json"
README = ROOT / "README.md"

CDN = "https://cdn.jsdelivr.net/gh/dan90o0/icons@main"
START = "<!-- ICONS:START -->"
END = "<!-- ICONS:END -->"


def preview_icon(icon: dict) -> str:
    url = f"{CDN}/{icon['path']}"
    if icon["format"] == "json":
        return "Lottie"
    return f'<img src="{url}" width="32" alt="{icon["slug"]}">'


def section(title: str, icons: list) -> list:
    if not icons:
        return []
    lines = [
        f"### {title}",
        "",
        "| 图标 | 名称 | 中文名 | 格式 | 大小 | 路径 |",
        "|:---:|---|---|---|---:|---|",
    ]
    for i in icons:
        kb = f"{i['size'] / 1024:.1f} KB"
        lines.append(
            f"| {preview_icon(i)} | `{i['slug']}` | {i['name_zh']} | {i['format']} | {kb} | `{i['path']}` |"
        )
    lines.append("")
    return lines


def main() -> None:
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    icons = data.get("icons", [])

    if not icons:
        body = [
            "_还没有图标。发我一张图 + 一个名字，我就能收进来。_",
            "",
        ]
    else:
        cats = {}
        for i in icons:
            cats.setdefault(i["category"], []).append(i)
        body = []
        for cat in sorted(cats):
            body += section(f"{cat}（{len(cats[cat])}）", cats[cat])

    text = README.read_text(encoding="utf-8")
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    new = head + START + "\n\n" + "\n".join(body) + "\n" + END + tail
    README.write_text(new, encoding="utf-8")

    statics = sum(1 for i in icons if i["type"] == "static")
    anims = len(icons) - statics
    print(f"README 已更新：共 {len(icons)} 个（静态 {statics} / 动态 {anims}）")


if __name__ == "__main__":
    main()
