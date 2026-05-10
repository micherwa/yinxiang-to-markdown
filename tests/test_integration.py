"""End-to-end integration tests with real .notes files.

These tests run against any *.notes files placed in ``input/``. They are
skipped when no sample is available, so the test suite stays green for
contributors who don't have private notes on hand.
"""
from pathlib import Path

import pytest

from src.main import convert_notes_file


def _samples() -> list[Path]:
    if not Path("input").exists():
        return []
    return sorted(Path("input").glob("*.notes"))


def test_full_conversion(tmp_path):
    samples = _samples()
    if not samples:
        pytest.skip("no sample .notes file in input/")
    for sample in samples:
        convert_notes_file(sample, tmp_path)
        notebook_dir = tmp_path / sample.stem
        assert notebook_dir.exists()
        md_files = list(notebook_dir.glob("*.md"))
        assert len(md_files) > 0
        for f in md_files:
            content = f.read_text(encoding="utf-8")
            assert content.startswith("---")
            assert "title:" in content


def test_image_extraction(tmp_path):
    """If any sample contains a PNG resource, verify it's extracted as a real PNG."""
    samples = _samples()
    if not samples:
        pytest.skip("no sample .notes file in input/")
    for sample in samples:
        convert_notes_file(sample, tmp_path)
        png_files = list((tmp_path / sample.stem / "assets").glob("*.png")) \
            if (tmp_path / sample.stem / "assets").exists() else []
        for png in png_files:
            assert png.read_bytes()[:4] == b"\x89PNG"
            return
    pytest.skip("no PNG resource found in any sample")
