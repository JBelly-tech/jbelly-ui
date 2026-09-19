#!/usr/bin/env python3
"""Answer one question from the recorded runs: on this brief, did we win (Class D).

Winning is not a feeling. For every brief that has been run under two conditions, this compares
them on the numbers that decide agent cost -- context tokens, billed tokens, wall minutes and tool
calls -- plus whether the page passed the deterministic checks, and prints WIN, LOSS or MIXED.

Usage:
  python evals/scoreboard.py                                  # ours against every other condition
  python evals/scoreboard.py --ours jbelly-ui --theirs none
  python evals/scoreboard.py --runs evals/runs --markdown evals/scoreboard.md
"""
import argparse, json, subprocess, sys
from pathlib import Path

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "skills" / "jbelly-ui" / "scripts"
# Lower is better for all four: cost is context size multiplied by steps.
METRICS = [("total_tokens", "context tokens"), ("billed_tokens", "billed tokens"),
           ("minutes", "minutes"), ("tool_calls", "tool calls")]


def latest_runs(runs_dir: Path) -> dict:
    """The newest usable run per (brief, condition). A leaked or pageless run is not usable."""
    best = {}
    for t in sorted(runs_dir.rglob("timing.json")):
        try: d = json.loads(t.read_text(encoding="utf-8"))
        except Exception: continue
        if not d.get("page") or d.get("clean") is False: continue
        key = (d.get("brief"), d.get("skill"))
        if key not in best or (d.get("stamp") or "") > (best[key].get("stamp") or ""):
            d["_dir"] = t.parent
            best[key] = d
    return best


def checks_pass(run: dict) -> str:
    """What the shipped deterministic checks say about the page this run produced."""
    page = run["_dir"] / "page.html"
    if not page.is_file(): return "no page"
    verdicts = []
    for script in ("lint_tokens.py", "preflight.py"):
        try:
            r = subprocess.run([sys.executable, str(SCRIPTS / script), str(page)],
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=180)
            verdicts.append("ok" if r.returncode == 0 else "FAIL")
        except Exception:
            verdicts.append("?")
    return "lint " + verdicts[0] + ", pre-flight " + verdicts[1]


def compare(ours: dict, theirs: dict) -> tuple:
    rows, wins, losses = [], 0, 0
    for key, label in METRICS:
        a, b = ours.get(key), theirs.get(key)
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)) or not b:
            rows.append((label, a, b, "-")); continue
        delta = (a - b) / b * 100
        verdict = "win" if a < b else ("tie" if a == b else "loss")
        wins += verdict == "win"; losses += verdict == "loss"
        rows.append((label, a, b, f"{delta:+.0f}% {verdict}"))
    overall = "WIN" if wins and not losses else ("LOSS" if losses and not wins else "MIXED")
    return rows, overall


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", default=str(REPO / "evals" / "runs"))
    ap.add_argument("--ours", default="jbelly-ui")
    ap.add_argument("--theirs", default="", help="one condition to compare against (default: each in turn)")
    ap.add_argument("--markdown", help="also write the report here")
    a = ap.parse_args()

    runs_dir = Path(a.runs).resolve()
    if not runs_dir.is_dir(): sys.exit(f"no runs directory: {runs_dir}")
    runs = latest_runs(runs_dir)
    if not runs: sys.exit("no usable run found; run evals/run.py first")

    briefs = sorted({b for b, s in runs if s == a.ours})
    if not briefs: sys.exit(f"no run for condition '{a.ours}'")
    others = sorted({s for b, s in runs if s != a.ours and (a.theirs in ("", s))})
    if not others: sys.exit("nothing to compare against yet")

    out, verdicts = [], []
    for brief in briefs:
        ours = runs.get((brief, a.ours))
        if not ours: continue
        out.append(f"\n## {brief}\n")
        out.append(f"{a.ours}: {checks_pass(ours)}")
        for other in others:
            theirs = runs.get((brief, other))
            if not theirs:
                out.append(f"\n{a.ours} vs {other}: not run yet"); continue
            rows, overall = compare(ours, theirs)
            verdicts.append((brief, other, overall))
            out.append(f"\n**{a.ours} vs {other}: {overall}** ({other}: {checks_pass(theirs)})\n")
            out.append(f"| metric | {a.ours} | {other} | |")
            out.append("|---|---|---|---|")
            for label, x, y, verdict in rows:
                fx = f"{x:,.0f}" if isinstance(x, (int, float)) else str(x)
                fy = f"{y:,.0f}" if isinstance(y, (int, float)) else str(y)
                out.append(f"| {label} | {fx} | {fy} | {verdict} |")

    won = [v for v in verdicts if v[2] == "WIN"]
    text = "\n".join(out)
    print(text)
    print(f"\n{len(won)} of {len(verdicts)} comparison(s) won outright.")
    for brief, other, overall in verdicts:
        if overall != "WIN":
            print(f"  not yet: {brief} vs {other} -> {overall}")
    if a.markdown:
        Path(a.markdown).write_text(text + "\n", encoding="utf-8", newline="\n")
    return 0 if verdicts and len(won) == len(verdicts) else 1


if __name__ == "__main__":
    sys.exit(main())
