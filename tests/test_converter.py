from src.converter import enml_to_markdown


def test_plain_text():
    enml = '<en-note><div>Hello World</div></en-note>'
    md = enml_to_markdown(enml, {})
    assert "Hello World" in md


def test_bold_italic():
    enml = '<en-note><div><b>bold</b> and <i>italic</i></div></en-note>'
    md = enml_to_markdown(enml, {})
    assert "**bold**" in md
    assert "*italic*" in md


def test_link():
    enml = '<en-note><div><a href="https://example.com">click</a></div></en-note>'
    md = enml_to_markdown(enml, {})
    assert "[click](https://example.com)" in md


def test_headings():
    enml = '<en-note><h1>Title</h1><h2>Sub</h2></en-note>'
    md = enml_to_markdown(enml, {})
    assert "# Title" in md
    assert "## Sub" in md


def test_unordered_list():
    enml = '<en-note><ul><li>a</li><li>b</li></ul></en-note>'
    md = enml_to_markdown(enml, {})
    assert "- a" in md
    assert "- b" in md


def test_ordered_list():
    enml = '<en-note><ol><li>first</li><li>second</li></ol></en-note>'
    md = enml_to_markdown(enml, {})
    assert "1." in md


def test_horizontal_rule():
    enml = '<en-note><div>above</div><hr/><div>below</div></en-note>'
    md = enml_to_markdown(enml, {})
    assert "---" in md


def test_code_block():
    enml = '<en-note><pre>code here</pre></en-note>'
    md = enml_to_markdown(enml, {})
    assert "```" in md
    assert "code here" in md


def test_todo_unchecked():
    enml = '<en-note><div><en-todo checked="false"/>Task A</div></en-note>'
    md = enml_to_markdown(enml, {})
    assert "- [ ]" in md
    assert "Task A" in md


def test_todo_checked():
    enml = '<en-note><div><en-todo checked="true"/>Task B</div></en-note>'
    md = enml_to_markdown(enml, {})
    assert "- [x]" in md
    assert "Task B" in md


def test_en_media_image():
    enml = '<en-note><en-media hash="abc123" type="image/png"/></en-note>'
    resource_map = {"abc123": "screenshot.png"}
    md = enml_to_markdown(enml, resource_map)
    assert "![screenshot.png](./assets/screenshot.png)" in md


def test_en_media_pdf():
    enml = '<en-note><en-media hash="def456" type="application/pdf"/></en-note>'
    resource_map = {"def456": "report.pdf"}
    md = enml_to_markdown(enml, resource_map)
    assert "[report.pdf](./assets/report.pdf)" in md


def test_en_media_missing():
    enml = '<en-note><en-media hash="unknown" type="image/png"/></en-note>'
    md = enml_to_markdown(enml, {})
    assert "附件" in md or "unknown" in md


def test_table():
    enml = '<en-note><table><tr><th>Name</th><th>Age</th></tr><tr><td>Alice</td><td>30</td></tr></table></en-note>'
    md = enml_to_markdown(enml, {})
    assert "| Name | Age |" in md
    assert "| --- | --- |" in md
    assert "| Alice | 30 |" in md


def test_blockquote():
    enml = '<en-note><blockquote>quoted text</blockquote></en-note>'
    md = enml_to_markdown(enml, {})
    assert "> quoted text" in md


def test_blockquote_multiline():
    enml = '<en-note><blockquote><div>line one</div><div>line two</div></blockquote></en-note>'
    md = enml_to_markdown(enml, {})
    assert "> line one" in md
    assert "> line two" in md


def test_strikethrough_del():
    enml = '<en-note><del>gone</del></en-note>'
    md = enml_to_markdown(enml, {})
    assert "~~gone~~" in md


def test_strikethrough_s():
    enml = '<en-note><s>obsolete</s></en-note>'
    md = enml_to_markdown(enml, {})
    assert "~~obsolete~~" in md


def test_underline_kept_as_html():
    enml = '<en-note><u>important</u></en-note>'
    md = enml_to_markdown(enml, {})
    assert "<u>important</u>" in md


def test_subscript_superscript():
    enml = '<en-note>H<sub>2</sub>O and x<sup>2</sup></en-note>'
    md = enml_to_markdown(enml, {})
    assert "<sub>2</sub>" in md
    assert "<sup>2</sup>" in md


def test_nested_unordered_list():
    enml = '<en-note><ul><li>outer<ul><li>inner</li></ul></li></ul></en-note>'
    md = enml_to_markdown(enml, {})
    assert "- outer" in md
    assert "  - inner" in md


def test_en_todo_in_div():
    """en-todo inside a div should produce a checkbox followed by the div's text."""
    enml = '<en-note><div><en-todo checked="true"/>Task A</div><div><en-todo checked="false"/>Task B</div></en-note>'
    md = enml_to_markdown(enml, {})
    assert "- [x] Task A" in md
    assert "- [ ] Task B" in md
