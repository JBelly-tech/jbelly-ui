#!/usr/bin/env python3
"""The accessibility defects that make up most of the real ones, caught before anyone reads the page (Class D).

Every year the same handful of failures is found on most of the world's top home pages: text without
contrast, images without alternative text, links and buttons with nothing to announce, form fields
without a label, and pages that never say what language they are in. Contrast is measured by
verify_theme.py. This script catches the rest, and the structural faults a screen reader trips on
first: no <main> landmark (or two), no <h1> or a skipped heading level, an aria reference to an id that
does not exist, a duplicate id, a positive tabindex, an iframe without a title, a page with navigation
but no skip link.

It is static by default -- the standard-library parser on the file, so it runs on any machine -- and
with Playwright installed it renders the page first and applies the same rules to the DOM a reader
actually gets, which is the one that matters for shells that draw their content from templates.

Rules (each line names the element and its source line where the parser can give one):
  A01 LANG      <html> without a lang attribute
  A02 TITLE     no <title>, or an empty one
  A03 MAIN      no <main> (or role="main"), or more than one
  A04 H1        no <h1>, or more than one
  A05 HEADINGS  a heading level skipped (h2 followed by h4)
  A06 IMG-ALT   <img> without an alt attribute (alt="" is a valid answer: decorative)
  A07 LINK-NAME <a href> with no accessible name
  A08 BTN-NAME  <button> or role="button" with no accessible name
  A09 LABEL     a form control with no label, aria-label, aria-labelledby or title
  A10 ARIA-REF  aria-labelledby / describedby / controls / owns naming an id that is not in the document
  A11 DUP-ID    the same id on two elements
  A12 TABINDEX  a positive tabindex (it reorders the keyboard for everyone else)
  A13 IFRAME    <iframe> without a title
  A14 SKIP      a <nav> but no skip link (an in-page link before it, or one whose text says "skip")

Usage:
  python scripts/check_a11y.py <file.html> [--rendered] [--width 1440] [--json] [--quiet] [--ignore A04,A14]
Exit 1 on findings, 2 if the page could not be read or rendered when --rendered was asked for.
"""
import json
import os
import re
import sys
from html.parser import HTMLParser

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # labels may be Arabic
except Exception: pass

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
SKIP_SUBTREE = {"script", "style", "template", "noscript", "svg"}   # svg is a leaf below; its title is read
FIELD_TYPES_UNLABELLED = {"hidden", "submit", "button", "reset", "image"}


class Node:
    __slots__ = ("tag", "attrs", "children", "parent", "line", "text")

    def __init__(self, tag, attrs, parent, line):
        self.tag, self.attrs, self.parent, self.line = tag, dict(attrs), parent, line
        self.children, self.text = [], ""

    def get(self, name, default=None):
        v = self.attrs.get(name)
        return default if v is None else v

    def walk(self):
        yield self
        for c in self.children:
            if isinstance(c, Node):
                for n in c.walk():
                    yield n

    def all_text(self):
        parts = []
        for c in self.children:
            if isinstance(c, str):
                parts.append(c)
            elif c.tag not in ("script", "style", "template"):
                parts.append(c.all_text())
        return "".join(parts)


class Tree(HTMLParser):
    """A small DOM: enough structure for names, labels, headings and ids."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", [], None, 0)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur, self.getpos()[0])
        self.cur.children.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur, self.getpos()[0]))

    def handle_endtag(self, tag):
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.cur = n.parent

    def handle_data(self, data):
        if data:
            self.cur.children.append(data)


def parse(html):
    t = Tree()
    t.feed(html)
    t.close()
    return t.root


def hidden(n):
    """Anything a reader never meets is not judged: hidden, aria-hidden, inside a template/script."""
    while n is not None and n.tag != "#root":
        if "hidden" in n.attrs or n.get("aria-hidden", "").strip().lower() == "true" or n.tag in ("template", "script", "style", "noscript"):
            return True
        n = n.parent
    return False


def by_id(root):
    ids = {}
    for n in root.walk():
        i = n.get("id")
        if i:
            ids.setdefault(i.strip(), []).append(n)
    return ids


def name_of(n, ids):
    """An approximation of the accessible name: aria-labelledby, aria-label, own text, alt of
    images inside, an svg <title>, then title."""
    lb = n.get("aria-labelledby", "").split()
    if lb:
        txt = " ".join(ids[i][0].all_text() for i in lb if i in ids).strip()
        if txt:
            return txt
    al = n.get("aria-label", "").strip()
    if al:
        return al
    txt = n.all_text().strip()
    if txt:
        return txt
    for c in n.walk():
        if c is n:
            continue
        if c.tag == "img" and c.get("alt", "").strip():
            return c.get("alt").strip()
        if c.tag == "svg":
            for t in c.walk():
                if t.tag == "title" and t.all_text().strip():
                    return t.all_text().strip()
            if c.get("aria-label", "").strip():
                return c.get("aria-label").strip()
        if c.tag == "input" and c.get("type", "").lower() == "image" and c.get("alt", "").strip():
            return c.get("alt").strip()
    if n.tag == "input" and n.get("type", "").lower() in ("submit", "button", "reset") and n.get("value", "").strip():
        return n.get("value").strip()
    return n.get("title", "").strip()


def labelled(n, ids, label_for):
    if n.get("aria-label", "").strip() or n.get("title", "").strip():
        return True
    if any(i in ids for i in n.get("aria-labelledby", "").split()):
        return True
    i = n.get("id", "").strip()
    if i and i in label_for:
        return True
    p = n.parent
    while p is not None and p.tag != "#root":
        if p.tag == "label":
            return True
        p = p.parent
    return False


def check(root, ignore=()):
    findings = []

    def add(code, line, what, fix):
        if code not in ignore:
            findings.append({"rule": code, "line": line, "what": what, "fix": fix})

    ids = by_id(root)
    html = next((n for n in root.walk() if n.tag == "html"), None)
    if html is None or not html.get("lang", "").strip():
        add("A01", html.line if html else 1, "<html> has no lang", 'add lang="en" (or the page language) so screen readers pick the right voice')
    title = next((n for n in root.walk() if n.tag == "title" and not hidden(n)), None)
    if title is None or not title.all_text().strip():
        add("A02", title.line if title else 1, "no page <title>", "a <title> that names the page, then the product")
    mains = [n for n in root.walk() if (n.tag == "main" or n.get("role") == "main") and not hidden(n)]
    if len(mains) != 1:
        add("A03", mains[0].line if mains else 1, "%d <main> landmark(s)" % len(mains), "exactly one <main> around the page's own content")
    heads = [n for n in root.walk() if re.fullmatch(r"h[1-6]", n.tag) and not hidden(n)]
    h1s = [h for h in heads if h.tag == "h1"]
    if len(h1s) != 1:
        add("A04", h1s[0].line if h1s else 1, "%d <h1>" % len(h1s), "one <h1>: the page's subject")
    prev = 0
    for h in heads:
        lvl = int(h.tag[1])
        if prev and lvl > prev + 1:
            add("A05", h.line, "heading jumps from h%d to h%d" % (prev, lvl), "use the next level down; style it with a class if it must look smaller")
        prev = lvl
    for n in root.walk():
        if hidden(n):
            continue
        if n.tag == "img" and "alt" not in n.attrs:
            add("A06", n.line, "<img> without alt", 'alt="" when decorative, the meaning in words when not')
        if n.tag == "a" and "href" in n.attrs and not name_of(n, ids):
            add("A07", n.line, "link with no accessible name (href=%s)" % n.get("href", "")[:40], "visible text, or aria-label on the link, or alt on the image inside it")
        if (n.tag == "button" or n.get("role") == "button") and not name_of(n, ids):
            add("A08", n.line, "button with no accessible name", "visible text or aria-label; an icon alone announces nothing")
        if n.tag == "iframe" and not n.get("title", "").strip():
            add("A13", n.line, "<iframe> without title", "title that says what the frame holds")
        try:
            if int(n.get("tabindex", "0")) > 0:
                add("A12", n.line, "tabindex=%s" % n.get("tabindex"), "0 or -1; order the DOM instead")
        except ValueError:
            pass
        for attr in ("aria-labelledby", "aria-describedby", "aria-controls", "aria-owns"):
            for ref in n.get(attr, "").split():
                if ref not in ids:
                    add("A10", n.line, "%s=%s names no element" % (attr, ref), "point at an id that exists, or drop the attribute")
    label_for = {n.get("for", "").strip() for n in root.walk() if n.tag == "label" and n.get("for", "").strip()}
    for n in root.walk():
        if hidden(n):
            continue
        if n.tag in ("select", "textarea") or (n.tag == "input" and n.get("type", "text").lower() not in FIELD_TYPES_UNLABELLED):
            if not labelled(n, ids, label_for):
                add("A09", n.line, "%s%s without a label" % (n.tag, (" name=" + n.get("name")) if n.get("name") else ""), "<label for> pointing at it, or aria-label when the label is elsewhere")
    for i, nodes in ids.items():
        vis = [n for n in nodes if not hidden(n)]
        if len(vis) > 1:
            add("A11", vis[1].line, "id=%s used %d times" % (i, len(vis)), "ids are unique; aria and labels resolve to the first one only")
    navs = [n for n in root.walk() if n.tag == "nav" and not hidden(n)]
    if navs:
        links = [n for n in root.walk() if n.tag == "a" and "href" in n.attrs and not hidden(n)]
        skip = any(n.get("href", "").startswith("#") and ("skip" in name_of(n, ids).lower() or n.line < navs[0].line) for n in links[:5])
        if not skip:
            add("A14", navs[0].line, "navigation without a skip link", '<a href="#main" class="sr-only focus:not-sr-only ...">Skip to content</a> as the first focusable element')
    return findings


def render(path, width):
    from playwright.sync_api import sync_playwright
    url = "file:///" + os.path.abspath(path).replace("\\", "/")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": width, "height": 1000})
        pg.goto(url, wait_until="networkidle")
        pg.wait_for_timeout(400)
        html = pg.content()
        b.close()
    return html


def main():
    a = sys.argv[1:]
    if not a or "--help" in a or "-h" in a:
        print(__doc__.strip()); return 0 if a else 2
    path = a[0]
    if not os.path.isfile(path):
        print("[FAIL] no such file: %s" % path); return 2
    quiet, as_json, rendered = "--quiet" in a, "--json" in a, "--rendered" in a
    width = int(a[a.index("--width") + 1]) if "--width" in a else 1440
    ignore = set(a[a.index("--ignore") + 1].split(",")) if "--ignore" in a else set()
    mode = "static"
    if rendered:
        try:
            html = render(path, width)
            mode = "rendered"
        except ImportError:
            print("[NOTE] Playwright not installed: checking the static markup only")
            html = open(path, encoding="utf-8", errors="replace").read()
        except Exception as e:
            print("[FAIL] could not render %s: %s: %s" % (path, e.__class__.__name__, str(e).splitlines()[0])); return 2
    else:
        html = open(path, encoding="utf-8", errors="replace").read()
    findings = check(parse(html), ignore)
    summary = "check_a11y: %s, %d finding(s) -> %s" % (mode, len(findings), "FAIL" if findings else "PASS")
    if as_json:
        # stdout is the JSON and nothing else, so a caller can parse it; the verdict goes to stderr
        print(json.dumps({"page": path, "mode": mode, "findings": findings, "summary": summary}, indent=2, ensure_ascii=False))
        print(summary, file=sys.stderr)
        return 1 if findings else 0
    if not quiet:
        for f in findings:
            print("[FAIL] %s %s:%s  %s\n       fix: %s" % (f["rule"], os.path.basename(path), f["line"] if mode == "static" else "-", f["what"], f["fix"]))
    print(summary)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
