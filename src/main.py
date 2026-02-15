"""CLI main entry point for Evernote/Yinxiang .notes conversion."""

import argparse
import re
from pathlib import Path

from src.converter import enml_to_markdown
from src.decryptor import parse_notes_file
from src.resource_handler import save_resources


def sanitize_filename(name: str) -> str:
    """Replace /\\:*?\"<>| with _, strip whitespace."""
    forbidden = r'/\:*?"<>|'
    result = name
    for char in forbidden:
        result = result.replace(char, "_")
    return result.strip()


def format_datetime(dt_str: str) -> str:
    """Convert Evernote time format 20220403T233652Z to ISO 2022-04-03T23:36:52Z."""
    if not dt_str:
        return dt_str
    m = re.fullmatch(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z", dt_str.strip())
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}T{m.group(4)}:{m.group(5)}:{m.group(6)}Z"
    return dt_str


def _build_front_matter(note: dict) -> str:
    """Build YAML front matter for a note (Obsidian-compatible)."""
    title = note.get("title", "")
    created = format_datetime(note.get("created", ""))
    updated = format_datetime(note.get("updated", ""))
    tags = note.get("tags", [])
    lines = [
        "---",
        f'title: "{title}"',
    ]
    if created:
        lines.append(f"created: {created}")
    if updated:
        lines.append(f"updated: {updated}")
    if tags:
        lines.append("tags:")
        for tag in tags:
            lines.append(f"  - {tag}")
    else:
        lines.append("tags: []")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def convert_notes_file(notes_path, output_dir):
    """Convert a single .notes file to markdown in output_dir/notebook_name/."""
    notes_path = Path(notes_path)
    output_dir = Path(output_dir)
    notebook_name = notes_path.stem
    notebook_dir = output_dir / notebook_name
    notebook_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = notebook_dir / "assets"

    notes = parse_notes_file(notes_path)
    total = len(notes)

    for i, note in enumerate(notes, start=1):
        resource_map = {}
        if note.get("resources"):
            resource_map = save_resources(note["resources"], assets_dir)
        md_content = enml_to_markdown(note.get("content", ""), resource_map)
        front_matter = _build_front_matter(note)
        base_filename = sanitize_filename(note.get("title", "")) or "untitled"
        filename = base_filename + ".md"
        filepath = notebook_dir / filename
        if filepath.exists():
            counter = 1
            while filepath.exists():
                filepath = notebook_dir / f"{base_filename}_{counter}.md"
                counter += 1
        filepath.write_text(front_matter + md_content + "\n", encoding="utf-8")
        print(f"Converting note {i}/{total}: {note.get('title', '(untitled)')}")

    print(f"Converted {total} notes to {notebook_dir}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert Evernote/Yinxiang .notes files to Markdown."
    )
    parser.add_argument(
        "input",
        help="Single .notes file or directory containing .notes files",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="./output",
        help="Output directory (default: ./output)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)

    if not input_path.exists():
        parser.error(f"Input path does not exist: {input_path}")

    if input_path.is_file():
        if input_path.suffix.lower() != ".notes":
            parser.error(f"Expected .notes file, got: {input_path}")
        convert_notes_file(input_path, output_dir)
    else:
        notes_files = list(input_path.glob("**/*.notes"))
        if not notes_files:
            parser.error(f"No .notes files found in {input_path}")
        for nf in notes_files:
            convert_notes_file(nf, output_dir)


if __name__ == "__main__":
    main()
