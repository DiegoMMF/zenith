---
name: engineering-mission-playbook
description: "Use when planning or replanning engineering missions that create, change, port, migrate, integrate, or preserve durable codebase behavior across UI, API, CLI, background jobs, data/migrations, libraries, or operator workflows. Defines investigation, scope inventory, coherent VAL-* contracts, evidence floors, multi-target task topology, engineering validation, root-cause patching, and durable guidance. For pure metric search, use optimization-mission-playbook instead."
---

# Engineering Mission Playbook

Success is the accepted behavior, proven on the real surface by an independent validator. A diff, a green command, a worker report, or a finished task is not success.

## Done

Each promise is one file, `contract/<ID>.md`:

```markdown
# VAL-AREA-001: Short title

Surface: browser | api | cli | tui | job | artifact | data | migration | library | parity | other.
Needs: none | prerequisite assertion/setup/oracle/source baseline/fixture/service.
Behavior: one actor/action/outcome promise.
Evidence: exact evidence a validator must collect.
Fail: optional failure or blocked condition.
Oracle: optional source baseline, golden corpus, or reference.
Scope: optional non-goals or accepted divergences.
```

`Surface`, `Needs`, `Behavior`, and `Evidence` are required. Unmet `Needs`, missing `Evidence`, the wrong surface, or a skipped target is failed or blocked, not passed.

Cover the requested behavior, including edge, error, empty, and rare cases that are in scope. For a port or parity mission, name the source version and prove it with the source suite, golden corpus, or a differential oracle. Tests and source inspection support the verdict. They are the oracle only when the assertion says so.

Use the surface the behavior actually has: a browser for UI, a real request for an API, a real command for CLI/TUI, a real trigger for a job, before/after state for data and migrations, a real import for a library.

## Loop

1. Name the behavior, the surface, and the evidence. Record a blocker instead of a vague assertion.
2. `submit_plan` with `work`, `validate`, and `gate`, then `advance_project`. The orchestrator does not implement the product.
3. Each live assertion has one owning `work` task. Several assertions may share that task when they share an implementation boundary. `validate` proves them independently. `gate` seals only assertions that have evidence, or an explicit accepted risk.
4. On failure, patch the earliest bad artifact: scope, contract, setup, oracle, or code. Stop when every live assertion has fresh evidence, or when the blocker is explicit.

`scrutiny-validator` covers implementation, hard gates, and evidence integrity. `user-testing-validator` covers a real user, caller, or operator surface. Scrutiny cannot pass a real-surface assertion by itself.

## Carriers

- `contract/<VAL-ID>.md`: done criteria.
- `AGENTS.md`: constraints every worker and validator must obey.
- `MEMORY.md`: setup, commands, ports, oracles, known flakes.
- `skills/`: a procedure that would otherwise be repeated in every task.
- `decisions/`: accepted scope cuts and accepted risk.
