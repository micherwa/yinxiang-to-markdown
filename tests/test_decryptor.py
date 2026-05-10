"""Tests for the decryptor module."""

import os
import base64
from pathlib import Path

import defusedxml.ElementTree as ET
import pytest

from src.decryptor import derive_key, decrypt_content, parse_notes_file


HMAC_KEY = b"{22C58AC3-F1C7-4D96-8B88-5E4BBF505817}"


def _find_sample_notes() -> list[Path]:
    """Return any *.notes files under input/ for integration testing.

    These are user-private files and are intentionally not checked into the
    repository. Tests that depend on them are skipped when none are present.
    """
    input_dir = Path("input")
    if not input_dir.exists():
        return []
    return sorted(input_dir.glob("*.notes"))


# --- Part A: Key Derivation ---


def test_derive_key_returns_16_bytes():
    nonce = os.urandom(16)
    key = derive_key(nonce, HMAC_KEY)
    assert isinstance(key, bytes)
    assert len(key) == 16


def test_derive_key_deterministic():
    nonce = b'\x01' * 16
    key1 = derive_key(nonce, HMAC_KEY)
    key2 = derive_key(nonce, HMAC_KEY)
    assert key1 == key2


def test_derive_key_different_nonce_different_key():
    key1 = derive_key(b'\x01' * 16, HMAC_KEY)
    key2 = derive_key(b'\x02' * 16, HMAC_KEY)
    assert key1 != key2


# --- Part B: Content Decryption ---


def test_decrypt_content_with_real_data():
    samples = _find_sample_notes()
    if not samples:
        pytest.skip("no sample .notes file in input/")
    tree = ET.parse(str(samples[0]))
    root = tree.getroot()
    notes = root.findall("note")
    if not notes:
        pytest.skip("sample .notes contains no <note> element")
    content_elem = notes[0].find("content")
    if content_elem is None or content_elem.get("encoding") != "base64:aes":
        pytest.skip("sample note is not AES-encrypted")
    raw = base64.b64decode(content_elem.text)
    decrypted = decrypt_content(raw)
    assert isinstance(decrypted, str)
    assert "en-note" in decrypted.lower() or "<!DOCTYPE" in decrypted


# --- Part C: Full .notes File Parsing ---


def test_parse_notes_file():
    samples = _find_sample_notes()
    if not samples:
        pytest.skip("no sample .notes file in input/")
    notes = parse_notes_file(samples[0])
    assert isinstance(notes, list)
    assert len(notes) > 0
    first = notes[0]
    for key in ("title", "content", "created", "updated", "resources"):
        assert key in first
    assert "en-note" in first["content"].lower() or "<!DOCTYPE" in first["content"]


def test_parse_notes_file_resources():
    """Find any sample with resources and verify the resource shape."""
    for sample in _find_sample_notes():
        notes = parse_notes_file(sample)
        notes_with_resources = [n for n in notes if len(n["resources"]) > 0]
        if notes_with_resources:
            res = notes_with_resources[0]["resources"][0]
            assert "mime" in res
            assert "data" in res
            assert isinstance(res["data"], bytes)
            return
    pytest.skip("no sample .notes file with resources in input/")
