"""Procoder bridge for the Freebuff hook engine.

Freebuff passes a hook the tool's values as arguments (`format-on-save.cmd`
reads `%1`, `safety-guard.cmd` reads `%*`); Procoder's hooks read a Claude-shaped
JSON payload on stdin. This is the one place that translation lives.

  pre   commit gate       -> a JSON deny on stdout, silence otherwise
  post  per-file findings -> plain text
  stop  handoff note      -> plain text

Only Procoder's own deny blocks a call. A toolchain failure is reported and
allowed through: `.git/hooks/pre-commit` is where a commit is actually refused,
and it fails closed on its own when procoder cannot run.
"""

import json
import os
import subprocess
import sys

PROCODER = r"C:\Users\trevo\.local\bin\procoder.exe"
EVENTS = {"pre": "pre-tool-use", "post": "post-tool-use", "stop": "stop"}
TIMEOUT = 180
# A scanner that never ran is rendered as a blocking finding, so say which it is.
INFRA = ("gave no answer", "was NOT checked")


def say(text, stream=None):
    """Write one message, never failing on an unencodable byte."""
    if not text:
        return
    target = stream or sys.stdout
    try:
        target.write(text if text.endswith("\n") else text + "\n")
        target.flush()
    except OSError:
        # A closed pipe is the reader's business, not a hook failure.
        return


def run(args, payload=None):
    """Run a Procoder command and return (stdout, stderr, returncode)."""
    try:
        done = subprocess.run(
            [PROCODER, *args],
            input=None if payload is None else json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        return done.stdout or "", done.stderr or "", done.returncode
    except FileNotFoundError:
        return "", f"procoder is not at {PROCODER}", 127
    except subprocess.TimeoutExpired:
        return "", f"procoder did not answer within {TIMEOUT}s", 124


def ask_procoder(event, payload):
    """Run one Procoder hook."""
    return run(["hook", EVENTS[event]], payload)


def hook_output(stdout):
    """The hookSpecificOutput Procoder wraps its answer in, or empty."""
    for line in reversed((stdout or "").splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            inner = json.loads(line).get("hookSpecificOutput")
        except ValueError:
            continue
        if isinstance(inner, dict):
            return inner
    return {}


def with_infra_note(reason):
    """Say so when a deny is caused by a scanner that could not run."""
    if any(mark in reason for mark in INFRA):
        return (
            reason + "\n(one of these is a scanner that did not run — see "
            "overall-documentation/TOOLCHAIN-SEMGREP.md)"
        )
    return reason


def handoff_once():
    """Print the previous session's handoff note once."""
    state = os.path.join(os.getcwd(), ".procoder", "state")
    note = os.path.join(state, "handoff.md")
    marker = os.path.join(state, ".handoff-seen")
    try:
        if not os.path.exists(note):
            return
        if os.path.exists(marker) and os.path.getmtime(marker) >= os.path.getmtime(
            note
        ):
            return
        with open(note, encoding="utf-8", errors="replace") as handle:
            text = handle.read().strip()
        if text:
            say("procoder handoff from the previous session:\n" + text)
        with open(marker, "w", encoding="utf-8") as handle:
            handle.write("seen\n")
    except OSError:
        return


def pre(argv):
    """Gate the command about to run."""
    command = " ".join(argv).strip()
    if not command:
        return 0
    payload = {
        "tool_name": "Bash",
        "cwd": os.getcwd(),
        "tool_input": {"command": command},
    }
    stdout, stderr, _ = ask_procoder("pre", payload)
    answer = hook_output(stdout)
    if answer.get("permissionDecision") == "deny":
        reason = answer.get("permissionDecisionReason") or "blocked by the commit gate"
        say(with_infra_note(reason), sys.stderr)
        return 1
    say(stderr.strip(), sys.stderr)
    return 0


def post(argv):
    """Report formatting and lint for the file just written.

    Secrets and SAST are deliberately left to the commit gate: one scan start-up
    costs ~15s, which is a fine price for a commit and a bad one for a keystroke.
    """
    target = argv[0] if argv else ""
    if not target or not os.path.exists(target):
        return 0
    path = os.path.abspath(target)
    want, _, code = run(["format", path])
    if code == 0 and want.strip():
        with open(path, encoding="utf-8", errors="replace") as handle:
            if want.strip() != handle.read().strip():
                say(
                    f"procoder [format]: {path} is not formatted — write this instead:\n{want}"
                )
    findings, error, _ = run(["lint", path])
    say((findings or error).strip())
    return 0


def stop(argv):
    """Write the handoff note as the turn ends."""
    stdout, stderr, _ = ask_procoder("stop", {"cwd": os.getcwd()})
    say(stdout.strip() or stderr.strip())
    return 0


HANDLERS = {"pre": pre, "post": post, "stop": stop}


def main(argv):
    """Dispatch one hook event from the command line."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            continue
    if not argv or argv[0] not in HANDLERS:
        say("procoder hook: expected one of pre|post|stop", sys.stderr)
        return 0
    if argv[0] == "pre":
        handoff_once()
    return HANDLERS[argv[0]](argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
