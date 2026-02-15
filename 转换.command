#!/bin/bash
cd "$(dirname "$0")"

# 检查 input 文件夹
if [ ! -d "input" ]; then
    echo "错误：找不到 input 文件夹。"
    echo "请在当前目录创建 input 文件夹，并将 .notes 文件放入其中。"
    echo ""
    echo "按回车键关闭..."
    read
    exit 1
fi

# 检查是否有 .notes 文件
count=$(ls -1 input/*.notes 2>/dev/null | wc -l)
if [ "$count" -eq 0 ]; then
    echo "错误：input 文件夹中没有 .notes 文件。"
    echo "请将印象笔记导出的 .notes 文件放入 input 文件夹。"
    echo ""
    echo "按回车键关闭..."
    read
    exit 1
fi

echo "=== 印象笔记 → Markdown 转换工具 ==="
echo "发现 $count 个 .notes 文件，开始转换..."
echo ""

source .venv/bin/activate
python -m src.main input -o output

echo ""
echo "✅ 转换完成！结果在 output 文件夹中。"
echo "可以直接将 output 中的文件夹拷贝到 Obsidian vault 使用。"
echo ""
echo "按回车键关闭..."
read
