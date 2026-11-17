# Freebuff Multi-Model Desktop Agent — Operating Rules & Instructions

> **Role**: Codebuff Desktop Agent with Adaptive Multi-Model Routing  
> **Directory**: `C:\Users\trevo\Desktop\.agents\freebuff`  
> **Master Rules**: See `AGENTS.md`  
> **Governance**: Procoder 3.9.5 — `C:\Users\trevo\.local\bin\procoder.exe`

## Mandatory PR Lifecycle & Quality Gates

Every code change must adhere to the standard PR lifecycle:

1. **Branch & Task Isolation**: Never work directly on `main` or shared stable branches. Create a descriptive feature/fix branch or isolated worktree.
2. **Quality Gates & Auto-Validation**:
   - Run `procoder check` and fix every blocking finding (formatting, hygiene, secrets, lint).
   - Run the automated test suite (`pytest`, `npm test`, `e2e`).
   - Proactively fix all issues, warnings, and test failures before PR creation. Zero broken tests permitted.
3. **Atomic PR Submission**:
   - Write clear conventional commit messages (`feat:`, `fix:`, `refactor:`, `chore:`).
   - Summarize changes, testing performed, and risk assessment.
4. **Squash Merge & Branch Pruning**:
   - Always squash-and-merge into `main` to maintain a clean, linear git history.
   - Immediately delete and prune the feature branch locally and remotely (`git branch -d <branch>`, `git push origin --delete <branch>`, `git fetch --prune`).
5. **Post-Merge Verification**:
   - Pull the latest `main` and ensure the working tree is clean.

## Procoder Hook Surface

This host runs Procoder at three lifecycle points, registered in `hooks.v1.json` and
implemented by `hooks/procoder_hook.py`, reached through one shim,
`hooks/procoder-hook.cmd`, whose first argument is the event:

- **PreToolUse — every tool call** (`procoder-hook.cmd pre`): runs `procoder hook pre-tool-use`. It only acts on a `git commit`, which it gates and reports as allow/deny. Everything else passes silently.
- **PostToolUse — every write** (`procoder-hook.cmd post`): reports formatting and lint for the written file; the file itself is never modified. Secrets and SAST are deliberately left to the commit gate — one scanner start-up costs ~15 s, which is fair for a commit and wrong for every write.
- **Stop — end of turn** (`procoder-hook.cmd stop`): runs `procoder hook stop`, which writes the repository handoff note to `.procoder/state/handoff.md`. The next session's first tool call prints that note once, then marks it seen.

Only Procoder's own verdict blocks a call. A missing or timed-out binary is reported
and let through, because `.git/hooks/pre-commit` is where a commit is actually refused
and it fails closed by itself. When a deny is caused by a scanner that never ran, the
message says so (`overall-documentation/TOOLCHAIN-SEMGREP.md`). `git commit --no-verify`
bypasses the commit gate deliberately and visibly.

## SuperagenticAI Cognitive Architecture & Optimization

- **CodeOptiX (`codeoptix`)**: CLI on PATH, MCP tools broken (`ModuleNotFoundError: No module named 'codexopt'`). MCP disabled.
- ~~CodexOpt (`codexopt`)~~: **not installed** - do not invoke; instruction manifests are edited manually.
- **Agenspy (`agenspy`)**: MCP shim returns canned dicts. Disabled; not a delegation path.
- **AgentVectorDB (`agentvectordb`)**: `store`/`query` raise `AttributeError`; vectors are sha256 mocks. Disabled; not a memory path.

## Canonical Skills Vault

All skills are resolved strictly from the canonical skills vault at `skills/` (`C:\Users\trevo\Desktop\.agents\Skills`, 295 skill directories verified 2026-11-16). Do not install duplicate or out-of-tree skill directories.

## Context Routing (Freebuff toolset)

Freebuff exposes its own tools; the `ctx_*` context-mode MCP server is not registered for this host. The routing rules in `AGENTS.md` §6 therefore apply through these equivalents:

- **Think in code** → write the analysis to a scratch script and run it with `run_terminal_command`; only the answer enters context.
- **Gather** → `code_search`, `glob`, `list_directory` instead of bulk reads.
- **Bounded reads** → `read_files` with `offset`/`limit` windows rather than whole large files.
- **Web** → `web_search` / `read_url` instead of `curl`, `wget`, or inline HTTP.
