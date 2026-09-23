---
name: optimization-mission-playbook
description: "Domain playbook for optimization missions — any task whose goal is to move a metric: performance, latency, throughput, memory, cost, score, quality, compression, ranking, solver, model/eval, and similar metric-improvement work. Defines how to think about and run an optimization mission: establishing the ground truth, trusting the measurement, profiling to the dominant cost, estimating the ceiling, generating and pruning disposable hypotheses, exploring cheaply before verifying expensively, guarding against metric gaming and overfitting, reasoning about correctness and trade-offs, and stopping on evidence."
---

# Optimization Mission Playbook

Use this when the goal is to move a metric. Durable behavior (a feature, a port, a migration, an API) belongs to `engineering-mission-playbook`. Load both only when the mission has both, and record the boundary.

Success is a metric that moves in the declared direction, on a measurement that is comparable and repeatable, with correctness and guardrails still holding. A number gained by changing the benchmark, the fixtures, or the verifier is not a win.

## Stop

Stop when the ceiling or a recorded "good enough" is reached, later rounds no longer pay for themselves, the budget is spent, or the environment cannot measure credibly. An honest "no further win", with what was tried and ruled out, is a successful stop.

## Loop

Default shape: targetless `work` in the current checkout, a ledger, attention, then the orchestrator accepts, rejects, or runs another hypothesis. A hypothesis is not an assertion and needs no gate.

```text
define correctness protocol + metric protocol
-> targetless work
-> ledger + attention
-> accept | reject | keep_as_evidence | rerun
-> next round or stop
```

Before `submit_plan`, record an optimization method the tasks can cite:

- correctness oracle independent of the candidate's own output, plus the case set, tolerances, and per-case failure rule;
- metric command, direction, unit, workloads, repetitions, aggregation, noise band, scoring reference, and working point, named separately;
- how a candidate is bound so baseline and candidate runs share build, cache, and workload;
- protected benchmark, verifier, fixture, and scoring paths;
- the stop rule.

Each experiment is one hypothesis. Sequence them with `depends_on` when they share the checkout. Add a `benchmark-infra` task only when shared measurement files must exist before any experiment. Do not optimize product code in that task.

Call `end_node(done=True, report=<ledger>, request_attention=True)` when the ledger is usable. Use `done=False` only when no usable ledger exists.

Ledger minimum:

```text
candidate_id, task_id, parent_ref, candidate_ref,
changed_files, optimization_method_ref,
correctness result per case, metric, baseline, candidate, delta, noise_band,
protected_paths_touched,
recommendation: accept | reject | keep_as_evidence | rerun | inconclusive
```

The orchestrator decides acceptance from the ledger and the checkout, not from the worker's prose. Update the working point only after acceptance.

Do not author `VAL-*` or `EXP-*` assertions by default. Use them only for a durable engineering deliverable, an external sign-off, or a high-risk claim that needs `validate` / `gate`. Then every declared assertion has one owning `work` task, `contract/<ID>.md` exists before `add_items`, and `contract-review` covers those assertions only.

`benchmark-validator` and `scrutiny-validator` are for that formal exception, not for routine search. Store the method, the oracle, and the scoreboard in `MEMORY.md` or `AGENTS.md`. Leave raw runs in attempts.
