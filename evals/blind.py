#!/usr/bin/env python3
"""Judge two pages for the same brief without telling the judge who made what.

Renders both pages, shows them to a judge model as "A" and "B", asks which is the better
professional interface and why, then asks again with the order swapped. A win counts only when
both orderings agree; otherwise the pair is a draw. Position bias is the thing this guards against.

The judge runs with no skills visible and no tools beyond reading the two images, so it cannot
discover which page came from which maker.

Usage:
  python evals/blind.py --a evals/runs/01-dashboard-jbelly-ui-*/workspace/out/page.html \\
                        --b evals/runs/01-dashboard-none-*/workspace/out/page.html \\
                        --label-a jbelly-ui --label-b no-skill --model claude-sonnet-5
"""
import argparse, glob, json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

REPO = Path(__file__).resolve().parent.parent
RUBRIC = """You are judging two web pages built from the same brief. You cannot see who made either one.

Look at both screenshots and answer as a demanding senior product designer would:
- hierarchy and rhythm (is the eye led, or is everything the same weight?)
- typography and spacing discipline
- does it look deliberately designed, or like a generic AI default (blue-600 primary, rounded-2xl
  plus shadow-lg everywhere, purple gradients, icon-in-a-square on every card)?
- data presentation: are numbers readable, charts legible, tables dense but calm?
- completeness: states, actions, and whether the page looks finished

Reply with strict JSON and nothing else:
{"winner": "A" | "B" | "tie", "confidence": 1-5, "why": "<=40 words", "loser_biggest_flaw": "<=20 words"}"""


def claude_cli() -> str:
    for name in (("claude.cmd", "claude.exe", "claude") if os.name == "nt" else ("claude",)):
        found = shutil.which(name)
        if found: return found
    sys.exit("claude CLI not found on PATH")


def shoot(page: Path, png: Path, width=1440, height=1000) -> bool:
    """One deterministic screenshot per page (Playwright, same size for both)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("playwright is needed for the blind judge: python -m pip install playwright")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": width, "height": height})
        pg.goto(page.resolve().as_uri(), wait_until="networkidle")
        pg.wait_for_timeout(1500)
        pg.mouse.move(width - 40, 20)          # keep the pointer off charts so no tooltip opens
        pg.screenshot(path=str(png))
        b.close()
    return png.is_file()


def ask_judge(first: Path, second: Path, model: str, timeout: int) -> dict:
    """One judgement: 'A' is `first`, 'B' is `second`."""
    prompt = (f"{RUBRIC}\n\nPage A: {first.as_posix()}\nPage B: {second.as_posix()}\n"
              "Read both image files, then reply with the JSON object only.")
    with tempfile.TemporaryDirectory() as tmp:
        settings = Path(tmp) / "settings.json"
        settings.write_text(json.dumps({"disableBundledSkills": True}), encoding="utf-8")
        pfile = Path(tmp) / "prompt.txt"
        pfile.write_text(prompt, encoding="utf-8", newline="\n")
        cmd = [claude_cli(), "-p", "--output-format", "json", "--disable-slash-commands",
               "--permission-mode", "acceptEdits", "--allowedTools", "Read",
               "--settings", str(settings)]
        if model: cmd += ["--model", model]
        with open(pfile, "rb") as pin:
            r = subprocess.run(cmd, stdin=pin, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=timeout)
    try:
        payload = json.loads(r.stdout or "{}")
        text = payload.get("result", "")
    except json.JSONDecodeError:
        text = r.stdout or ""
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return {"winner": "error",
                "why": (text or r.stderr or f"claude exited {r.returncode} with no output")[:200]}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {"winner": "error", "why": m.group(0)[:200]}


def judged(v: dict, first: str, second: str) -> str:
    """Label the winner of one judgement. Empty string means the judge cast no usable vote."""
    return {"A": first, "B": second, "tie": "tie"}.get(v.get("winner"), "")


def one(path_arg: str) -> Path:
    hits = sorted(glob.glob(path_arg))
    if not hits: sys.exit(f"no page matches {path_arg}")
    return Path(hits[-1]).resolve()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--a", required=True, help="page (glob allowed; newest match wins)")
    ap.add_argument("--b", required=True)
    ap.add_argument("--label-a", default="A"); ap.add_argument("--label-b", default="B")
    ap.add_argument("--model", default="claude-sonnet-5", help="judge model (use a family other than the builder's)")
    ap.add_argument("--out", default=str(REPO / "evals" / "runs" / "blind"))
    ap.add_argument("--timeout", type=int, default=600)
    a = ap.parse_args()

    page_a, page_b = one(a.a), one(a.b)
    out = Path(a.out).resolve(); out.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    png_a, png_b = out / f"{stamp}-x.png", out / f"{stamp}-y.png"
    print(f"[blind] rendering\n  {a.label_a}: {page_a}\n  {a.label_b}: {page_b}")
    shoot(page_a, png_a); shoot(page_b, png_b)

    print("[blind] judging, order 1 …")
    v1 = ask_judge(png_a, png_b, a.model, a.timeout)          # A = label_a
    print("[blind] judging, order 2 (swapped) …")
    v2 = ask_judge(png_b, png_a, a.model, a.timeout)          # A = label_b

    pick1 = judged(v1, a.label_a, a.label_b)
    pick2 = judged(v2, a.label_b, a.label_a)
    # A judge that never named A, B or tie has not voted at all. Filing that as a draw would hide a
    # broken judge behind a result that looks like a real comparison.
    unanswered = {f"order{i}": (v.get("why") or "no winner field")[:200]
                  for i, (v, pick) in enumerate(((v1, pick1), (v2, pick2)), 1) if not pick}
    agreed = pick1 == pick2 and pick1 in (a.label_a, a.label_b)
    if unanswered: winner = "no verdict (judge failed to answer)"
    elif agreed: winner = pick1
    else: winner = "draw (judge disagreed with itself when swapped)"
    verdict = {
        "page_a": str(page_a), "page_b": str(page_b), "label_a": a.label_a, "label_b": a.label_b,
        "judge_model": a.model, "order1": v1, "order2": v2,
        "pick_order1": pick1 or "no answer", "pick_order2": pick2 or "no answer",
        "unanswered": unanswered,
        "winner": winner,
    }
    (out / f"{stamp}-verdict.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    print(f"[blind] order 1 -> {pick1 or 'no answer'} | order 2 -> {pick2 or 'no answer'}")
    print(f"[blind] WINNER: {verdict['winner']}")
    print(f"[blind] -> {out / f'{stamp}-verdict.json'}")
    for key, why in unanswered.items():
        print(f"[blind] {key}: judge gave no usable verdict -> {why}", file=sys.stderr)
    return 1 if unanswered else 0


if __name__ == "__main__":
    sys.exit(main())
