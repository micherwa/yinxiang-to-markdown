# 印象笔记 .notes → Markdown 转换工具

将印象笔记（Evernote China）导出的 `.notes` 文件批量转换为 Markdown 格式，便于导入 Obsidian 等笔记软件。

---

## 快速使用（非程序人员）

### macOS 用户

需先安装 Python 环境，然后按以下步骤操作：

1. 将 `.notes` 文件放进 `input/` 目录
2. 双击 `转换.command`
3. 转换后的 Markdown 文件在 `output/` 目录中，直接拷贝到 Obsidian vault 即可使用

### Windows 用户

无需安装任何环境，直接使用独立版：

1. 下载 [最新发布的 Windows 版本](../../actions/workflows/build-exe.yml)（点击最近一次运行 → 下载 `yinxiang-converter-windows`）
2. 解压后得到 `convert.exe`、`input/`、`output/` 三个文件
3. 将 `.notes` 文件放进 `input/` 目录
4. 双击 `convert.exe`
5. 转换后的 Markdown 文件在 `output/` 目录中

---

## 功能特性

- 自动解密 `.notes` 文件（AES-128-CBC 加密）
- 转换 ENML 为标准 Markdown
- 提取图片和附件到 `assets/` 目录
- 保留笔记元数据（标题、创建时间、更新时间、标签）
- 按笔记本名称分文件夹组织输出
- Obsidian 兼容（标签格式、图片路径）

---

## 输出结构

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
tags:
  - tag1
  - tag2
---
```

---

## 如何从印象笔记导出 .notes 文件

1. 打开印象笔记客户端
2. 选择要导出的笔记本
3. 全选笔记 → 文件 → 导出
4. 选择 `.notes` 格式保存

---

## 开发者指南

### 环境安装

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

### 运行测试

```bash
python -m pytest tests/ -v
```

### 打包 Windows .exe

本项目通过 GitHub Actions 自动构建 Windows 版本，无需在本地操作：

1. 进入仓库的 **Actions** 页面
2. 选择 **Build Windows exe** 工作流
3. 点击 **Run workflow**
4. 构建完成后，在 Artifacts 中下载 `yinxiang-converter-windows`

如需本地打包（需在 Windows 环境下）：

```bash
pip install pyinstaller
pyinstaller --onefile --name convert --hidden-import=src --hidden-import=src.main --hidden-import=src.decryptor --hidden-import=src.converter --hidden-import=src.resource_handler app.py
```
