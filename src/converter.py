"""ENML to Markdown converter."""

import re
import warnings
from urllib.parse import quote
from bs4 import BeautifulSoup, NavigableString, Tag, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# Block-level container tags whose children should each end with a newline
_BLOCK_CONTAINERS = {"div", "p", "en-note", "body", "html"}


def enml_to_markdown(enml: str, resource_map: dict) -> str:
    """Convert ENML (Evernote Markup Language) to Markdown.

    Args:
        enml: ENML content (HTML variant).
        resource_map: md5_hash -> filename for replacing <en-media> references.

    Returns:
        Markdown string.
    """
    soup = BeautifulSoup(enml, "lxml")
    root = soup.find("en-note") or soup
    parts: list = []
    _convert_element(root, resource_map, parts, list_depth=0)
    result = "".join(parts)
    result = _clean_blank_lines(result)
    return result.strip()


def _convert_element(element, resource_map: dict, parts: list, *, list_depth: int) -> None:
    """Recursively convert a DOM element to Markdown.

    list_depth lets nested ul/ol indent correctly.
    """
    if isinstance(element, NavigableString):
        text = str(element)
        if text.strip():
            parts.append(text)
        return

    if not isinstance(element, Tag):
        return

    name = element.name
    if name is None:
        return

    # --- Block-level ---

    if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
        level = int(name[1])
        text = _get_text_content(element)
        parts.append(f"\n{'#' * level} {text}\n")
        return

    if name == "hr":
        parts.append("\n---\n")
        return

    if name == "pre":
        parts.append(f"\n```\n{element.get_text()}\n```\n")
        return

    if name == "br":
        parts.append("\n")
        return

    if name == "blockquote":
        inner_parts: list = []
        for child in element.children:
            _convert_element(child, resource_map, inner_parts, list_depth=list_depth)
        inner = _clean_blank_lines("".join(inner_parts)).strip()
        if inner:
            quoted = "\n".join(f"> {ln}" if ln else ">" for ln in inner.split("\n"))
            parts.append(f"\n{quoted}\n")
        return

    if name == "table":
        _convert_table(element, parts)
        return

    if name in ("ul", "ol"):
        _convert_list(element, resource_map, parts, list_depth=list_depth)
        return

    if name == "en-todo":
        # Just emit the checkbox prefix; the surrounding container (typically
        # <div>) is responsible for the label and trailing newline.
        checked = element.get("checked", "").lower() == "true"
        parts.append("- [x] " if checked else "- [ ] ")
        return

    if name == "en-media":
        hash_val = element.get("hash", "")
        mime = element.get("type", "")
        filename = resource_map.get(hash_val)
        if filename:
            encoded = quote(filename)
            if mime.startswith("image/"):
                parts.append(f"![{filename}](./assets/{encoded})")
            else:
                parts.append(f"[{filename}](./assets/{encoded})")
        else:
            parts.append(f"附件({hash_val})" if hash_val else "附件")
        return

    # --- Inline ---

    if name in ("b", "strong"):
        parts.append(f"**{_get_text_content(element)}**")
        return

    if name in ("i", "em"):
        parts.append(f"*{_get_text_content(element)}*")
        return

    if name in ("del", "strike", "s"):
        parts.append(f"~~{_get_text_content(element)}~~")
        return

    if name == "u":
        # Markdown has no native underline; keep raw HTML (Obsidian renders it).
        parts.append(f"<u>{_get_text_content(element)}</u>")
        return

    if name in ("sub", "sup"):
        parts.append(f"<{name}>{_get_text_content(element)}</{name}>")
        return

    if name == "a":
        href = element.get("href", "")
        parts.append(f"[{_get_text_content(element)}]({href})")
        return

    if name == "code":
        parts.append(f"`{element.get_text()}`")
        return

    # --- Containers / fall-through ---

    if name in _BLOCK_CONTAINERS:
        for child in element.children:
            _convert_element(child, resource_map, parts, list_depth=list_depth)
        if name in ("div", "p", "en-note"):
            parts.append("\n")
        return

    # tr/td/th — handled by _convert_table; if reached standalone, just recurse
    if name in ("tr", "td", "th", "li"):
        for child in element.children:
            _convert_element(child, resource_map, parts, list_depth=list_depth)
        return

    # Unknown tag: recurse into children
    for child in element.children:
        _convert_element(child, resource_map, parts, list_depth=list_depth)


def _convert_list(list_elem: Tag, resource_map: dict, parts: list, *, list_depth: int) -> None:
    """Convert <ul>/<ol> to Markdown, with nested-list indentation support.

    Handles two structures for nested lists:
    1. Standard: <ul><li>x<ul>...</ul></li></ul>           (nested inside <li>)
    2. Evernote HTML export: <ul><li>x</li><ul>...</ul></ul>  (nested as sibling of <li>)

    In case 2 the sibling <ul>/<ol> is attached to the preceding <li>. An orphan
    sibling list with no preceding <li> is rendered one level deeper as a
    standalone list.
    """
    indent = "  " * list_depth
    is_ordered = list_elem.name == "ol"

    # Group direct children: each <li> may pick up subsequent sibling <ul>/<ol>
    # as its nested children (Evernote export pattern).
    groups: list = []  # list of (li_tag, [sibling_nested_list, ...])
    orphan_nested: list = []  # sibling lists appearing before any <li>
    for child in list_elem.children:
        if not isinstance(child, Tag):
            continue
        if child.name == "li":
            groups.append((child, []))
        elif child.name in ("ul", "ol"):
            if groups:
                groups[-1][1].append(child)
            else:
                orphan_nested.append(child)

    for orphan in orphan_nested:
        _convert_list(orphan, resource_map, parts, list_depth=list_depth + 1)

    for i, (li, sibling_nested) in enumerate(groups, start=1):
        marker = f"{i}." if is_ordered else "-"
        inline_parts: list = []
        nested_parts: list = []
        for child in li.children:
            if isinstance(child, Tag) and child.name in ("ul", "ol"):
                _convert_list(
                    child, resource_map, nested_parts, list_depth=list_depth + 1
                )
            else:
                _convert_element(child, resource_map, inline_parts, list_depth=list_depth)
        for sib in sibling_nested:
            _convert_list(sib, resource_map, nested_parts, list_depth=list_depth + 1)
        inline_text = "".join(inline_parts).strip().replace("\n", " ")
        parts.append(f"\n{indent}{marker} {inline_text}".rstrip())
        if nested_parts:
            parts.append("".join(nested_parts))
    if list_depth == 0:
        parts.append("\n")


def _get_text_content(element) -> str:
    """Extract plain text from an element (recursive)."""
    if isinstance(element, NavigableString):
        return str(element)
    if isinstance(element, Tag):
        return element.get_text()
    return ""


def _convert_table(table: Tag, parts: list) -> None:
    """Convert HTML table to Markdown table."""
    rows: list = []
    for tr in table.find_all("tr"):
        cells: list = []
        for cell in tr.find_all(["td", "th"]):
            cells.append(_get_text_content(cell).strip().replace("\n", " "))
        if cells:
            rows.append(cells)

    if not rows:
        return

    parts.append("\n")
    header = rows[0]
    parts.append("| " + " | ".join(header) + " |\n")
    parts.append("| " + " | ".join("---" for _ in header) + " |\n")
    for row in rows[1:]:
        while len(row) < len(header):
            row.append("")
        parts.append("| " + " | ".join(row[: len(header)]) + " |\n")
    parts.append("\n")


def _clean_blank_lines(text: str) -> str:
    """Replace more than 2 consecutive newlines with at most 2."""
    return re.sub(r"\n{3,}", "\n\n", text)
