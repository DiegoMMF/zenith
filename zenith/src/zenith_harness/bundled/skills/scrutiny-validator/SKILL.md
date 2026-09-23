---
name: scrutiny-validator
description: Adversarial scrutiny procedure for engineering validation assignments. Runs hard-gate commands, reviews the current implementation and evidence integrity against assigned contracts, can use feature-reviewer lanes, and returns per-target verdicts.
---

# Scrutiny Validator

Use this when the assignment asks for implementation scrutiny, hard-gate commands, evidence integrity, or source review.

Scrutiny does not prove a real user, caller, or operator surface. That belongs to `user-testing-validator`. Do not pass a real-surface assertion from scrutiny alone unless this run is the scrutiny lane and a sibling validator owns the surface evidence.

## Inputs

Read the assignment (exact target ids), each assertion (`Surface`, `Needs`, `Behavior`, `Evidence`, and `Fail` / `Oracle` / `Scope` when present; `Statement`, `Evidence Floor`, and `Non-Goals` mean the same), `AGENTS.md`, and the current checkout. Worker reports are claims, not proof. If behavior, surface, or required evidence cannot be read off the assertion, the target is unverifiable.

## Verdict

`passed=true` only when, for every assigned target:

- hard-gate commands that this assignment owns (tests, lint, typecheck, build, or the contract's commands) exit 0, with the exit code visible;
- `Needs` are met;
- the implementation matches `Behavior` within `Scope`;
- evidence this task owns is present and was not mocked away, weakened, or limited to a test-only path.

Otherwise `passed=false`. Blocking findings include missing implementation, a failed required command, unmet `Needs`, missing evidence, a weakened proof, or a security, data, migration, compatibility, or public-API break.

For each failure, write `<regressions_dir>/<item_id>.md` with the command or finding, unmet `Needs`, missing `Evidence`, and how to reproduce it.

A `feature-reviewer` lane is advisory. You own the verdict.

## Report

```markdown
## Hard-Gate Commands
- `<command>` -> exit <code>. <focused output>

## Per-Target Verdicts
### <target-id>: passed | failed
- Needs: <checked prerequisites, unmet dependencies, or None>
- Evidence: <commands/source review/artifacts collected and any named sibling evidence owner>
- Review: <why contract is or is not satisfied>

## Evidence Integrity
- <changed proof surfaces, missing evidence, and credibility impact>

## Responsibility Drift
- <none or concrete drift>

## Review Limitations
- <unreviewed areas and why>
```

Call `end_node` with one item per assigned target, then exit.
