# 把图标文件传到这里

在 GitHub 网页或手机 App 里：**Add file → Upload files**，把图片拖进来后 Commit。

提交后会自动触发 `ingest-icon` 工作流：识别格式 → 转 GIF（必要时）→ 归档到 `static/` 或 `animated/` 下 → 更新 `icons.json`、`README.md` 和清单 JSON → 删除这里的源文件。

文件名会转成 slug：`Blue Dot.png` → `blue-dot`。想指定中文名或分类，用 Actions 的 `ingest-icon → Run workflow` 表单。
