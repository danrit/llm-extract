"""
Parse Cloudflare image transformation HTML docs into clean Markdown.

Rules:
- Keep only the main article content (sl-markdown-content)
- Remove navigation elements
- Remove image examples (img tags and their wrapper elements)
- For tab groups: keep only "URL format" panel; skip "Workers" panel
  - For other tab groups (e.g. Remote/Hosted), keep all panels
- Keep anchor links on headings
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup, Tag, NavigableString


INPUT = Path(__file__).parent / "cloudflare.html"
OUTPUT = Path(__file__).parent / "cloudflare.md"


def get_code_text(pre: Tag) -> str:
    """Extract plain text from an expressive-code <pre> block."""
    lines = []
    for line_div in pre.find_all("div", class_="ec-line"):
        lines.append(line_div.get_text())
    if lines:
        return "\n".join(lines)
    return pre.get_text()


def node_to_md(node, depth=0) -> str:
    """Recursively convert a BS4 node to Markdown text."""
    if isinstance(node, NavigableString):
        return str(node)

    tag = node.name

    # Skip SVG, scripts, styles, nav elements
    if tag in ("svg", "script", "style", "link", "button", "noscript"):
        return ""

    # Skip image zoom wrappers and plain images
    if tag == "starlight-image-zoom-zoomable":
        return ""
    if tag == "img":
        return ""

    # Handle starlight-tabs: only emit the "URL format" panel (or all if no Workers tab)
    if tag == "starlight-tabs":
        return handle_tabs(node)

    # Headings — preserve anchor id
    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        return handle_heading(node)

    # Paragraphs
    if tag == "p":
        inner = children_to_md(node)
        return f"\n{inner}\n"

    # Lists
    if tag == "ul":
        return handle_list(node, ordered=False)
    if tag == "ol":
        return handle_list(node, ordered=True)
    if tag == "li":
        return children_to_md(node)

    # Code inline
    if tag == "code":
        text = node.get_text()
        return f"`{text}`"

    # Code block (expressive-code wrapper)
    if tag == "div" and node.get("class") and "expressive-code" in node.get("class", []):
        return handle_code_block(node)

    # Pre fallback
    if tag == "pre":
        lang = node.get("data-language", "")
        text = get_code_text(node)
        return f"\n```{lang}\n{text}\n```\n"

    # Tables — skip image comparison tables (border:none + text-align:center = visual example table)
    if tag == "table":
        style = node.get("style", "")
        if "border:none" in style and "text-align:center" in style:
            return ""
        return handle_table(node)

    # Anchor links (inline)
    if tag == "a":
        href = node.get("href", "")
        anchor_id = node.get("id", "")
        text = children_to_md(node)
        # Heading icon anchors — skip
        if node.get("class") and "anchor-link" in node.get("class", []):
            return ""
        # Bare anchor tags (<a id="foo"></a>) — emit as raw HTML so in-page links work
        if anchor_id and not href and not text.strip():
            return f'<a id="{anchor_id}"></a>'
        if not text.strip():
            return ""
        if href.startswith("#") or href.startswith("/") or href.startswith("http"):
            return f"[{text}]({href})"
        return text

    # Strong / em
    if tag == "strong":
        return f"**{children_to_md(node)}**"
    if tag in ("em", "i"):
        return f"*{children_to_md(node)}*"

    # Details / summary (collapsible sections)
    if tag == "details":
        return handle_details(node)
    if tag == "summary":
        return children_to_md(node)

    # Blockquote / aside / callouts
    if tag in ("blockquote", "aside"):
        inner = children_to_md(node).strip()
        quoted = "\n".join(f"> {line}" for line in inner.splitlines())
        return f"\n{quoted}\n"

    # heading-wrapper divs
    if tag == "div" and node.get("class") and "heading-wrapper" in node.get("class", []):
        return children_to_md(node)

    # tablist-wrapper — skip (navigation)
    if tag == "div" and node.get("class") and "tablist-wrapper" in node.get("class", []):
        return ""

    # Generic block containers — recurse
    if tag in ("div", "section", "article", "main", "span", "figcaption", "figure"):
        return children_to_md(node)

    # hr
    if tag == "hr":
        return "\n---\n"

    # br
    if tag == "br":
        return "\n"

    # Fallback: recurse into children
    return children_to_md(node)


def children_to_md(node) -> str:
    parts = []
    for child in node.children:
        parts.append(node_to_md(child))
    return "".join(parts)


def handle_heading(node) -> str:
    level = int(node.name[1])
    prefix = "#" * level

    # Extract text, skip the icon anchor-link children
    text_parts = []
    for child in node.children:
        if isinstance(child, Tag) and child.get("class") and "anchor-link" in child.get("class", []):
            continue
        text_parts.append(node_to_md(child))
    text = "".join(text_parts).strip()

    # GFM auto-generates anchors from heading text — no {#id} needed
    return f"\n{prefix} {text}\n"


def handle_list(node, ordered=False) -> str:
    items = []
    for i, child in enumerate(node.children):
        if isinstance(child, Tag) and child.name == "li":
            content = node_to_md(child).strip()
            # Handle nested lists inside li
            if ordered:
                items.append(f"{i + 1}. {content}")
            else:
                items.append(f"- {content}")
    return "\n" + "\n".join(items) + "\n"


def handle_code_block(node) -> str:
    pre = node.find("pre")
    if not pre:
        return ""
    lang = pre.get("data-language", "")
    text = get_code_text(pre)
    return f"\n```{lang}\n{text}\n```\n"


def handle_table(node) -> str:
    rows = []
    header_done = False
    for tr in node.find_all("tr"):
        cells = []
        for cell in tr.find_all(["th", "td"]):
            # Remove images from cells
            for img in cell.find_all("starlight-image-zoom-zoomable"):
                img.decompose()
            for img in cell.find_all("img"):
                img.decompose()
            cells.append(children_to_md(cell).strip().replace("\n", " "))
        if not cells:
            continue
        row_str = "| " + " | ".join(cells) + " |"
        rows.append(row_str)
        if not header_done and tr.find("th"):
            sep = "| " + " | ".join(["---"] * len(cells)) + " |"
            rows.append(sep)
            header_done = True
    return "\n" + "\n".join(rows) + "\n"


def handle_details(node) -> str:
    summary = node.find("summary")
    summary_text = ""
    if summary:
        summary_text = children_to_md(summary).strip()

    # Get content after summary
    parts = []
    past_summary = False
    for child in node.children:
        if child == summary:
            past_summary = True
            continue
        if past_summary:
            parts.append(node_to_md(child))
    content = "".join(parts).strip()

    result = f"\n**{summary_text}**\n\n{content}\n"
    return result


def handle_tabs(node) -> str:
    """Process a starlight-tabs element.

    If tabs contain 'URL format', only emit that panel.
    If only 'Workers' tab(s) exist, skip entirely.
    For other tab patterns (e.g. Remote/Hosted), emit all panels.
    """
    tab_links = node.find_all("a", role="tab")
    labels = [a.get_text(strip=True) for a in tab_links]

    has_url_format = "URL format" in labels
    has_workers = "Workers" in labels

    panels = node.find_all("div", role="tabpanel")

    if has_url_format:
        url_idx = labels.index("URL format")
        if url_idx < len(panels):
            return children_to_md(panels[url_idx])
        return ""
    elif has_workers and not has_url_format:
        # Workers-only tab group — skip entirely
        return ""
    else:
        # Other tab groups (e.g. Remote/Hosted) — emit all panels with labels
        parts = []
        for label, panel in zip(labels, panels):
            parts.append(f"\n**{label}**\n")
            parts.append(children_to_md(panel))
        return "".join(parts)


def clean_markdown(text: str) -> str:
    """Post-process to clean up excessive blank lines and whitespace."""
    # Normalize line endings
    text = text.replace("\r\n", "\n")
    # Collapse 3+ blank lines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip trailing whitespace on each line
    lines = [line.rstrip() for line in text.splitlines()]
    text = "\n".join(lines)
    return text.strip() + "\n"


def parse(html_path: Path) -> str:
    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    article = soup.find("div", class_=lambda c: c and "sl-markdown-content" in c)
    if not article:
        raise ValueError("Could not find sl-markdown-content div")

    # Remove all images and their zoom wrappers before processing
    for zoom in article.find_all("starlight-image-zoom-zoomable"):
        zoom.decompose()
    for img in article.find_all("img"):
        img.decompose()

    md = children_to_md(article)
    return clean_markdown(md)


if __name__ == "__main__":
    result = parse(INPUT)
    OUTPUT.write_text(result, encoding="utf-8")
    print(f"Written {len(result)} chars to {OUTPUT}")
