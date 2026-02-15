"""End-to-end integration tests with real .notes files."""
from pathlib import Path

from src.main import convert_notes_file


def test_full_conversion_zhoubao(tmp_path):
    """Convert 周报.notes (24 notes)"""
    convert_notes_file("input/周报.notes", tmp_path)
    notebook_dir = tmp_path / "周报"
    assert notebook_dir.exists()
    md_files = list(notebook_dir.glob("*.md"))
    assert len(md_files) == 24
    for f in md_files:
        content = f.read_text(encoding="utf-8")
        assert content.startswith("---")
        assert "title:" in content


def test_full_conversion_guanggao(tmp_path):
    """Convert 广告业务.notes (4 notes)"""
    convert_notes_file("input/广告业务.notes", tmp_path)
    notebook_dir = tmp_path / "广告业务"
    assert notebook_dir.exists()
    md_files = list(notebook_dir.glob("*.md"))
    assert len(md_files) == 4


def test_guanggao_has_image(tmp_path):
    """广告业务 should have extracted image asset"""
    convert_notes_file("input/广告业务.notes", tmp_path)
    assets_dir = tmp_path / "广告业务" / "assets"
    if assets_dir.exists():
        png_files = list(assets_dir.glob("*.png"))
        assert len(png_files) >= 1
        # Verify it's a real PNG
        first_png = png_files[0]
        data = first_png.read_bytes()
        assert data[:4] == b"\x89PNG"
