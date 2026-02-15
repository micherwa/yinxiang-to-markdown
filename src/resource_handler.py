from pathlib import Path
from typing import Any

MIME_EXT_MAP = {
    "image/png": ".png",
    "image/jpeg": ".jpeg",
    "image/jpg": ".jpg",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
    "image/bmp": ".bmp",
    "application/pdf": ".pdf",
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
    "video/mp4": ".mp4",
    "text/plain": ".txt",
    "text/html": ".html",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
}


def mime_to_ext(mime: str) -> str:
    return MIME_EXT_MAP.get(mime, ".bin")


def save_resources(resources: list[dict[str, Any]], assets_dir: Path) -> dict[str, str]:
    assets_dir.mkdir(parents=True, exist_ok=True)
    mapping: dict[str, str] = {}
    used_names: set[str] = set()
    for res in resources:
        md5 = res["md5"]
        data = res["data"]
        mime = res["mime"]
        original_name = res.get("filename", "")
        if original_name:
            name = original_name
        else:
            ext = mime_to_ext(mime)
            name = f"{md5}{ext}"
        name = _unique_name(name, used_names)
        used_names.add(name)
        filepath = assets_dir / name
        filepath.write_bytes(data)
        mapping[md5] = name
    return mapping


def _unique_name(name: str, used: set[str]) -> str:
    if name not in used:
        return name
    stem = Path(name).stem
    suffix = Path(name).suffix
    counter = 1
    while True:
        candidate = f"{stem}_{counter}{suffix}"
        if candidate not in used:
            return candidate
        counter += 1
