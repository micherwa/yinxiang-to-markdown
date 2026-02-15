"""Tests for the decryptor module."""

import os
import base64
import xml.etree.ElementTree as ET

from src.decryptor import derive_key, decrypt_content, parse_notes_file


HMAC_KEY = b"{22C58AC3-F1C7-4D96-8B88-5E4BBF505817}"


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
    tree = ET.parse("input/周报.notes")
    root = tree.getroot()
    note = root.findall("note")[0]
    content_elem = note.find("content")
    assert content_elem.get("encoding") == "base64:aes"
    raw = base64.b64decode(content_elem.text)
    decrypted = decrypt_content(raw)
    assert isinstance(decrypted, str)
    assert "en-note" in decrypted.lower() or "<!DOCTYPE" in decrypted


# --- Part C: Full .notes File Parsing ---


def test_parse_notes_file():
    notes = parse_notes_file("input/周报.notes")
    assert isinstance(notes, list)
    assert len(notes) == 24
    first = notes[0]
    assert "title" in first
    assert "content" in first
    assert "created" in first
    assert "updated" in first
    assert "resources" in first
    assert first["title"] == "2022-Q2"
    assert "en-note" in first["content"].lower() or "<!DOCTYPE" in first["content"]


def test_parse_notes_file_resources():
    # 广告业务.notes has notes with image resources
    notes = parse_notes_file("input/广告业务.notes")
    notes_with_resources = [n for n in notes if len(n["resources"]) > 0]
    assert len(notes_with_resources) > 0, "Need at least one note with resources"
    res = notes_with_resources[0]["resources"][0]
    assert "mime" in res
    assert "data" in res
    assert isinstance(res["data"], bytes)
