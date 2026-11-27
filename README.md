# Icons

个人图标库。静态图标按矢量/位图分开，动态图标按实际格式（GIF / WebP / Lottie / SVG 动画）分开，文件名统一英文 slug。

<p>
  <img src="https://img.shields.io/badge/icons-0-blue" alt="icon count">
  <img src="https://img.shields.io/badge/license-personal-lightgrey" alt="license">
</p>

## 目录结构

```
icons/
├── static/
│   ├── svg/          # 矢量静态图标
│   └── png/          # 位图静态图标（jpg/jpeg 也归到这里）
├── animated/
│   ├── gif/          # GIF 动图
│   ├── webp/         # WebP / APNG 动图
│   ├── lottie/       # Lottie JSON 矢量动画
│   └── svg/          # SMIL / CSS 动画的 SVG
├── icons.json        # 全量索引（slug / 中文名 / 分类 / 格式 / 路径 / 大小）
├── scripts/
│   ├── add_icon.py   # 收录新图标：归档 + 更新索引 + 重建本表格 + 提交推送
│   └── build_readme.py
└── README.md
```

判定规则：文件后缀说了算。`.svg` 默认静态，若内容是带动画的 SVG 就放进 `animated/svg`。

## 命名规范

- 文件名一律 **kebab-case 英文 slug**：`arrow-left`、`heart-beat`、`shopping-cart`
- 中文名只存在 `icons.json` 的 `name_zh` 字段和下面的对照表里，不进文件名
- 同名 slug 重复收录时，新文件覆盖旧的，索引里保留一条

## 怎么用

jsDelivr CDN（推荐，带缓存和跨域）：

```
https://cdn.jsdelivr.net/gh/dan90o0/icons@main/static/svg/arrow-left.svg
```

GitHub 原始文件：

```
https://raw.githubusercontent.com/dan90o0/icons/main/static/svg/arrow-left.svg
```

微信小程序里用 CDN 地址时，记得把 `cdn.jsdelivr.net` 加进 **downloadFile 合法域名**；如果不想配域名，直接把 `.svg` / `.png` 下载进包内 `assets/` 反而更稳。

## 收录新图标

```bash
# 本地文件
python3 scripts/add_icon.py ./incoming/heart.gif --slug heart-beat --zh 心跳 --category emoji

# 网络图片
python3 scripts/add_icon.py "https://example.com/arrow.png" --slug arrow-left --zh 左箭头 --category arrow
```

脚本会按后缀把文件放进对应目录，更新 `icons.json`，重写下面的清单表格，然后 commit + push。

## 清单文件（Emby / Jellyfin 图标库格式）

根目录自动生成两类清单，格式与 [sooyaaabo/IconLibrary](https://github.com/sooyaaabo/IconLibrary) 一致（Emby 图标库插件可直接读取）：

| 文件 | 内容 |
|---|---|
| `All-Icon.json` | 全量图标（静态 + 动态） |
| `{分类}-Icon.json` | 按分类拆分，如 `Character-Icon.json` |

结构：

```json
{
    "name": "dan90o0 图标库",
    "description": "作者：dan90o0｜更新时间：2026-11-27 14:37｜共 1 个（静态 0 · 动态 1）",
    "icons": [
        {
            "name": "suis-dance",
            "url": "https://raw.githubusercontent.com/dan90o0/icons/main/animated/gif/suis-dance.gif"
        }
    ]
}
```

订阅地址：

```
https://raw.githubusercontent.com/dan90o0/icons/main/All-Icon.json
https://cdn.jsdelivr.net/gh/dan90o0/icons@main/All-Icon.json
```

每次收录图标由 `scripts/build_manifest.py` 自动重建，`name` 取中文名（无则用 slug），`url` 为 raw 直链。注意 Emby 网页端显示 GIF 取决于客户端，部分客户端只渲染首帧。

## 图标清单

<!-- ICONS:START -->

### character（1）

| 图标 | 名称 | 中文名 | 格式 | 大小 | 路径 |
|:---:|---|---|---|---:|---|
| <img src="https://cdn.jsdelivr.net/gh/dan90o0/icons@main/animated/gif/suis-dance.gif" width="32" alt="suis-dance"> | `suis-dance` | suis-dance | gif | 522.0 KB | `animated/gif/suis-dance.gif` |

<!-- ICONS:END -->

## 授权

图标仅供本人项目使用。若后续要开源给他人复用，建议补一份 LICENSE（如 MIT 或 CC BY 4.0）。
