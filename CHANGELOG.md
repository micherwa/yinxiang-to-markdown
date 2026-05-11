# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-05-11

### Added
- 首个公开版本
- `.notes` 文件 AES-128-CBC 解密（HMAC-SHA256 完整性校验）
- ENML → Markdown 转换（支持标题、加粗、斜体、列表、表格、引用、删除线、上下标、代码块、待办、分隔线）
- 资源（图片、附件）按笔记本分目录提取
- YAML Front Matter 输出，Obsidian 兼容
- CLI 入口：`python -m src.main <input> -o <output>`
- 双击启动脚本：`转换.command`（macOS）、`转换.bat`（Windows）
- 跨平台二进制（Windows / macOS）通过 GitHub Actions 构建并发布到 Releases
- `--overwrite` / `--skip-existing` 选项控制重复运行行为
- tqdm 进度条
- `defusedxml` 防御不可信 XML 输入
- MIT License

[Unreleased]: https://github.com/micherwa/yinxiang-to-markdown/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/micherwa/yinxiang-to-markdown/releases/tag/v0.1.0
