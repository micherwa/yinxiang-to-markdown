"""Decryptor for Evernote/Yinxiang .notes files."""

import base64
import hashlib
import hmac
import logging
from pathlib import Path
from typing import Optional, Union
from xml.etree.ElementTree import Element

import defusedxml.ElementTree as ET

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

HMAC_KEY = b"{22C58AC3-F1C7-4D96-8B88-5E4BBF505817}"
SIGNATURE = b"ENC0"


def derive_key(nonce: bytes, hmac_key: bytes) -> bytes:
    """Derive a 16-byte AES key from nonce using 50,000 rounds of HMAC-SHA256."""
    # Pad nonce to 20 bytes: nonce[:16] + 4 zero bytes, then set byte[19] = 1
    padded = bytearray(20)
    padded[:16] = nonce[:16]
    padded[19] = 1
    current = bytes(padded)

    key = bytearray(16)
    for _ in range(50000):
        digest = hmac.new(hmac_key, current, hashlib.sha256).digest()
        for j in range(16):
            key[j] ^= digest[j]
        current = digest

    return bytes(key)


def _decrypt_content_raw(data: bytes) -> bytes:
    """Decrypt AES-encrypted data and return raw bytes (with padding removed)."""
    if len(data) < 84:  # 4 + 16 + 16 + 16 + 32 minimum
        raise ValueError("Data too short")

    if data[:4] != SIGNATURE:
        raise ValueError("Invalid signature")

    nonce1 = data[4:20]
    nonce2 = data[20:36]
    iv = data[36:52]
    encrypted_data = data[52:-32]
    stored_hash = data[-32:]

    key1 = derive_key(nonce1, HMAC_KEY)
    key2 = derive_key(nonce2, HMAC_KEY)

    data_to_verify = data[:-32]
    computed_hash = hmac.new(key2, data_to_verify, hashlib.sha256).digest()
    if not hmac.compare_digest(computed_hash, stored_hash):
        raise ValueError("HMAC verification failed")

    cipher = Cipher(
        algorithms.AES(key1),
        modes.CBC(iv),
        backend=default_backend(),
    )
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(encrypted_data) + decryptor.finalize()

    # Remove PKCS7 padding
    pad_len = decrypted[-1]
    if not (1 <= pad_len <= 16):
        raise ValueError("Invalid PKCS7 padding")
    for i in range(pad_len):
        if decrypted[-(i + 1)] != pad_len:
            raise ValueError("Invalid PKCS7 padding")
    decrypted = decrypted[:-pad_len]

    return decrypted


def decrypt_content(data: bytes) -> str:
    """Decrypt AES-encrypted note content and return UTF-8 string."""
    return _decrypt_content_raw(data).decode("utf-8")


def _parse_resource(res_elem: Element) -> Optional[dict]:
    """Parse a resource element into a dict with data, mime, filename, md5."""
    data_elem = res_elem.find("data")
    if data_elem is None or data_elem.text is None:
        return None

    encoding = data_elem.get("encoding", "base64")
    try:
        raw = base64.b64decode(data_elem.text)
    except Exception as e:
        logger.warning("resource: base64 decode failed (%s); skipping", e)
        return None

    if encoding == "base64:aes":
        try:
            raw = _decrypt_content_raw(raw)
            # Resources are typically binary; if we got valid UTF-8 text, keep as bytes
            if not isinstance(raw, bytes):
                raw = raw.encode("utf-8") if raw else b""
        except Exception as e:
            logger.warning(
                "resource: AES decryption failed (%s); falling back to raw base64", e
            )
            try:
                raw = base64.b64decode(data_elem.text)
            except Exception as inner:
                logger.warning("resource: fallback base64 decode also failed (%s); skipping", inner)
                return None

    mime_elem = res_elem.find("mime")
    mime = mime_elem.text if mime_elem is not None and mime_elem.text else ""

    filename = ""
    res_attrs = res_elem.find("resource-attributes")
    if res_attrs is not None:
        fn_elem = res_attrs.find("file-name")
        if fn_elem is not None and fn_elem.text:
            filename = fn_elem.text

    md5_hash = hashlib.md5(raw).hexdigest()

    return {
        "data": raw,
        "mime": mime,
        "filename": filename,
        "md5": md5_hash,
    }


def parse_notes_file(filepath: Union[str, Path]) -> list[dict]:
    """Parse a .notes file and return list of note dicts."""
    path = Path(filepath)
    tree = ET.parse(path)
    root = tree.getroot()

    notes = []
    for note_elem in root.findall("note"):
        title_elem = note_elem.find("title")
        title = title_elem.text or "" if title_elem is not None else ""

        content_elem = note_elem.find("content")
        content = ""
        if content_elem is not None and content_elem.text:
            encoding = content_elem.get("encoding", "")
            if encoding == "base64:aes":
                try:
                    raw = base64.b64decode(content_elem.text)
                    content = decrypt_content(raw)
                except Exception as e:
                    logger.warning(
                        "note %r: content decryption failed (%s); keeping ciphertext",
                        title,
                        e,
                    )
                    content = content_elem.text
            else:
                content = content_elem.text

        created_elem = note_elem.find("created")
        created = created_elem.text or "" if created_elem is not None else ""

        updated_elem = note_elem.find("updated")
        updated = updated_elem.text or "" if updated_elem is not None else ""

        tags = []
        for tag_elem in note_elem.findall("tag"):
            if tag_elem.text:
                tags.append(tag_elem.text)

        resources = []
        for res_elem in note_elem.findall("resource"):
            res = _parse_resource(res_elem)
            if res is not None:
                resources.append(res)

        notes.append({
            "title": title,
            "content": content,
            "created": created,
            "updated": updated,
            "tags": tags,
            "resources": resources,
        })

    return notes
