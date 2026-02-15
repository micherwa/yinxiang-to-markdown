"""独立运行入口，用于 PyInstaller 打包。固定 input/ → output/。"""
import sys
from pathlib import Path
from src.main import convert_notes_file


def run():
    # 打包后 exe 所在目录
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent

    input_dir = base / "input"
    output_dir = base / "output"

    print("=== 印象笔记 → Markdown 转换工具 ===")
    print()

    if not input_dir.exists():
        print("错误：找不到 input 文件夹。")
        print("请在当前目录创建 input 文件夹，并将 .notes 文件放入其中。")
        input("\n按回车键关闭...")
        return

    notes_files = sorted(input_dir.glob("*.notes"))
    if not notes_files:
        print("错误：input 文件夹中没有 .notes 文件。")
        print("请将印象笔记导出的 .notes 文件放入 input 文件夹。")
        input("\n按回车键关闭...")
        return

    print(f"发现 {len(notes_files)} 个 .notes 文件，开始转换...")
    print()

    for nf in notes_files:
        convert_notes_file(nf, output_dir)

    print()
    print("✅ 转换完成！结果在 output 文件夹中。")
    print("可以直接将 output 中的文件夹拷贝到 Obsidian vault 使用。")
    input("\n按回车键关闭...")


if __name__ == "__main__":
    run()
