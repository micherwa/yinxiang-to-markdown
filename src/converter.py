"""ENML to Markdown converter."""

import re
import warnings
from urllib.parse import quote
from bs4 import BeautifulSoup, NavigableString, Tag, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


def enml_to_markdown(enml: str, resource_map: dict[str, str]) -> str:
    """Convert ENML (Evernote Markup Language) to Markdown.

    Args:
        enml: ENML content (HTML variant).
        resource_map: md5_hash -> filename for replacing <en-media> references.

    Returns:
        Markdown string.
    """
    soup = BeautifulSoup(enml, "lxml")
    root = soup.find("en-note") or soup
    parts: list[str] = []
    _convert_element(root, resource_map, parts)
    result = "".join(parts)
    result = _clean_blank_lines(result)
    return result.strip()


def _convert_element(element, resource_map: dict[str, str], parts: list[str]) -> None:
    """Recursively convert a DOM element to Markdown."""
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

    # Handle block-level elements that need newlines
    if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
        level = int(name[1])
        prefix = "#" * level
        text = _get_text_content(element)
        parts.append(f"\n{prefix} {text}\n")
        return

    if name == "hr":
        parts.append("\n---\n")
        return

    if name == "pre":
        text = element.get_text()
        parts.append(f"\n```\n{text}\n```\n")
        return

    if name == "br":
        parts.append("\n")
        return

    if name == "table":
        _convert_table(element, parts)
        return

    if name == "ul":
        for li in element.find_all("li", recursive=False):
            text = _get_text_content(li)
            parts.append(f"\n- {text}")
        parts.append("\n")
        return

    if name == "ol":
        for i, li in enumerate(element.find_all("li", recursive=False), start=1):
            text = _get_text_content(li)
            parts.append(f"\n{i}. {text}")
        parts.append("\n")
        return

    if name == "en-todo":
        checked = element.get("checked", "").lower() == "true"
        checkbox = "- [x] " if checked else "- [ ] "
        # Get sibling text (text after the tag in the same parent)
        label_parts: list[str] = []
        for sib in element.next_siblings:
            if isinstance(sib, NavigableString):
                label_parts.append(str(sib))
            elif isinstance(sib, Tag) and sib.name not in ("en-todo",):
                label_parts.append(_get_text_content(sib))
                break
            else:
                break
        label = "".join(label_parts).strip()
        parts.append(f"\n{checkbox}{label}\n")
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

    # Inline elements
    if name == "b" or name == "strong":
        text = _get_text_content(element)
        parts.append(f"**{text}**")
        return

    if name == "i" or name == "em":
        text = _get_text_content(element)
        parts.append(f"*{text}*")
        return

    if name == "a":
        href = element.get("href", "")
        text = _get_text_content(element)
        parts.append(f"[{text}]({href})")
        return

    if name == "code":
        text = element.get_text()
        parts.append(f"`{text}`")
        return

    # Container tags: div, p, span, en-note - recurse into children
    if name in ("div", "p", "span", "en-note", "body", "html"):
        for child in element.children:
            _convert_element(child, resource_map, parts)
        # Add newline after block containers
        if name in ("div", "p", "en-note"):
            parts.append("\n")
        return

    # tr, td, th - handled inside table
    if name in ("tr", "td", "th"):
        for child in element.children:
            _convert_element(child, resource_map, parts)
        return

    # li - handled in ul/ol
    if name == "li":
        for child in element.children:
            _convert_element(child, resource_map, parts)
        return

    # Default: recurse
    for child in element.children:
        _convert_element(child, resource_map, parts)


def _get_text_content(element) -> str:
    """Extract plain text from an element (recursive)."""
    if isinstance(element, NavigableString):
        return str(element)
    if isinstance(element, Tag):
        return element.get_text()
    return ""


def _convert_table(table: Tag, parts: list[str]) -> None:
    """Convert HTML table to Markdown table."""
    rows: list[list[str]] = []
    trs = table.find_all("tr")
    for tr in trs:
        cells: list[str] = []
        for cell in tr.find_all(["td", "th"]):
            cells.append(_get_text_content(cell).strip())
        if cells:
            rows.append(cells)

    if not rows:
        return

    parts.append("\n")
    # First row as header
    header = rows[0]
    parts.append("| " + " | ".join(header) + " |\n")
    parts.append("| " + " | ".join("---" for _ in header) + " |\n")
    for row in rows[1:]:
        # Pad row to same length as header if needed
        while len(row) < len(header):
            row.append("")
        parts.append("| " + " | ".join(row[: len(header)]) + " |\n")
    parts.append("\n")


def _clean_blank_lines(text: str) -> str:
    """Replace more than 2 consecutive newlines with at most 2."""
    return re.sub(r"\n{3,}", "\n\n", text)
