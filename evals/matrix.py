#!/usr/bin/env python3
"""Run briefs across conditions, one after another, and pick up where it stopped (Class D).

Every combination is a separate process (evals/run.py), so a failure or a rate limit costs one
cell, not the batch. Finished cells are skipped on the next invocation, which makes the matrix
resumable across sessions and across a rate-limit window.

Usage:
  python evals/matrix.py --skills none,jbelly-ui --model claude-sonnet-5            # all 12 briefs
  python evals/matrix.py --briefs 01,05,10 --skills jbelly-ui --model claude-sonnet-5
  python evals/matrix.py --skills none,jbelly-ui --dry-run                          # show the plan
"""
import argparse, json, subprocess, sys, time
from pathlib import Path

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

REPO = Path(__file__).resolve().parent.parent
BRIEFS = REPO / "evals" / "briefs"
RUNS = REPO / "evals" / "runs"


def done_cells() -> set:
    """(brief, skill, model) already measured, so a rerun continues instead of repeating."""
    have = set()
    for t in RUNS.rglob("timing.json"):
        try: d = json.loads(t.read_text(encoding="utf-8"))
        except Exception: continue
        if d.get("page"):                       # only a run that produced a page counts as done
            have.add((d.get("brief"), d.get("skill"), d.get("model")))
    return have


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--briefs", default="", help="comma-separated prefixes, e.g. 01,05,10 (default: all)")
    ap.add_argument("--skills", required=True, help="comma-separated conditions, e.g. none,jbelly-ui")
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--timeout", type=int, default=2400, help="seconds per cell")
    ap.add_argument("--redo", action="store_true", help="run cells that already have a page")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    wanted = [b.strip() for b in a.briefs.split(",") if b.strip()]
    briefs = sorted(p for p in BRIEFS.glob("*.md")
                    if not wanted or any(p.name.startswith(w) for w in wanted))
    skills = [s.strip() for s in a.skills.split(",") if s.strip()]
    if not briefs: sys.exit("no briefs matched")

    have = set() if a.redo else done_cells()
    cells = [(b, s) for b in briefs for s in skills if (b.stem, s, a.model) not in have]
    skipped = len(briefs) * len(skills) - len(cells)
    print(f"[matrix] {len(cells)} cell(s) to run, {skipped} already done · model {a.model}")
    for b, s in cells: print(f"  {b.stem:22} {s}")
    if a.dry_run: return 0

    results, t0 = [], time.time()
    for i, (b, s) in enumerate(cells, 1):
        print(f"\n[matrix] {i}/{len(cells)} · {b.stem} · {s}")
        r = subprocess.run([sys.executable, str(REPO / "evals" / "run.py"), "--brief", str(b),
                            "--skill", s, "--model", a.model, "--timeout", str(a.timeout)],
                           text=True, encoding="utf-8", errors="replace")
        results.append({"brief": b.stem, "skill": s, "exit": r.returncode})
        if r.returncode != 0:
            print(f"[matrix] cell failed (exit {r.returncode}); continuing with the next one")

    mins = round((time.time() - t0) / 60, 1)
    failed = [r for r in results if r["exit"] != 0]
    print(f"\n[matrix] finished {len(results)} cell(s) in {mins} min · {len(failed)} failed")
    for r in failed: print(f"  failed: {r['brief']} · {r['skill']}")
    print("[matrix] next: python evals/grade_all.py --markdown evals/results.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
