"""Tests for the main CLI module."""

from src.main import sanitize_filename, format_datetime, convert_notes_file, _build_front_matter


def test_sanitize_filename():
    assert sanitize_filename("hello world") == "hello world"
    assert sanitize_filename("a/b\\c:d") == "a_b_c_d"
    assert sanitize_filename("test?.md") == "test_.md"
    assert sanitize_filename("  spaces  ") == "spaces"


def test_format_datetime():
    assert format_datetime("20220403T233652Z") == "2022-04-03T23:36:52Z"
    assert format_datetime("") == ""
    assert format_datetime("invalid") == "invalid"


def test_front_matter_with_tags():
    """有标签时应输出 YAML list 格式"""
    note = {
        "title": "Test",
        "created": "20220403T233652Z",
        "updated": "20220703T135908Z",
        "tags": ["work", "project"],
    }
    fm = _build_front_matter(note)
    assert "tags:" in fm
    assert "  - work" in fm
    assert "  - project" in fm
    assert "['work'" not in fm


def test_front_matter_no_tags():
    """无标签时应输出空 list"""
    note = {
        "title": "Test",
        "created": "",
        "updated": "",
        "tags": [],
    }
    fm = _build_front_matter(note)
    assert "tags: []" in fm


def test_convert_notes_file(tmp_path):
    output_dir = tmp_path / "output"
    convert_notes_file("input/广告业务.notes", output_dir)
    notebook_dir = output_dir / "广告业务"
    assert notebook_dir.exists()
    md_files = list(notebook_dir.glob("*.md"))
    assert len(md_files) == 4
    content = md_files[0].read_text(encoding="utf-8")
    assert "---" in content
    assert "title:" in content
