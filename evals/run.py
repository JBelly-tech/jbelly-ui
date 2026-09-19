#!/usr/bin/env python3
"""Run one brief under one condition and record what it cost (Class D).

A condition is which skill the agent can see: a skill name, or "none" for the baseline.
Every other installed skill is switched off for the run, so the condition is exactly what it says.

Usage:
  python evals/run.py --brief evals/briefs/01-dashboard.md --skill jbelly-ui
  python evals/run.py --brief evals/briefs/01-dashboard.md --skill none --model claude-sonnet-5
  python evals/run.py --brief ... --skill some-other-skill --model claude-sonnet-5

Writes <out>/timing.json (the numbers), <out>/stream.jsonl (the raw events),
<out>/workspace/ (what the agent produced). Grading happens in grade_all.py.

What this costs, before you run it: each call starts a real, autonomous agent session on YOUR
account and lets it write files. One screen-building brief is typically tens of thousands of
tokens and several minutes, and a full matrix is that many times over -- enough to reach a plan's
rate limit. Nothing here is free or instant.

Where it can write: a workspace in the system temp directory, created per run. The repo, the user
skills directory and the agent skills directory are denied for reading and writing, so a run cannot
study the skill it is being measured without. Every run is scanned afterwards and records whether
any call reached outside its workspace; a run that leaked is marked and must not be compared.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

REPO = Path(__file__).resolve().parent.parent
# Bundled/plugin skills that disableBundledSkills does not remove; switched off by name so
# every condition sees the same (empty) background.
EXTRA_OFF = ("doctor", "docs", "import-memory", "morning")
# Where workspaces live: outside the repo on purpose. A workspace inside it lets an agent walk up
# the tree and read the very skill the run is supposed to be measuring without.
WORKSPACE_ROOT = Path(tempfile.gettempdir()) / "jbelly-evals"
DEFAULT_TOOLS = ("Read,Write,Edit,Glob,Grep,Skill,"
                 "Bash(python:*),Bash(python3:*),Bash(py:*),Bash(node:*)")


def claude_cli() -> str:
    """The CLI's real path (npm installs a .cmd wrapper on Windows)."""
    for name in (("claude.cmd", "claude.exe", "claude") if os.name == "nt" else ("claude",)):
        found = shutil.which(name)
        if found: return found
    sys.exit("claude CLI not found on PATH")


def installed_skills() -> dict:
    """Every skill this machine exposes to an agent: name -> folder."""
    found = {}
    for base in (Path.home() / ".claude" / "skills", Path.home() / ".agents" / "skills"):
        if not base.is_dir(): continue
        for child in sorted(base.iterdir()):
            try:
                if (child / "SKILL.md").is_file() and child.name not in found:
                    found[child.name] = child
            except OSError:
                continue
    return found


def resolve_skill(name: str, given: str | None) -> Path:
    if given:
        p = Path(given).expanduser().resolve()
        if not (p / "SKILL.md").is_file(): sys.exit(f"no SKILL.md in {p}")
        return p
    inst = installed_skills()
    if name in inst: return inst[name].resolve()
    local = REPO / "skills" / name
    if (local / "SKILL.md").is_file(): return local
    sys.exit(f"skill '{name}' is not installed; pass --skill-src <path>")


def build_prompt(brief_text: str, page_path: str) -> str:
    return (f"{brief_text.strip()}\n\n"
            f"Write the finished page to `{page_path}`. "
            "Work autonomously: do not ask questions, do not stop for confirmation, "
            "and say when the file is written.")


def parse_stream(stream_path: Path) -> dict:
    """Token totals, tool-call count, and which skills actually fired."""
    tool_calls, skills_used, tools_used, assistant_msgs, result_event = 0, [], {}, 0, None
    with open(stream_path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line: continue
            try: ev = json.loads(line)
            except json.JSONDecodeError: continue
            if ev.get("type") == "assistant":
                assistant_msgs += 1
                for block in ev.get("message", {}).get("content", []) or []:
                    if block.get("type") == "tool_use":
                        tool_calls += 1
                        name = block.get("name", "?")
                        tools_used[name] = tools_used.get(name, 0) + 1
                        if name == "Skill":
                            s = (block.get("input") or {}).get("skill")
                            if s and s not in skills_used: skills_used.append(s)
            elif ev.get("type") == "result":
                result_event = ev
    u = (result_event or {}).get("usage", {}) or {}
    return {
        "tool_calls": tool_calls,
        "tools_used": dict(sorted(tools_used.items(), key=lambda kv: -kv[1])),
        "assistant_messages": assistant_msgs,
        "skills_used": skills_used,
        "input_tokens": u.get("input_tokens", 0),
        "output_tokens": u.get("output_tokens", 0),
        "cache_read_tokens": u.get("cache_read_input_tokens", 0),
        "cache_creation_tokens": u.get("cache_creation_input_tokens", 0),
        "num_turns": (result_event or {}).get("num_turns"),
        "cost_usd": (result_event or {}).get("total_cost_usd"),
        "duration_ms": (result_event or {}).get("duration_ms"),
        "is_error": (result_event or {}).get("is_error"),
        "result_text": ((result_event or {}).get("result") or "")[:400],
    }


def outside_workspace(stream_path: Path, ws: Path) -> dict:
    """Out-of-workspace tool calls, split by what actually happened.

    A denied attempt is not contamination: the guard did its job. A call that came back with
    content is, because the run then knew something the condition was supposed to hide. Only the
    fields that name a target are inspected -- scanning whole inputs matches paths that merely
    appear inside the page the agent is writing.
    """
    ws_s = ws.as_posix().lower()
    path_fields = ("file_path", "path", "pattern", "command", "notebook_path", "url")
    calls, out = {}, {"leaked": [], "blocked": []}

    def is_outside(value: str) -> bool:
        q = value.replace("\\", "/").lower()
        if not re.search(r"(?:^[a-z]:/|^/[a-z]/)", q): return False
        if ws_s in q: return False
        tmp = Path(tempfile.gettempdir()).as_posix().lower()
        return not q.startswith(tmp)

    with open(stream_path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try: ev = json.loads(line)
            except json.JSONDecodeError: continue
            if ev.get("type") == "assistant":
                for block in ev.get("message", {}).get("content", []) or []:
                    if block.get("type") != "tool_use": continue
                    inp = block.get("input") or {}
                    targets = [str(inp[f]) for f in path_fields if isinstance(inp.get(f), str)]
                    hit = next((t for t in targets if is_outside(t)), None)
                    if hit: calls[block["id"]] = f"{block.get('name')}: {hit[:110]}"
            elif ev.get("type") == "user":
                for block in ev.get("message", {}).get("content", []) or []:
                    if block.get("type") != "tool_result" or block.get("tool_use_id") not in calls: continue
                    body = block.get("content")
                    text = body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)
                    low = text.lower()
                    denied = any(w in low for w in ("permission", "denied", "not allowed", "blocked"))
                    out["blocked" if denied else "leaked"].append(calls.pop(block["tool_use_id"]))
    for leftover in calls.values():          # no result recorded: treat as a leak, not as a pass
        out["leaked"].append(leftover)
    out["leaked"], out["blocked"] = out["leaked"][:25], out["blocked"][:25]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--brief", required=True)
    ap.add_argument("--skill", required=True, help="skill name under test, or 'none' for the baseline")
    ap.add_argument("--skill-src", help="folder to use when the skill is not installed")
    ap.add_argument("--model", default="", help="model id (default: the CLI's own default)")
    ap.add_argument("--out", help="output directory (default: evals/runs/<brief>-<skill>-<stamp>)")
    ap.add_argument("--allowed-tools", default="", help="override the tool allow-list")
    ap.add_argument("--workspace-root", default="", help="where workspaces are created (default: system temp)")
    ap.add_argument("--timeout", type=int, default=3600, help="seconds before the run is abandoned")
    ap.add_argument("--dry-run", action="store_true", help="print the command and exit")
    a = ap.parse_args()

    brief = Path(a.brief).resolve()
    if not brief.is_file(): sys.exit(f"no such brief: {brief}")
    stamp = time.strftime("%Y%m%d-%H%M%S")
    name = f"{brief.stem}-{a.skill}-{stamp}"
    out = Path(a.out).resolve() if a.out else REPO / "evals" / "runs" / name
    out.mkdir(parents=True, exist_ok=True)
    # The workspace is the only place the agent should be able to touch.
    ws_root = Path(a.workspace_root).resolve() if a.workspace_root else WORKSPACE_ROOT
    ws = (ws_root / name).resolve()

    skill_src = None if a.skill == "none" else resolve_skill(a.skill, a.skill_src)
    if ws.exists(): shutil.rmtree(ws)
    (ws / "out").mkdir(parents=True)
    if skill_src and not any(p.name == a.skill for p in installed_skills().values() if p.name == a.skill):
        dest = ws / ".claude" / "skills" / a.skill          # not installed: snapshot it into the workspace
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(skill_src, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git"))

    # Exactly one skill visible (or none). There is no Skill() permission rule; visibility is
    # controlled by skillOverrides, so every other installed skill is switched off by name.
    names = set(installed_skills()) | set(EXTRA_OFF)
    others = {name: "off" for name in sorted(names) if name != a.skill}
    # Deny the places an agent could read its way to another condition's advantage.
    # Absolute path, no "//" prefix: on Windows the prefixed form is accepted and then never matches,
    # so a run that looked blocked would quietly read the repo it is being measured against.
    off_limits = [REPO, Path.home() / ".claude" / "skills", Path.home() / ".agents" / "skills"]
    deny = [f"{tool}({p.as_posix()}/**)" for p in off_limits for tool in ("Read", "Edit", "Write", "Glob", "Grep")]
    settings = {"includeCoAuthoredBy": False, "disableBundledSkills": True,
                "skillOverrides": others, "permissions": {"deny": deny}}
    settings_path = out / "settings.json"
    settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")

    page = (ws / "out" / "page.html").as_posix()      # inside the temp workspace, not the repo
    prompt = build_prompt(brief.read_text(encoding="utf-8"), page)
    prompt_path = out / "prompt.txt"          # stdin: a multi-line argv value is mangled by the .cmd wrapper
    prompt_path.write_text(prompt, encoding="utf-8", newline="\n")

    allowed = a.allowed_tools or DEFAULT_TOOLS
    cmd = [claude_cli(), "-p", "--output-format", "stream-json", "--verbose",
           "--permission-mode", "acceptEdits", "--allowedTools", allowed,
           "--settings", str(settings_path)]
    if a.skill == "none": cmd.append("--disable-slash-commands")
    if a.model: cmd += ["--model", a.model]

    if a.dry_run:
        print(" ".join(f'"{c}"' if " " in c else c for c in cmd), "< prompt.txt")
        print(f"[dry] skills switched off: {len(others)} · skill under test: {a.skill} ({skill_src})")
        return 0

    print(f"[run] brief={brief.stem} skill={a.skill} model={a.model or '(default)'} "
          f"· {len(others)} other skills off")
    print(f"[run] starting an autonomous agent session on your account; workspace {ws}")
    stream_path = out / "stream.jsonl"
    t0 = time.time()
    with open(stream_path, "w", encoding="utf-8") as fh, open(prompt_path, "rb") as pin:
        proc = subprocess.run(cmd, cwd=ws, stdin=pin, stdout=fh, stderr=subprocess.PIPE,
                              text=True, timeout=a.timeout)
    wall = time.time() - t0
    if proc.returncode != 0:
        print(f"[run] CLI exited {proc.returncode}: {(proc.stderr or '')[:400]}")

    m = parse_stream(stream_path)
    isolation = outside_workspace(stream_path, ws)
    leaks = isolation["leaked"]
    produced = sorted(p.relative_to(ws).as_posix() for p in (ws / "out").rglob("*") if p.is_file())
    record = {
        "brief": brief.stem, "skill": a.skill, "model": a.model or "(cli default)",
        "agent": "claude-code", "stamp": stamp,
        "minutes": round(wall / 60, 2), "wall_seconds": round(wall, 1),
        # Two numbers on purpose: context is what the cost model charges for (every step re-sends
        # the prefix), billed is what is not served from cache.
        "total_tokens": m["input_tokens"] + m["output_tokens"] + m["cache_read_tokens"] + m["cache_creation_tokens"],
        "billed_tokens": m["input_tokens"] + m["output_tokens"] + m["cache_creation_tokens"],
        **m,
        "skill_fired": (a.skill in m["skills_used"]) if a.skill != "none" else (not m["skills_used"]),
        "produced": produced, "page": "out/page.html" if (ws / "out" / "page.html").is_file() else None,
        "exit_code": proc.returncode, "skill_source": str(skill_src) if skill_src else None,
        "skills_switched_off": len(others), "allowed_tools": allowed,
        "workspace": str(ws), "outside_workspace": leaks,
        "blocked_attempts": isolation["blocked"], "clean": not leaks,
    }
    produced_page = ws / "out" / "page.html"
    if produced_page.is_file():
        shutil.copy2(produced_page, out / "page.html")
    (out / "timing.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"[run] {record['total_tokens']:,} context tokens ({record['billed_tokens']:,} billed) · "
          f"{record['minutes']} min · {record['tool_calls']} tool calls "
          f"· skill fired: {record['skill_fired']} · page: {bool(record['page'])}")
    if isolation["blocked"]:
        print(f"[run] guard held: {len(isolation['blocked'])} out-of-workspace call(s) were denied")
    if leaks:
        print(f"[run] CONTAMINATED - {len(leaks)} out-of-workspace call(s) returned content; this "
              f"number is not comparable:")
        for h in leaks[:6]: print("       " + h)
    print(f"[run] -> {out / 'timing.json'}")
    return 0 if record["page"] else 1


if __name__ == "__main__":
    sys.exit(main())
