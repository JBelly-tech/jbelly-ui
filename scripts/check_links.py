#!/usr/bin/env python3
"""Fetch every link this project publishes, and fail on the ones that resolve to nothing.

Two links were dead here for a long time and nobody noticed, because nobody clicks every link in a
README: `https://www.designtokens.org/schema`, named as the `$schema` of the exported token file,
has never existed; and the site's "The recorded runs" button pointed at a directory that GitHub
Pages does not serve. A move between accounts adds a third kind -- a repository URL redirects after
a transfer, but a Pages site does not, so every absolute link to the old site dies silently.

By default this checks only the links this project controls: its own repository, its own site, and
every relative target on the site resolved against the deployed copy. Those cannot flake for
reasons outside the repository, which is what makes them safe to gate a build on. `--external`
adds the rest -- other people's sites, which move on their own schedule.

Usage: python scripts/check_links.py [--external] [--site URL] [--quiet]
Exit 1 if any link is dead, 2 if the site could not be reached at all.
"""
import argparse
import concurrent.futures as cf
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://jbelly-tech.github.io/jbelly-ui/"
OURS = ("jbelly-tech.github.io", "github.com/JBelly-tech")

# A URL in a script is as often a regex or a format string as a link; these characters say so.
NOT_A_LINK = set("\\[]{}^*")
SKIP = ("fonts.googleapis.com", "fonts.gstatic.com", "cdn.tailwindcss.com", "cdn.jsdelivr.net",
        "unpkg.com", "example.com", "localhost", "127.0.0.1", "www.w3.org/2000/svg")
SKIP_DIRS = ("internal/", "evals/runs/", "tests/out/", "docs/showcase/")
SKIP_EXT = (".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2", ".pyc")

URL = re.compile(r"https?://[^\s\"'`<>)\]},]+")
HREF = re.compile(r"""(?:href|src)\s*=\s*["']([^"'#][^"']*)["']""")
MDLINK = re.compile(r"\]\(([^)\s]+)\)")


def tracked():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True,
                         encoding="utf-8", errors="replace").stdout
    for rel in out.splitlines():
        if rel.startswith(SKIP_DIRS) or rel.endswith(SKIP_EXT):
            continue
        yield rel


def collect(site):
    found = []
    for rel in tracked():
        try:
            txt = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in URL.finditer(txt):
            u = m.group(0).rstrip(".,;:")
            if any(h in u for h in SKIP) or NOT_A_LINK & set(u):
                continue
            found.append((u, rel))
        if rel == "index.html":
            # A script block holds filename fragments, not URLs: `src = 'showcase/default-' + tone`
            # is not a link, and a checker that reports it teaches you to ignore its output.
            body = re.sub(r"<script[\s\S]*?</script>", " ", txt)
            for m in HREF.finditer(body):
                t = m.group(1)
                if t.startswith(("http", "//", "data:", "mailto:", "#")):
                    continue
                found.append((site + t.lstrip("./"), rel + " (relative)"))
        if rel.endswith(".md"):
            for m in MDLINK.finditer(txt):
                t = m.group(1)
                if t.startswith(("http", "#", "mailto:")):
                    continue
                found.append(("file:" + str((ROOT / rel).parent / t.split("#")[0]), rel + " -> " + t))
    return sorted(set(found))


def fetch(item):
    u, where = item
    if u.startswith("file:"):
        return (u, where, 200 if pathlib.Path(u[5:]).exists() else 404, "")
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "jbelly-ui-check-links"})
        with urllib.request.urlopen(req, timeout=25) as r:
            return (u, where, r.status, r.geturl())
    except urllib.error.HTTPError as e:
        return (u, where, e.code, "")
    except Exception as e:
        return (u, where, 0, type(e).__name__)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--external", action="store_true", help="also check other people's sites")
    ap.add_argument("--site", default=SITE, help="where the published copy lives")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    site = a.site if a.site.endswith("/") else a.site + "/"
    items = collect(site)
    if not a.external:
        items = [(u, w) for u, w in items if u.startswith("file:") or any(o in u for o in OURS)]
    if not items:
        print("check_links: nothing to check", file=sys.stderr)
        return 2

    bad = []
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        results = list(ex.map(fetch, items))
    reachable = any(code == 200 for u, w, code, f in results if u.startswith("http"))
    if not reachable:
        print("check_links: not one link resolved -- no network, or the site is down. "
              "This is not a pass.", file=sys.stderr)
        return 2
    for u, where, code, final in results:
        if code != 200:
            bad.append((u, where, code, final))
    for u, where, code, final in sorted(bad):
        print("[FAIL] %s  ->  %s%s" % (u, code or "unreachable", "  " + final if final else ""))
        print("       named in %s" % where)
    if not a.quiet:
        print("check_links: %d link(s) checked%s, %d dead -> %s"
              % (len(items), "" if a.external else " (this project's own; --external for the rest)",
                 len(bad), "FAIL" if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
