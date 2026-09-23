---
name: benchmark-validator
description: Benchmark validation procedure for one assigned benchmark-related target. For optimization EXP-* targets, independently classify candidate outcome. For engineering VAL-* or legacy engineering targets, prove or disprove the required benchmark/performance assertion.
---

# Benchmark Validator

Use this for exactly one benchmark-related assertion. If the assignment names more than one, fail it as too broad and request attention.

You do not pick the winner and you do not keep optimizing. You decide whether the cited candidate is trustworthy.

Read the assignment, the one contract, `AGENTS.md`, the ledger, the candidate ref, and the measurement protocol. Do not mutate the workspace, and do not read or depend on hidden verifier internals.

## Integrity

If the candidate changes the benchmark, scoring, fixtures, golden outputs, or verifier to move the number, the proof is invalid. For an `EXP-*` target that is `invalid`. For a `VAL-*` or legacy target, `passed=false`.

## Remeasure

Rebuild parent and candidate as the contract says. Run both under the declared protocol. Capture raw output, aggregate, spread, and environment. Run correctness and guardrails before any metric comparison. A skipped, stale, or un-runnable check is `invalid` for `EXP-*` and `passed=false` for an engineering target.

Attack the failure modes this candidate could introduce (input size, cache, concurrency, edge cases) in addition to the contract's own command. If the contract does not give enough oracle or candidate binding to do that, classify the experiment `invalid` instead of promoting on speed alone.

## Outcome

For an optimization `EXP-*` target:

- `promoted`: integrity holds, setup is complete, correctness and guardrails pass, and the metric meets the promotion rule.
- `rejected`: integrity and setup hold, but correctness, a guardrail, or the metric fails.
- `budget_exhausted`: the declared budget stopped the run and the contract allows that.
- `invalid`: missing ledger, broken candidate binding, compromised evidence, or unverifiable setup.

`passed=true` for `promoted`, `rejected`, or a legitimate `budget_exhausted`. `passed=false` for `invalid`.

For a `VAL-*` or legacy engineering target, `passed=true` only when the benchmark assertion and its guardrails pass with fresh evidence. A rejected candidate, a failed guardrail, missing evidence, or an exhausted budget is `passed=false` unless the contract defines that outcome as the required behavior.

If `passed=false`, write `<regressions_dir>/<item_id>.md` with the command, the expected measurement or behavior, and the invalidating issue.

## Report

```markdown
## Experiment
- Item ID: <id>
- Parent artifact: <ref/path>
- Candidate artifact: <ref/path>
- Ledger: <path>

## Evidence Integrity
- Changed protected/evidence-sensitive paths: <list>
- Verdict: <credible | invalid>

## Measurements
- Parent: <runs, aggregate, spread, raw paths>
- Candidate: <runs, aggregate, spread, raw paths>
- Improvement: <calculation and threshold>

## Correctness And Guardrails
- `<command>` -> exit <code>, <result>

## Outcome
- <promoted | rejected | budget_exhausted | invalid>
- Reason: <contract-tied explanation>

## Limitations
- <setup or measurement caveats>
```

Call `end_node` with exactly one item for the assigned target id, then exit.
