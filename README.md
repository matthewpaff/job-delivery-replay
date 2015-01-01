# Job Delivery Replay

Replay in-memory job delivery events with deduplication, retry counts, and dead-letter states.

Uses Python 3.10+ and its standard library only. No package installation, virtual
environment, external server, Redis, Celery, or network access is required.

## Run

```console
python -m jobs_lab --help
python -m jobs_lab examples/sample.json
python -m jobs_lab --check-fixtures fixtures/cases.jsonl
python generate_fixtures.py --count 20
python -m unittest discover -s tests -v
```

Run from this directory. The optional path defaults to `-`, which reads JSON from
stdin. Output is JSON or a fixture-check summary. Exit codes are 0 success,
1 file failure, and 2 invalid input. Examples and fixtures contain generated data.

Input has max_attempts and events. enqueue creates a pending job; deliver represents a completed successful attempt; fail represents a failed attempt. Completed deliveries and enqueue events are deduplicated. Reaching the failure limit leaves a dead job; subsequent deliveries do not execute it. Jobs and outcomes are returned in deterministic order. This is an in-memory state machine, not Celery, an actual queue, or a guarantee of production exactly-once processing.

## Learning focus

The roadmap's Celery-inspired worker retries and duplicate-delivery learning exercises. This is an independent concept exercise based on the modeled
roadmap. It makes no claim to be employer-owned or period-authentic production code.

## Structure

- `jobs_lab/core.py`: validated parsing, storage, or state transitions.
- `jobs_lab/cli.py`: JSON command interface.
- `jobs_lab/generate_fixtures.py`: original deterministic validation cases.
- `jobs_lab/fixture_check.py`: expected-output/error checks.
- `fixtures/cases.jsonl`: 366 generated cases, with explicit descriptions.
- `tests/`: independently selected boundaries and the complete corpus check.

Branches `feature/core`, `feature/cli`, `data/fixtures`, and `docs/usage` retain
snapshots; `main` contains the complete tool. Dates and provenance are also recorded
in TIMELINE.json. Many data cases share a scenario; they are not separate features.

Keep changes focused, use actual dates for new work, and add a regression test
for changed behavior. Licensed under [MIT](LICENSE).

[History and provenance](HISTORY.md).
