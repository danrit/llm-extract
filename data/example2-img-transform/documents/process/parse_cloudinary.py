#!/usr/bin/env python3
"""Parse cloudinary.html into a clean markdown documentation."""

import json
import re
from pathlib import Path
from urllib.parse import unquote

from bs4 import BeautifulSoup, Comment, NavigableString, Tag


HTML_FILE = Path(__file__).parent / "cloudinary.html"
OUT_FILE = Path(__file__).parent / "cloudinary.md"

# Maps original HTML anchor names (for heading anchors) to GFM auto-slugs.
# Populated by build_heading_anchor_map() before the conversion pass.
HEADING_ANCHOR_MAP: dict[str, str] = {}


def gfm_slug(text: str) -> str:
    """Generate a GFM-compatible anchor slug from heading text (plain text input).

    Input must be plain text (already extracted via get_text()), NOT raw HTML.
    Matches github-slugger behaviour on the decoded text:
      - lowercase
      - spaces → hyphens
      - remove chars that aren't [a-z0-9_-]  (angle brackets, dots, parens, etc.)
      - collapse multiple hyphens, strip leading/trailing
    """
    s = text.lower()
    s = re.sub(r"\s+", "-", s)           # spaces → hyphens
    s = re.sub(r"[^\w-]", "", s)         # keep only word chars and hyphens
    s = re.sub(r"-+", "-", s)            # collapse multiple hyphens
    return s.strip("-")


def build_heading_anchor_map(soup: BeautifulSoup) -> dict[str, str]:
    """Map every HTML anchor name that precedes a heading to its GFM slug.

    Only the outer document is scanned; anchors inside <script type="text/html">
    templates are invisible to find_all and are handled as standalone anchors
    during the conversion pass.
    """
    slug_counter: dict[str, int] = {}
    mapping: dict[str, str] = {}

    for a in soup.find_all("a", {"name": True}):
        name = a.get("name")
        if not name or a.get_text(strip=True):
            continue  # skip anchors with visible text

        # Walk forward to find the immediately following sibling element
        nxt = a.next_sibling
        while nxt and isinstance(nxt, NavigableString) and not nxt.strip():
            nxt = nxt.next_sibling

        if not (isinstance(nxt, Tag) and nxt.name in ("h1", "h2", "h3", "h4", "h5", "h6")):
            continue  # not a heading anchor

        heading_text = nxt.get_text(strip=True)
        slug = gfm_slug(heading_text) or name.replace("_", "-")

        # GFM deduplication: first occurrence is bare slug, subsequent get -1, -2, …
        if slug not in slug_counter:
            slug_counter[slug] = 0
            final = slug
        else:
            slug_counter[slug] += 1
            final = f"{slug}-{slug_counter[slug]}"

        mapping[name] = final

    return mapping


def decode_snippets(data_props: str) -> str | None:
    """Extract only the URL snippet from a cld-sdk-code-snippets data-props value."""
    try:
        data = json.loads(unquote(data_props))
        snippets = data.get("snippets", [])
        for s in snippets:
            if s.get("language") == "URL":
                versions = s.get("versions", [])
                if versions:
                    return versions[0].get("snippet")
    except Exception:
        pass
    return None


def table_to_md(table: Tag) -> str:
    """Convert an HTML table to markdown."""
    lines = []
    thead = table.find("thead")
    tbody = table.find("tbody")

    if thead:
        headers = [th.get_text(strip=True) for th in thead.find_all("th")]
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    if tbody:
        for row in tbody.find_all("tr"):
            cells = []
            for td in row.find_all("td"):
                cell_text = element_to_md(td).strip()
                cell_text = cell_text.replace("\n", " ").replace("|", "\\|")
                cells.append(cell_text)
            lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines)


def element_to_md(el: Tag | NavigableString, depth: int = 0) -> str:
    """Recursively convert a BeautifulSoup element to markdown text."""
    if isinstance(el, Comment):
        return ""
    if isinstance(el, NavigableString):
        return str(el)

    tag = el.name
    if tag is None:
        return ""

    classes = el.get("class", [])
    if isinstance(classes, str):
        classes = [classes]

    skip_classes = {
        "markdown-actions", "mobile-active-submenu", "sidebar-holder-wrapper",
        "sidebar-holder", "sidebar-desktop", "content-img-outer-wrapper",
        "content-img-inner-wrapper", "agent-skills-popover", "banner",
        "updated-at", "llms-directive",
    }
    if any(c in skip_classes for c in classes):
        return ""

    if "md_autotoc" in classes:
        return ""

    if tag == "img":
        return ""

    if tag == "script":
        return ""

    if tag == "style":
        return ""

    if tag == "svg":
        return ""

    # Code snippet blocks — keep only the URL variant
    if "cld-sdk-code-snippets" in classes or "cld-sdk-code-snippets-placeholder" in classes:
        data_props = el.get("data-props") or el.get("data-payload")
        if data_props:
            url = decode_snippets(data_props)
            if url:
                return f"\n```\n{url}\n```\n"
        return ""

    # js-template: parse the embedded <script type="text/html"> as HTML
    if "js-template" in classes:
        script = el.find("script", {"type": "text/html"})
        if script:
            inner_html = script.string or ""
            inner_soup = BeautifulSoup(inner_html, "html.parser")
            return elements_to_md(inner_soup.contents, depth)
        return ""

    if tag == "table":
        return "\n" + table_to_md(el) + "\n"

    # Headings — GFM auto-generates the anchor from heading text, no <a id> needed.
    # Angle brackets must be HTML-encoded so GFM treats them as literal characters
    # (raw <> in a heading would be parsed as inline HTML, producing an empty text
    # node and thus an empty/missing auto-anchor).
    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        level = int(tag[1])
        text = el.get_text(strip=True).replace("<", "&lt;").replace(">", "&gt;")
        prefix = "#" * level
        return f"\n{prefix} {text}\n"

    # Anchor tags
    if tag == "a":
        name = el.get("name")
        href = el.get("href", "")
        inner = "".join(element_to_md(c, depth) for c in el.children)

        if name and not inner.strip():
            # Pure anchor (no visible text).
            if name in HEADING_ANCHOR_MAP:
                # This anchor is for a heading — GFM handles it automatically, skip.
                return ""
            # Standalone anchor (e.g. #dot_rotation, #codec_note) — needs an
            # explicit HTML tag since there is no heading to auto-generate it.
            return f'<a id="{name}"></a>'

        if href and inner.strip():
            # Rewrite in-page links that target heading anchors to their GFM slug.
            if href.startswith("#"):
                anchor_name = href[1:]
                if anchor_name in HEADING_ANCHOR_MAP:
                    href = "#" + HEADING_ANCHOR_MAP[anchor_name]
            # Encode angle brackets in link text so GFM renders them literally.
            link_text = inner.strip().replace("<", "&lt;").replace(">", "&gt;")
            return f"[{link_text}]({href})"

        return inner

    if tag == "code":
        return f"`{el.get_text()}`"

    if tag == "pre":
        code = el.find("code")
        if code:
            lang = ""
            for cls in (code.get("class") or []):
                if cls.startswith("language-"):
                    lang = cls[9:]
                    break
            return f"\n```{lang}\n{code.get_text()}\n```\n"
        return f"\n```\n{el.get_text()}\n```\n"

    if tag == "p":
        inner = "".join(element_to_md(c, depth) for c in el.children).strip()
        return f"\n{inner}\n" if inner else ""

    if tag in ("strong", "b"):
        inner = "".join(element_to_md(c, depth) for c in el.children).strip()
        return f"**{inner}**"

    if tag in ("em", "i"):
        inner = "".join(element_to_md(c, depth) for c in el.children).strip()
        return f"*{inner}*"

    if tag in ("ul", "ol"):
        items = []
        for i, li in enumerate(el.find_all("li", recursive=False)):
            prefix = "-" if tag == "ul" else f"{i + 1}."
            content = elements_to_md(li.contents, depth + 1).strip()
            indented = content.replace("\n", "\n  ")
            items.append(f"{prefix} {indented}")
        return "\n" + "\n".join(items) + "\n"

    if tag in ("blockquote",) or "md_special" in classes:
        inner = elements_to_md(el.contents, depth).strip()
        if not inner:
            return ""
        quoted = "\n".join(f"> {l}" for l in inner.split("\n"))
        return f"\n{quoted}\n"

    if tag == "hr":
        return "\n---\n"

    if tag == "br":
        return "\n"

    return elements_to_md(el.contents, depth)


def elements_to_md(children, depth: int = 0) -> str:
    return "".join(element_to_md(child, depth) for child in children)


def remove_troubleshooting_section(soup: BeautifulSoup) -> None:
    """Remove the Troubleshooting transformation errors section."""
    anchor = soup.find("a", {"name": "troubleshooting_transformation_errors"})
    if not anchor:
        return

    h2 = anchor.find_next("h2") or anchor.find_parent("h2")
    if not h2:
        return

    # Remove from the h2 until the next h2, but stop before any <a name="...">
    # that immediately precedes the next section heading (to avoid deleting it).
    to_remove = [anchor, h2]
    node = h2.next_sibling
    while node:
        next_node = node.next_sibling
        if isinstance(node, Tag) and node.name == "h2":
            break
        if isinstance(node, Tag) and node.name == "a" and node.get("name"):
            following = node.next_sibling
            while following and isinstance(following, NavigableString) and not following.strip():
                following = following.next_sibling
            if isinstance(following, Tag) and following.name == "h2":
                break
        to_remove.append(node)
        node = next_node

    for el in to_remove:
        if el.parent:
            el.extract()


def main():
    global HEADING_ANCHOR_MAP

    html = HTML_FILE.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    remove_troubleshooting_section(soup)

    # First pass: build heading anchor → GFM slug map
    HEADING_ANCHOR_MAP = build_heading_anchor_map(soup)

    content_div = soup.find("div", class_="docs_content_col")
    if not content_div:
        raise RuntimeError("Could not find docs_content_col div")

    header_div = soup.find("div", class_="docs-header-wrapper")
    title = ""
    if header_div:
        h1 = header_div.find("h1")
        if h1:
            title = f"# {h1.get_text(strip=True)}\n\n"

    md = title + elements_to_md(content_div.contents)

    # Strip stray DOCTYPE/html declarations left by inner HTML reparsing
    md = re.sub(r"html PUBLIC[^\n]*\n?", "", md)
    md = re.sub(r"<!DOCTYPE[^\n]*\n?", "", md, flags=re.IGNORECASE)

    # Normalise whitespace
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = "\n".join(l.rstrip() for l in md.split("\n"))
    md = md.strip() + "\n"

    OUT_FILE.write_text(md, encoding="utf-8")
    print(f"Written to {OUT_FILE} ({len(md)} chars, {md.count(chr(10))} lines)")


if __name__ == "__main__":
    main()
