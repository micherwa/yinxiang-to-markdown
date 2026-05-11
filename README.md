# 印象笔记 .notes → Markdown 转换工具

[![Test](https://github.com/micherwa/yinxiang-to-markdown/actions/workflows/test.yml/badge.svg)](https://github.com/micherwa/yinxiang-to-markdown/actions/workflows/test.yml)
[![Release](https://img.shields.io/github/v/release/micherwa/yinxiang-to-markdown?label=release)](https://github.com/micherwa/yinxiang-to-markdown/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

将印象笔记（Evernote China）导出的 `.notes` 文件批量转换为 Markdown 格式，便于导入 Obsidian 等笔记软件。

> **免责声明**：本工具仅用于将用户**自己**导出的 `.notes` 文件转换为 Markdown，便于个人备份与迁移。请确保你拥有所处理数据的合法权利。使用本工具造成的数据损失或任何法律风险由使用者自行承担。

---

## 快速使用（非程序人员）

到 [Releases 页面](https://github.com/micherwa/yinxiang-to-markdown/releases/latest) 下载对应平台的压缩包：

### Windows

1. 下载 `yinxiang-converter-windows.zip` 并解压
2. 将 `.notes` 文件放进 `input/` 目录
3. 双击 `convert.exe`
4. 转换后的 Markdown 文件在 `output/` 目录中，直接拷贝到 Obsidian vault 即可使用

### macOS

1. 下载 `yinxiang-converter-macos.tar.gz` 并解压
2. 将 `.notes` 文件放进 `input/` 目录
3. 双击 `convert`（首次打开会被 Gatekeeper 拦截 → 在 Finder 里**右键 → 打开** → 弹窗里再点"打开"）
4. 转换后的 Markdown 文件在 `output/` 目录中

> 也可以从源码运行：见下方"开发者指南"。

---

## 功能特性

- 自动解密 `.notes` 文件（AES-128-CBC + HMAC-SHA256 完整性校验）
- 转换 ENML 为标准 Markdown：标题、加粗/斜体、删除线、上下标、引用、链接、表格、嵌套列表、待办、代码块
- 提取图片和附件到 `assets/` 目录
- 保留笔记元数据（标题、创建时间、更新时间、标签）
- 按笔记本名称分文件夹组织输出
- Obsidian 兼容（YAML 标签格式、相对图片路径）
- 安全：使用 `defusedxml` 防御不可信 XML 输入

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

### 环境要求

- Python 3.9+

### 环境安装

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# 或固定版本：pip install -r requirements.lock
```

### CLI 命令行

```bash
# 转换单个文件
python -m src.main path/to/笔记本.notes -o output/

# 转换整个目录
python -m src.main path/to/notes_dir/ -o output/

# 重复运行时的策略
python -m src.main input/ -o output/ --skip-existing   # 跳过已有的
python -m src.main input/ -o output/ --overwrite       # 覆盖已有的
# 默认行为：自动追加 _1/_2 后缀

# 显示 debug 日志
python -m src.main input/ -o output/ -v
```

### 运行测试

```bash
pytest tests/ -v
```

依赖真实 `.notes` 文件的集成测试在 `input/` 为空时会自动 skip。

### 打包跨平台二进制

通过推送 `v*` tag 自动触发 GitHub Actions 构建 Windows 和 macOS 二进制并发布到 Releases：

```bash
git tag v0.1.0
git push origin v0.1.0
```

也可以本地打包：

```bash
pip install pyinstaller
pyinstaller --onefile --name convert \
  --hidden-import=src --hidden-import=src.main \
  --hidden-import=src.decryptor --hidden-import=src.converter \
  --hidden-import=src.resource_handler app.py
```

---

## 安全报告

发现漏洞请见 [SECURITY.md](./SECURITY.md)。

## 致谢

`.notes` 加密格式的逆向分析参考了开源项目 [HNIdesu/YinxiangbijiConverter](https://github.com/HNIdesu/YinxiangbijiConverter)。

## License

[MIT](./LICENSE)
