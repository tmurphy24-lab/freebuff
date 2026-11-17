# Engineering principles (Freebuff)

`procoder principles` prints this file at the start of a session instead of its
built-in default, so what the agent loads is visible and reviewable here.

1. **A gate that cannot run is not a gate that passed.** Report a broken
   toolchain as broken (see `overall-documentation/TOOLCHAIN-SEMGREP.md`); never
   let "could not check" read as "checked clean".
2. **Boring beats clever.** Prefer the smallest change that makes the behaviour
   correct; leave no speculative abstraction behind.
3. **One place for each fact.** A rule lives in one file and is referenced, not
   copied. Duplicated rules drift; drifted rules are worse than none.
4. **Hooks must never wedge a session.** Fail closed only where the risk is
   unjudged (a commit), and say why in the message the agent reads.
5. **Verify with the tool, not from memory.** Re-run the command that decides
   the question; a remembered pass is not evidence.
6. **Isolation is the contract.** This directory owns its config, hooks, state
   and logs. Nothing here reaches into another agent's runtime.
7. **Depth over volume.** A short, true manifest beats a long, aspirational one.
