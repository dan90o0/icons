#!/usr/bin/env python3
"""生成 Emby/Jellyfin 图标库清单（参考 sooyaaabo/IconLibrary 的格式）。

输出：
  All-Icon.json            全量清单（静态 + 动态）
  {Category}-Icon.json     按分类拆分，如 Character-Icon.json

格式与 Emby 图标库插件兼容：
{
  "name": "图标库名称",
  "description": "作者｜更新时间｜说明",
  "icons": [ { "name": "显示名", "url": "图片直链" }, ... ]
}
"""

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "icons.json"

RAW = "https://raw.githubusercontent.com/dan90o0/icons/main"
AUTHOR = "dan90o0"
LIB_NAME = "dan90o0 图标库"


def icon_url(icon: dict) -> str:
    """大 GIF 存在 -lite 版本时，清单指向轻量版（体积小、加载快）。"""
    path = ROOT / icon["path"]
    lite = path.with_name(f"{path.stem}-lite{path.suffix}")
    if lite.exists():
        return f"{RAW}/{icon['path'].rsplit('/', 1)[0]}/{lite.name}"
    return f"{RAW}/{icon['path']}"


def manifest(icons: list, title: str, extra: str = "") -> dict:
    statics = sum(1 for i in icons if i["type"] == "static")
    anims = len(icons) - statics
    parts = [
        f"作者：{AUTHOR}",
        f"更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"共 {len(icons)} 个（静态 {statics} · 动态 {anims}）",
    ]
    if extra:
        parts.append(extra)
    return {
        "name": title,
        "description": "｜".join(parts),
        "icons": [
            {"name": i.get("name_zh") or i["slug"], "url": icon_url(i)}
            for i in sorted(icons, key=lambda x: (x["category"], x["slug"]))
        ],
    }


def write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    print(f"  {path.name}: {len(data['icons'])} 个")


def main() -> None:
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    icons = data.get("icons", [])

    print("生成清单：")
    write(ROOT / "All-Icon.json", manifest(icons, LIB_NAME))

    cats = {}
    for i in icons:
        cats.setdefault(i["category"], []).append(i)
    for cat, items in sorted(cats.items()):
        fname = f"{cat.capitalize()}-Icon.json"
        write(ROOT / fname, manifest(items, f"{LIB_NAME} · {cat}"))

    # 清理已没有图标的旧分类清单
    for p in ROOT.glob("*-Icon.json"):
        if p.name == "All-Icon.json":
            continue
        cat = p.stem[: -len("-Icon")].lower()
        if cat not in cats:
            p.unlink()
            print(f"  删除空分类清单 {p.name}")


if __name__ == "__main__":
    main()
