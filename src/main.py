"""CLI main entry point for Evernote/Yinxiang .notes conversion."""

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import Optional

from src.converter import enml_to_markdown
from src.decryptor import parse_notes_file
from src.resource_handler import save_resources

logger = logging.getLogger(__name__)

# Windows 文件系统保留名（不区分大小写）
_WIN_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}

# 跨平台文件名安全长度（NTFS / APFS 单段上限 255 字节，留点余量给后缀）
_FILENAME_MAX = 200


def sanitize_filename(name: str) -> str:
    """Make a string safe to use as a cross-platform filename.

    Rules:
    - Replace path separators and shell metachars with `_`
    - Strip control chars
    - Strip leading/trailing dots and whitespace (Windows quietly drops them)
    - Avoid Windows reserved names (CON, PRN, NUL, COM1..9, LPT1..9)
    - Truncate to 200 chars to leave headroom for `.md` and dedup suffix
    """
    forbidden = r'/\:*?"<>|'
    result = name
    for ch in forbidden:
        result = result.replace(ch, "_")
    # control chars
    result = re.sub(r"[\x00-\x1f]", "_", result)
    # collapse whitespace runs
    result = re.sub(r"\s+", " ", result).strip()
    # Windows: trailing dots/spaces are silently stripped, leading dot hides on Unix
    result = result.strip(". ")
    if not result:
        return ""
    # Reserved names: prepend underscore
    stem = result.split(".", 1)[0]
    if stem.upper() in _WIN_RESERVED:
        result = "_" + result
    if len(result) > _FILENAME_MAX:
        result = result[:_FILENAME_MAX].rstrip(". ")
    return result


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


def _resolve_target(notebook_dir: Path, base: str, mode: str) -> Optional[Path]:
    """Decide where to write a note's .md file.

    Returns the target path, or None if the note should be skipped.
    """
    target = notebook_dir / f"{base}.md"
    if not target.exists():
        return target
    if mode == "overwrite":
        return target
    if mode == "skip":
        return None
    # default: dedup with numeric suffix
    counter = 1
    while True:
        candidate = notebook_dir / f"{base}_{counter}.md"
        if not candidate.exists():
            return candidate
        counter += 1


def convert_notes_file(notes_path, output_dir, *, on_conflict: str = "rename") -> dict:
    """Convert a single .notes file to markdown in output_dir/notebook_name/.

    Args:
        notes_path: path to the .notes file
        output_dir: root output directory
        on_conflict: 'rename' (default, append _1/_2…), 'overwrite', or 'skip'

    Returns a dict with counts: {"converted": N, "skipped": M, "failed": K}.
    """
    notes_path = Path(notes_path)
    output_dir = Path(output_dir)
    notebook_name = sanitize_filename(notes_path.stem) or "untitled"
    notebook_dir = output_dir / notebook_name
    notebook_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = notebook_dir / "assets"

    try:
        notes = parse_notes_file(notes_path)
    except Exception as e:
        logger.error("failed to parse %s: %s", notes_path, e)
        return {"converted": 0, "skipped": 0, "failed": 1}

    converted = skipped = failed = 0
    total = len(notes)

    try:
        from tqdm import tqdm
        iterator = tqdm(notes, desc=notebook_name, unit="note", leave=False)
        log_fn = tqdm.write
    except ImportError:
        iterator = notes
        log_fn = print

    for i, note in enumerate(iterator, start=1):
        try:
            resource_map = {}
            if note.get("resources"):
                resource_map = save_resources(note["resources"], assets_dir)
            md_content = enml_to_markdown(note.get("content", ""), resource_map)
            front_matter = _build_front_matter(note)
            base = sanitize_filename(note.get("title", "")) or f"untitled_{i}"
            target = _resolve_target(notebook_dir, base, on_conflict)
            if target is None:
                skipped += 1
                continue
            target.write_text(front_matter + md_content + "\n", encoding="utf-8")
            converted += 1
        except Exception as e:
            failed += 1
            logger.warning("note %d/%d (%r) failed: %s", i, total, note.get("title", ""), e)

    log_fn(
        f"[{notebook_name}] converted={converted} skipped={skipped} failed={failed} → {notebook_dir}"
    )
    return {"converted": converted, "skipped": skipped, "failed": failed}


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert Evernote/Yinxiang .notes files to Markdown.",
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
    conflict = parser.add_mutually_exclusive_group()
    conflict.add_argument(
        "--overwrite",
        dest="on_conflict",
        action="store_const",
        const="overwrite",
        help="Overwrite existing .md files with the same name",
    )
    conflict.add_argument(
        "--skip-existing",
        dest="on_conflict",
        action="store_const",
        const="skip",
        help="Skip notes whose target .md already exists",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show debug logs",
    )
    parser.set_defaults(on_conflict="rename")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    input_path = Path(args.input)
    output_dir = Path(args.output)

    if not input_path.exists():
        parser.error(f"Input path does not exist: {input_path}")

    if input_path.is_file():
        if input_path.suffix.lower() != ".notes":
            parser.error(f"Expected .notes file, got: {input_path}")
        notes_files = [input_path]
    else:
        notes_files = sorted(input_path.glob("**/*.notes"))
        if not notes_files:
            parser.error(f"No .notes files found in {input_path}")

    totals = {"converted": 0, "skipped": 0, "failed": 0}
    for nf in notes_files:
        result = convert_notes_file(nf, output_dir, on_conflict=args.on_conflict)
        for k in totals:
            totals[k] += result[k]

    print(
        f"\nDone. converted={totals['converted']} "
        f"skipped={totals['skipped']} failed={totals['failed']}"
    )
    sys.exit(1 if totals["failed"] else 0)


if __name__ == "__main__":
    main()
