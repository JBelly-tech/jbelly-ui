#!/usr/bin/env python3
"""Point every published link at a new owner or a new site, in one command.

This project has moved once and will move again -- to a company account, or onto a domain. GitHub
redirects a repository URL after a transfer, so `github.com/...` links survive. It does **not**
redirect a Pages site: the old `<owner>.github.io/<repo>/` address stops resolving the moment the
repository leaves, and every absolute link to it dies at once. The first move meant finding 22 of
them by hand, in six files, and the two that were missed were only caught by fetching all of them.

So the next move is this script plus `check_links.py`, and neither of them is a memory exercise.

What it deliberately does NOT touch:

  - `skills/jbelly-ui/` -- the folder people install names no host this project owns, which is why
    the last move broke nothing for anyone already using it. smoke.py holds that.
  - the package name `jbelly-ui` -- it is what people type in `npx skills add <owner>/jbelly-ui`,
    and renaming it breaks every published install line for a cosmetic gain.
  - git history -- rewriting fifty commits to change a name in the log changes every hash, breaks
    every clone in existence and dead-links every commit URL.

Usage:
  python scripts/retarget.py --owner JBelly-tech                    # a new GitHub owner
  python scripts/retarget.py --owner Acme --site https://acme.dev/  # ...and a domain
  python scripts/retarget.py --owner Acme --dry-run                 # show, change nothing

Then: python scripts/check_links.py   (and commit)
Exit 1 if nothing matched -- a rewrite that changes nothing is a failure, not a no-op.
"""
import argparse
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
# Where the current values live. Everything else derives from a `git ls-files` sweep, so a new file
# that names the owner is picked up without anyone remembering to add it here.
CURRENT_OWNER = "JBelly-tech"
CURRENT_SITE = "https://jbelly-tech.github.io/jbelly-ui/"
NEVER = ("skills/jbelly-ui/",)          # the installed folder must not learn our hostnames
SKIP = ("internal/", "evals/runs/", "tests/out/", "docs/showcase/", "CHANGELOG.md")
SKIP_EXT = (".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2", ".pyc")


def files():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True,
                         encoding="utf-8", errors="replace").stdout
    for rel in out.splitlines():
        if rel.startswith(SKIP) or rel.startswith(NEVER) or rel.endswith(SKIP_EXT):
            continue
        yield rel


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--owner", required=True, help="the new GitHub owner (user or organisation)")
    ap.add_argument("--site", default="", help="the new published site, if it is changing")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    old_host = CURRENT_SITE.split("//", 1)[1].split("/", 1)[0]
    new_site = a.site or ("https://%s.github.io/jbelly-ui/" % a.owner.lower())
    new_host = new_site.split("//", 1)[1].split("/", 1)[0]
    new_base = new_site.rstrip("/")
    old_base = CURRENT_SITE.rstrip("/")

    total, touched = 0, []
    for rel in files():
        p = ROOT / rel
        try:
            s = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        before = s
        s = s.replace(old_base, new_base)                       # the site, path and all
        s = s.replace(old_host, new_host)                       # any bare hostname left
        s = re.sub(re.escape(CURRENT_OWNER) + r"(?=/)", a.owner, s)          # owner/repo
        s = s.replace("github.com/" + CURRENT_OWNER, "github.com/" + a.owner)
        if s == before:
            continue
        n = sum(1 for x, y in zip(before.splitlines(), s.splitlines()) if x != y)
        total += n
        touched.append((rel, n))
        if not a.dry_run:
            p.write_text(s, encoding="utf-8", newline="\n")

    for rel, n in touched:
        print("  %-44s %d line(s)" % (rel, n))
    print("%d line(s) in %d file(s)%s" % (total, len(touched), "  (dry run)" if a.dry_run else ""))
    if not touched:
        print("retarget: nothing matched %s or %s -- is CURRENT_OWNER still right?"
              % (CURRENT_OWNER, old_host), file=sys.stderr)
        return 1
    if not a.dry_run:
        print("\nNext: update CURRENT_OWNER/CURRENT_SITE in this file and the SITE in "
              "check_links.py, then run:\n  python scripts/check_links.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
