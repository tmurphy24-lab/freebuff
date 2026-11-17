# Freebuff Multi-Model Desktop Agent — Workspace Agent Rules

> **Role**: Codebuff Desktop Agent with Adaptive Multi-Model Routing  
> **Stance**: Adaptive model selection, cost and latency awareness, robust paired programming, strictly zero cross-agent leakage.  
> **Local Agent Entry**: `FREEBUFF.md`  
> **Master Ecosystem Hub**: `C:\Users\trevo\Desktop\.agents\AGENTS.md`  
> **Continuous Optimization Standard**: CodexOpt is **not installed** (verified 2026-10-24) - manifests are edited by hand  
> **Canonical Skills Vault**: `skills/` (`C:\Users\trevo\Desktop\.agents\Skills`, 295 skill directories verified 2026-11-16)

---

## 1. Agent Mission & Specialization

Specialized for dynamic model dispatching across Claude, GPT, and open-weights models, selected by task complexity rather than by habit.

All operations are isolated strictly to this agent's workspace boundaries. Configuration, session state, caches, and local logs reside inside this directory with zero cross-app leakage.

---

## 2. Procoder Governance & Mandatory Quality Gates

All development, modifications, and commits performed by this agent are strictly governed by **Procoder** (`C:\Users\trevo\.local\bin\procoder.exe`). Every pull request, commit, and task resolution must pass all quality gates cleanly without warnings or failures.

- **Gate Enforcement**: Enforced via `procoder check` and the full `procoder` command set (this directory's policies live in `.procoder/config.toml`).
- **Commit Gate Policy**: `commit_gate = "block"` — Direct commits are prevented if any gate or validation check fails.
- **Linting Policy**: `lint.policy = "block"` — Zero linting errors or style warnings allowed (enforced via ecosystem linters e.g. `ruff`, `eslint`, `prettier`, `golangci-lint`).
- **Real Database Testing Gate (Zero-Mock Invariant)**: `test.policy = "block"` — All unit and integration test suites must pass 100%. Mocking database sessions or tables is **strictly blocked** (`real PostgreSQL tests with zero mocking: block`). All data operations execute against real PostgreSQL instances with UUIDv7 primary keys, `company_id` tenant isolation, and Row-Level Security (RLS).
- **SAST & Secrets Security**: `security.sast_blocks_at = "ERROR"` — Gitleaks secrets scanning and Semgrep SAST are executed continuously. Any finding at `ERROR` level strictly blocks the build and commit.
- **Quality Chain**: `procoder analyze` → `procoder spec` → `procoder plan` → `procoder todo` → `procoder check`. Controllers refuse to close while sections are missing, placeholders remain, acceptance criteria are unmet, or the gate is unclean.
- **5-Level Drill-Down Spec Compliance** (engineering ladder, all under `docs/drill-down-spec/`):
  - **Level 1 — Service** (WHAT it is; the pre-flight anti-duplication audit is the gate _inside_ Level 1) → `docs/drill-down-spec/<topic>/level-1-service.md`
  - **Level 2 — Process trace** (HOW it runs: KPIs, 90% autonomous / 10% human-in-the-loop) → `level-2-process.md`
  - **Level 3 — Capabilities** (the PARTS the service is made of) → `level-3-capabilities.md`
  - **Level 4 — Functions & Interfaces** (HOW parts connect: functions, REST/Avro contracts, security surface) → `level-4-functions-interfaces.md`
  - **Level 5 — Final Build** (what gets added) → `level-5-final-build.md`
  - Workbook/seed data and ADRs are referenced by the ladder, not a level; feature specs live under `docs/drill-down-spec/` (never `docs/specs/`).

---

## 3. Runtime Boundaries

No shared sidecar or background telemetry service is assumed. This agent owns
its local configuration, hooks, state, and logs. Procoder hooks (PreToolUse on
every tool call, PostToolUse on every write, Stop at end of turn) are registered
in `hooks.v1.json` and driven through `hooks/procoder-hook.cmd`; see `FREEBUFF.md`
for the surface.

---

## 4. Instruction Maintenance (CodexOpt is not installed)

This agent's instructions are maintained by hand. CodexOpt is **not installed** (verified 2026-10-24):

- **Status**: not installed - no CLI, no config, no database on this machine.
- **Benchmark Tracking**: unavailable - `codexopt` is not on PATH.
- **Continuous Engineering Refinement**: prune redundant instructions by hand, and keep `AGENTS.md` the single master file in this directory.
- **Configuration**: no `codexopt.yaml` exists. Each agent keeps its own `AGENTS.md`.

---

## 5. Mandatory PR Lifecycle & Clean Code Directives

Every change authored by this agent must satisfy the following core software engineering mandates:

### A. Branch Isolation & Commits

- **Branch Safety**: Never commit directly to `main` or stable branches. Work strictly in isolated branches: `feature/<name>`, `fix/<name>`, or `refactor/<name>`.
- **Conventional Commits**: Commit messages must adhere to conventional commits (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`).
- **Atomic Commits**: Each commit must represent a single logical, verifiable step with passing tests.

### B. Pull Request Invariants, Vertical Slicing & Merging

- **Zero PR Scope Blockers & Unrestricted System Expansion**: Creating new pages, new route paths, new components, new database models, new migrations, new event schemas, and physical domain execution logic is fully authorized, required, and expected. Any artificial line cap or rule claiming "don't make paths / extra pages" is strictly repealed. Complete vertical slices ship with full test coverage.
- **Strict 1-to-1 PR Ratio for Drill-Down Specs**: Every drill-down specification corresponds strictly 1-to-1 to a single PR. Extraneous capabilities require dedicated specs and separate PRs.
- **Autonomous Slash Command & Orchestrator Governance (`/boost`, `/teamwork`)**: Strictly FORBIDDEN to output conversational routine filler ("Routine Declaration: Solo Routine", "Routine Declaration: Delegation Routine", "Solo Routine is active and confirmed") or pause for user questions. All commands operate in 100% autonomous engineering delivery mode.
- **Zero Rate Limit / Quota Excuses**: Never cite GitHub API rate limits, Copilot quotas, or subscription tiers; user does not pay for Copilot and does not need to. Agents execute locally and autonomously.
- **Squash-and-Merge**: All PRs must be squash-merged into `main` to preserve a clean linear history.
- **Branch Pruning**: Delete and prune the feature branch locally and remotely immediately post-merge (`git branch -d <branch>`, `git push origin --delete <branch>`, `git fetch --prune`).

### C. Clean Code, SOLID & Architectural Invariants

- **Single Responsibility Principle (SRP)**: Functions **MUST** stay under 30 lines with a single clear purpose. Modules **MUST** stay under 300 lines.
- **Open/Closed & Liskov Substitution**: Code must be open for extension but closed for modification. Subtypes must be substitutable for their base types.
- **Interface Segregation & Dependency Inversion**: Keep interfaces minimal and purpose-built. Depend upon abstractions, not concrete implementations.
- **DRY & KISS**: Avoid duplicate code by extracting reusable utilities into canonical libraries. Prefer simple, readable implementations over speculative abstractions.
- **Explicit Control & Data Flow**: Avoid hidden side effects, magical global state, or implicit mutations. Prefer early returns and explicit error handling.
- **Test-Driven Development (TDD)**: Test-first methodology. Write failing tests (RED) reproducing bugs or defining requirements before implementing production code (GREEN), then REFACTOR.
- **Zero Secrets**: Credentials, API keys, and environment files (`.env`, `.pem`, service accounts) must never be committed.

---

## 6. Mandatory Context-Mode Routing Rules

To prevent context flooding and ensure high-performance execution, this agent strictly adheres to Context-Mode routing protocols. The `ctx_*` context-mode MCP server is **not registered for this host** (`freebuff/.mcp.json` carries `xerj`, `rea` and `e2e` only), so each rule below is stated against the tool that actually exists here.

### A. Think in Code — MANDATORY

- When analyzing, counting, filtering, comparing, searching, or transforming data: **write code** to a scratch script and run it with `run_terminal_command`, printing only the computed answer.
- Do NOT read raw bulky data into the conversation context. PROGRAM the analysis, do not manually compute it. Pure JavaScript or TypeScript — Node.js built-ins only (`fs`, `path`, `child_process`).

### B. Strictly Blocked Operations

- **`curl` / `wget` — FORBIDDEN**: Never execute `curl` or `wget` via shell commands. Use `web_search` or `read_url`.
- **Inline HTTP — FORBIDDEN**: Do not use `node -e "fetch(...)"` or `python -c "requests.get(...)"` via terminal commands.
- **Direct Web Fetching — FORBIDDEN**: Never fetch large raw web pages into context. Use `web_search` first, then `read_url` for a specific page.

### C. Redirected Operations

- **Shell commands >20 lines**: Write the logic to a script file and run that. `run_terminal_command` is reserved for simple operations (`git`, `mkdir`, `rm`, `mv`, `npm install`, one build or test command).
- **File Reading for Analysis**: Reading files to edit uses direct file tools; reading files to analyze, explore, or summarize uses `code_search` plus bounded `read_files` windows (`offset`/`limit`).
- **Large Search Operations**: Filter and count with `code_search`, `glob` or a script instead of returning hundreds of search lines.

### D. Canonical Tool Selection Flow

1. **GATHER**: `run_terminal_command` (batch of read-only commands) or `list_directory` — concise inventory.
2. **FOLLOW-UP**: `code_search` — targeted symbol or text retrieval with line numbers.
3. **PROCESSING**: scratch script through `run_terminal_command` — only stdout enters context.
4. **WEB**: `web_search` for excerpts, `read_url` when a specific page is required.
5. **INDEX**: nothing to write; `procoder index` maintains the symbol map where the directory is a git repository.
