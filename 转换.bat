@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist "input" (
    echo 错误：找不到 input 文件夹。
    echo 请在当前目录创建 input 文件夹，并将 .notes 文件放入其中。
    echo.
    pause
    exit /b 1
)

dir /b "input\*.notes" >nul 2>&1
if errorlevel 1 (
    echo 错误：input 文件夹中没有 .notes 文件。
    echo 请将印象笔记导出的 .notes 文件放入 input 文件夹。
    echo.
    pause
    exit /b 1
)

echo === 印象笔记 转换为 Markdown 转换工具 ===
echo 开始转换...
echo.

.venv\Scripts\python.exe -m src.main input -o output

echo.
echo 转换完成！结果在 output 文件夹中。
echo 可以直接将 output 中的文件夹拷贝到 Obsidian vault 使用。
echo.
pause
