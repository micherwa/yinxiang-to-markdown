# 印象笔记 .notes → Markdown 转换工具

将印象笔记（Evernote China）导出的 `.notes` 文件批量转换为 Markdown 格式，便于导入 Obsidian 等笔记软件。

---

## 快速使用（非程序人员）

无需安装 Python，按以下步骤操作：

1. **放入文件**：将 `.notes` 文件放进 `input/` 目录
2. **运行转换**：
   - **macOS**：双击 `转换.command`
   - **Windows**：双击 `转换.bat` 或 `转换.exe`
3. **获取结果**：转换后的 Markdown 文件在 `output/` 目录中，直接拷贝到 Obsidian vault 即可使用

---

## Windows 独立版（不需要 Python）

如果你使用 Windows 且未安装 Python，可使用 `转换.exe`：

- 双击 `转换.exe` 即可运行
- 同样将 `.notes` 放入 `input/`，结果输出到 `output/`
- `转换.exe` 由 PyInstaller 打包生成，无需额外环境

---

## 项目介绍

本工具支持：

- 自动解密 `.notes` 文件（AES-128-CBC 加密）
- 转换 ENML 为标准 Markdown
- 提取图片和附件到 `assets/` 目录
- 保留笔记元数据（标题、创建时间、更新时间、标签）
- 按笔记本名称分文件夹组织输出

---

## 开发者使用

### 安装

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### CLI 命令行

**转换单个文件：**

```bash
python -m src.main path/to/笔记本.notes -o output/
```

**转换整个目录：**

```bash
python -m src.main path/to/notes_dir/ -o output/
```

### 输出结构

```
output/
├── 笔记本A/
│   ├── 笔记标题1.md
│   ├── 笔记标题2.md
│   └── assets/
│       ├── image.png
│       └── file.pdf
├── 笔记本B/
│   └── ...
```

每个 Markdown 文件包含 YAML Front Matter：

```yaml
---
title: "笔记标题"
created: 2022-04-03T23:36:52Z
updated: 2022-07-03T13:59:08Z
tags: [tag1, tag2]
---
```

---

## 如何从印象笔记导出 .notes 文件

1. 打开印象笔记客户端
2. 选择要导出的笔记本
3. 全选笔记 → 文件 → 导出
4. 选择 `.notes` 格式保存

---

## 打包 Windows .exe（开发者）

使用 PyInstaller 打包独立可执行文件：

```bash
pip install pyinstaller
pyinstaller --onefile --name 转换 src/main.py
```

生成的 `转换.exe` 位于 `dist/` 目录，可复制给非 Python 用户使用。

---

## 运行测试（开发者）

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```
