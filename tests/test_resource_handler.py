import os
from src.resource_handler import save_resources, mime_to_ext


def test_mime_to_ext():
    assert mime_to_ext("image/png") == ".png"
    assert mime_to_ext("image/jpeg") == ".jpeg"
    assert mime_to_ext("application/pdf") == ".pdf"
    assert mime_to_ext("unknown/type") == ".bin"


def test_save_resources(tmp_path):
    resources = [
        {"data": b"\x89PNG\r\n\x1a\n fake png data", "mime": "image/png", "filename": "screenshot.png", "md5": "abc123"},
        {"data": b"%PDF fake pdf data", "mime": "application/pdf", "filename": "report.pdf", "md5": "def456"},
    ]
    assets_dir = tmp_path / "assets"
    mapping = save_resources(resources, assets_dir)
    assert len(mapping) == 2
    assert "abc123" in mapping
    assert "def456" in mapping
    assert os.path.exists(assets_dir / mapping["abc123"])
    assert os.path.exists(assets_dir / mapping["def456"])
    assert "screenshot.png" in mapping["abc123"]
    assert "report.pdf" in mapping["def456"]


def test_save_resources_duplicate_filename(tmp_path):
    resources = [
        {"data": b"data1", "mime": "image/png", "filename": "img.png", "md5": "aaa"},
        {"data": b"data2", "mime": "image/png", "filename": "img.png", "md5": "bbb"},
    ]
    assets_dir = tmp_path / "assets"
    mapping = save_resources(resources, assets_dir)
    assert len(mapping) == 2
    assert mapping["aaa"] != mapping["bbb"]


def test_save_resources_no_filename(tmp_path):
    resources = [
        {"data": b"data", "mime": "image/jpeg", "filename": "", "md5": "fff999"},
    ]
    assets_dir = tmp_path / "assets"
    mapping = save_resources(resources, assets_dir)
    assert "fff999" in mapping
    assert "fff999" in mapping["fff999"]
