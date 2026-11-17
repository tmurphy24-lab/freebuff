"""Procoder bridge for the Freebuff hook engine.

Freebuff passes a hook the tool's values as arguments (`format-on-save.cmd`
reads `%1`, `safety-guard.cmd` reads `%*`); Procoder's hooks read a JSON
payload on stdin. This is the one place that translation lives.

  pre   commit gate       -> a deny on stdout, silence otherwise
  post  per-file findings -> plain text
  stop  handoff note      -> plain text

Only Procoder's own deny blocks a call. A toolchain failure is reported and
allowed through: `.git/hooks/pre-commit` is where a commit is actually refused,
and it fails closed on its own when procoder cannot run.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

PROCODER = r"C:\Users\trevo\.local\bin\procoder.exe"
EVENTS = {"pre": "pre-tool-use", "post": "post-tool-use", "stop": "stop"}
TIMEOUT = 180


def say(text: str, stream=None) -> None:
    """Write one message, never failing on an unencodable byte."""
    if not text:
        return
    target = stream or sys.stdout
    try:
        target.write(text if text.endswith("\n") else text + "\n")
        target.flush()
    except OSError:
        return


def run(argv) -> tuple[str, str, int]:
    """Run procoder and return (stdout, stderr, returncode)."""
    try:
        proc = subprocess.run(
            [PROCODER, *argv],
            input=None,
            text=True,
            capture_output=True,
            timeout=TIMEOUT,
        )
    except FileNotFoundError:
        return "", f"procoder binary not found at {PROCODER}\n", 127
    except subprocess.TimeoutExpired:
        return "", "procoder timed out\n", 124
    except OSError as exc:
        return "", f"procoder failed to start: {exc}\n", 126
    return proc.stdout or "", proc.stderr or "", proc.returncode


def read_payload() -> dict:
    """Read a JSON envelope from stdin if one arrived, else {}.

    PreToolUse, PostToolUse and Stop always send a JSON envelope on stdin.
    """
    if sys.stdin is None:
        return {}
    try:
        if sys.stdin.isatty():
            return {}
    except OSError:
        return {}
    raw = sys.stdin.read()
    if not raw:
        return {}
    text = raw.strip()
    if not text.startswith("{"):
        return {}
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return {}
    if not isinstance(obj, dict):
        return {}
    return obj


def command_from(payload: dict, argv) -> str:
    """The command a PreToolUse event is about to run."""
    tool_input = payload.get("tool_input") or {}
    from_host = str(tool_input.get("command") or "").strip()
    if from_host:
        return from_host
    return " ".join(str(a) for a in argv).strip() or " "


def file_path_from(payload: dict, argv) -> str:
    """The file a PostToolUse event just wrote."""
    tool_input = payload.get("tool_input") or {}
    chosen = argv[0] if argv else ""
    if not chosen:
        chosen = str(tool_input.get("file_path") or "")
    if not chosen:
        chosen = str(tool_input.get("path") or "")
    return chosen.strip()


def hook_output(stdout: str) -> str | None:
    """Extract Procoder's answer for the host."""
    text = (stdout or "").strip()
    if not text:
        return None
    return text


def ask_procoder(event: str, payload: dict) -> tuple[str, str, int]:
    """Run the matching Procoder hook and return (stdout, stderr, rc)."""
    cmd = ["hook", EVENTS.get(event, event)]
    return run(cmd)


def pre(payload: dict, argv) -> int:
    """Commit gate: deny only when Procoder says so."""
    command = command_from(payload, argv)
    forwarded = {
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "cwd": (payload or {}).get("cwd") or os.getcwd(),
        "session_id": (payload or {}).get("session_id"),
        "source": (payload or {}).get("source"),
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        ),
    }
    stdout, stderr, rc = ask_procoder("pre", forwarded)
    if stderr:
        say(stderr.rstrip("\n"))
    answer = hook_output(stdout)
    if answer:
        say(answer)
        if rc != 0:
            return 1
    return 0


def post(payload: dict, argv) -> int:
    """PostToolUse: forward Procoder's per-file findings to the host."""
    target = file_path_from(payload, argv)
    if not target:
        return 0
    stdout, stderr, rc = ask_procoder("post", {"file_path": target})
    if stderr:
        say(stderr.rstrip("\n"))
        return 0
    answer = hook_output(stdout)
    if answer:
        say(answer)
    return 0


def stop(payload: dict, argv) -> int:
    """Stop: hand the session off through Procoder stop."""
    stdout, stderr, rc = ask_procoder("stop", {})
    if stderr:
        say(stderr.rstrip("\n"))
    answer = hook_output(stdout)
    if answer:
        say(answer)
    return 0


HANDLERS = {
    "pre": pre,
    "post": post,
    "stop": stop,
}


def main(*args) -> int:
    argv = list(args) or list(sys.argv[1:])
    payload = read_payload()
    event = (payload or {}).get("event") or (
        argv[0] if argv else ""
    )
    handler = HANDLERS.get(event)
    if handler is None:
        say(f"procoder-hook: unknown event {event!r}")
        return 0
    return handler(payload, argv)


if __name__ == "__main__":
    raise SystemExit(main())
