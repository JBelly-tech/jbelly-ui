#!/usr/bin/env python3
"""Grade every run under evals/runs/ and print one comparison table (Class D).

For each run it reads timing.json (what the run cost), then judges the page it produced with
the same deterministic checks the skill ships: token lint, pre-flight, the assertion grader,
and source metrics. Nothing here asks a model for an opinion.

Usage:
  python evals/grade_all.py                      # everything under evals/runs/
  python evals/grade_all.py --runs evals/runs --json results.json --markdown table.md
"""
import argparse, importlib.util, json, re, subprocess, sys
from pathlib import Path

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "skills" / "jbelly-ui" / "scripts"
TOOLS = REPO / "comparison" / "tools"
PREFLIGHT_SUMMARY = re.compile(r"^preflight:.*?(\d+) FAIL.*$", re.M)
_grader = None


def grader():
    """grade.py is imported, not spawned: its CLI walks an iteration dir for outputs/dashboard*.html,
    so against a run dir holding one page.html it would grade nothing and still exit 0. check() takes
    the page we actually have."""
    global _grader
    if _grader is None:
        spec = importlib.util.spec_from_file_location("jbelly_grade", TOOLS / "grade.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _grader = mod
    return _grader


def run_script(path: Path, *args: str) -> tuple[int, str]:
    if not path.is_file(): return 99, f"missing script: {path}"  # python's own exit 2 would read as a page that failed the check
    try:
        r = subprocess.run([sys.executable, str(path), *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=300)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except Exception as exc:  # a timeout or a failed spawn must not take the whole table down
        return 99, f"{type(exc).__name__}: {exc}"


def grade_page(page: Path) -> dict:
    """Deterministic verdicts for one produced page: token lint, pre-flight, the assertion grader,
    source metrics. A grader that could not be run is recorded in tool_errors rather than scored,
    because a check that quietly did not happen reads exactly like a check that passed."""
    out = {"tool_errors": []}
    code, text = run_script(SCRIPTS / "lint_tokens.py", str(page))
    out["lint_ok"] = code == 0
    out["lint"] = text.strip().splitlines()[-1][:160] if text.strip() else ""
    out["lint_ran"] = code != 99
    if not out["lint_ran"]: out["tool_errors"].append(f"lint_tokens.py: {out['lint']}")

    code, text = run_script(SCRIPTS / "preflight.py", str(page))
    out["preflight_ok"] = code == 0
    m = PREFLIGHT_SUMMARY.search(text)   # its own tally; the per-check lines it prints read "[FAIL] ..."
    out["preflight_fails"] = int(m.group(1)) if m else None
    out["preflight"] = (m.group(0) if m else (text.strip().splitlines() or [""])[-1])[:160]
    if not m: out["tool_errors"].append(f"preflight.py: no summary line (exit {code})")

    code, text = run_script(TOOLS / "dom_metrics.py", page.stem, str(page))
    try: out["metrics"] = json.loads(text)
    except Exception: out["tool_errors"].append(f"dom_metrics.py: no JSON (exit {code})")
    out["dom_elements"] = (out.get("metrics") or {}).get("dom_elements")

    try:
        checks = grader().check(page.read_text(encoding="utf-8", errors="replace"))
        out["assertions"] = [{"check": n, "passed": ok, "evidence": ev} for n, ok, ev in checks]
        out["assert_passed"] = sum(1 for c in out["assertions"] if c["passed"])
        out["assert_total"] = len(checks)
    except Exception as exc:
        out["tool_errors"].append(f"grade.py: {type(exc).__name__}: {exc}")

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


def verdicts(r: dict) -> tuple:
    """lint / pre-flight / grader / DOM cells. ERR, never a score, when the grader did not run."""
    if not r.get("page_written"): return ("-", "-", "-", "-")
    pf = "PASS" if r.get("preflight_ok") else (f"{r['preflight_fails']} FAIL" if r.get("preflight_fails") is not None else "ERR")
    gr = f"{r['assert_passed']}/{r['assert_total']}" if r.get("assert_total") else "ERR"
    lint = ("ok" if r.get("lint_ok") else "fail") if r.get("lint_ran") else "ERR"
    dom = r.get("dom_elements")
    return (lint, pf, gr, "ERR" if dom is None else str(dom))


def markdown(rows: list) -> str:
    """Errored runs are listed under the table, not in it: the CLI never finished them, so their
    tokens and verdicts are not comparable with a run that did."""
    head = ("| brief | skill | tokens | min | calls | page | lint | pre-flight | grader | dom | KB | isolated |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|---|\n")
    order = lambda r: (r.get("brief") or "", r.get("skill") or "")
    body = ""
    for r in sorted([r for r in rows if not r.get("is_error")], key=order):
        lint, pf, gr, dom = verdicts(r)
        body += (f"| {r.get('brief')} | {r.get('skill')} | {(r.get('total_tokens') or 0):,} | "
                 f"{r.get('minutes')} | {r.get('tool_calls')} | {'yes' if r.get('page_written') else 'NO'} | "
                 f"{lint} | {pf} | {gr} | {dom} | "
                 f"{r.get('kb', '-')} | {'yes' if r.get('clean') else 'NO - leaked'} |\n")
    bad = sorted([r for r in rows if r.get("is_error")], key=order)
    tail = ""
    if bad:
        tail = f"\n**{len(bad)} run(s) errored and are excluded from the comparison:**\n\n"
        for r in bad:
            tail += f"- ERRORED {r.get('brief')} / {r.get('skill')} - {r.get('run_dir')}\n"
    return head + body + tail


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
    if not [r for r in rows if not r.get("is_error")]:
        sys.exit(f"all {len(rows)} run(s) errored: nothing to compare")
    broken = [f"{r.get('run_dir')}: {e}" for r in rows for e in (r.get("tool_errors") or [])]
    for b in broken: print(f"[grader did not run] {b}", file=sys.stderr)
    return 1 if broken else 0   # an unrun check must not leave the table looking clean


if __name__ == "__main__":
    sys.exit(main())
