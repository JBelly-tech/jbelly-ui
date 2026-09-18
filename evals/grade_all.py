#!/usr/bin/env python3
"""Grade every run under evals/runs/ and print one comparison table (Class D).

For each run it reads timing.json (what the run cost), then judges the page it produced with
the same deterministic checks the skill ships: token lint, pre-flight, the assertion grader,
and source metrics. Nothing here asks a model for an opinion.

Usage:
  python evals/grade_all.py                      # everything under evals/runs/
  python evals/grade_all.py --runs evals/runs --json results.json --markdown table.md
"""
import argparse, json, subprocess, sys
from pathlib import Path

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "skills" / "jbelly-ui" / "scripts"
TOOLS = REPO / "comparison" / "tools"


def run_script(path: Path, *args: str) -> tuple[int, str]:
    try:
        r = subprocess.run([sys.executable, str(path), *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=300)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as exc:  # a missing script must not take the whole table down
        return 99, f"{type(exc).__name__}: {exc}"


def grade_page(page: Path) -> dict:
    """Deterministic verdicts for one produced page."""
    out = {}
    code, text = run_script(SCRIPTS / "lint_tokens.py", str(page))
    out["lint_ok"] = code == 0
    out["lint"] = text.strip().splitlines()[-1][:160] if text.strip() else ""
    code, text = run_script(SCRIPTS / "preflight.py", str(page))
    out["preflight_ok"] = code == 0
    last = [l for l in text.strip().splitlines() if "FAIL" in l or "PASS" in l]
    out["preflight"] = (last[-1] if last else "")[:160]
    out["preflight_fails"] = sum(1 for l in text.splitlines() if l.strip().startswith("FAIL"))
    code, text = run_script(TOOLS / "dom_metrics.py", page.stem, str(page))
    out["kb"] = round(page.stat().st_size / 1024, 1)
    return out


def collect(runs_dir: Path) -> list:
    rows = []
    for timing in sorted(runs_dir.rglob("timing.json")):
        try: t = json.loads(timing.read_text(encoding="utf-8"))
        except Exception: continue
        row = {k: t.get(k) for k in ("brief", "skill", "model", "total_tokens", "minutes",
                                     "tool_calls", "skill_fired", "cost_usd", "is_error", "clean")}
        page = timing.parent / "page.html"                      # copied out of the workspace
        if not page.is_file():
            page = timing.parent / "workspace" / (t.get("page") or "out/page.html")
        row["page_written"] = page.is_file()
        if page.is_file():
            row.update(grade_page(page))
        row["run_dir"] = str(timing.parent.relative_to(runs_dir)) if timing.parent != runs_dir else "."
        rows.append(row)
    return rows


def markdown(rows: list) -> str:
    head = ("| brief | skill | tokens | min | calls | page | lint | pre-flight | KB | isolated |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n")
    body = ""
    for r in sorted(rows, key=lambda r: (r.get("brief") or "", r.get("skill") or "")):
        body += (f"| {r.get('brief')} | {r.get('skill')} | {(r.get('total_tokens') or 0):,} | "
                 f"{r.get('minutes')} | {r.get('tool_calls')} | {'yes' if r.get('page_written') else 'NO'} | "
                 f"{'ok' if r.get('lint_ok') else 'fail'} | "
                 f"{'PASS' if r.get('preflight_ok') else str(r.get('preflight_fails', '?')) + ' FAIL'} | "
                 f"{r.get('kb', '-')} | {'yes' if r.get('clean') else 'NO - leaked'} |\n")
    return head + body


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", default=str(REPO / "evals" / "runs"))
    ap.add_argument("--json", help="write the rows here")
    ap.add_argument("--markdown", help="write the table here")
    a = ap.parse_args()
    runs_dir = Path(a.runs).resolve()
    if not runs_dir.is_dir(): sys.exit(f"no runs directory: {runs_dir}")
    rows = collect(runs_dir)
    if not rows: sys.exit("no timing.json found; run evals/run.py first")
    table = markdown(rows)
    print(table)
    if a.json: Path(a.json).write_text(json.dumps(rows, indent=2), encoding="utf-8")
    if a.markdown: Path(a.markdown).write_text(table, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
