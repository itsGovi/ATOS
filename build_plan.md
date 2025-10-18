Nice — here’s a tight, **actionable 4-week sprint plan** for **Project 1 — Code Fluency Sprint (CLI + Tests)** that will force you to read, debug and ship code until tracebacks feel like plain English. Every day is an experiment: small, measurable, repeatable. I kept it practical — commands, exercises, failure scenarios to practice, and a debugging checklist you’ll actually use in interviews.

---

# Sprint overview (4 weeks)

Goal: Build a small CLI that fetches data from a public API, writes CSV, and is covered by unit + integration tests. Add logging, CI, and a `self-debug` command that surfaces failing tests and suggests fixes.
Success metric: repo can be cloned, tests run and pass in CI; you can reproduce and fix 5 common errors in <30 minutes.

Workload: ~8–12 hours/week (flex) — daily micro-tasks (1–2 hours) + two deeper blocks (3–4 hours) on core days.

---

## Week 0 — Prep (2–3 hours, optional)

* Create repo: `git init project1-cli`
* Add README with objective + run instructions.
* Set up Python venv:

  ```bash
  python -m venv .venv
  source .venv/bin/activate
  pip install -U pip
  ```
* Requirements file: `pip install requests pytest black isort pre-commit`

---

## Week 1 — MVP CLI + basic test (goal: minimal working flow)

**Outcome:** CLI `fetcher` that calls a public API (e.g., [https://api.coindesk.com/v1/bpi/currentprice.json](https://api.coindesk.com/v1/bpi/currentprice.json)) and writes CSV.

### Day-by-day

Mon: scaffold

* Create package structure:

  ```
  project1-cli/
    fetcher/
      __init__.py
      cli.py
      api.py
      io.py
    tests/
      test_api.py
      test_io.py
  ```
* Add `pyproject.toml` with formatters + `pre-commit` hooks.

Tue: API wrapper

* Implement `api.get_price()` using `requests`.
* Write unit test `test_api.py` that mocks `requests` (use `unittest.mock`).

Wed: IO layer

* Implement `io.write_csv(data, path)` — simple CSV writer.
* Unit test `test_io.py` with temporary file (`tmp_path`).

Thu: CLI entrypoint

* Implement `cli.main()` with `argparse`:

  ```bash
  python -m fetcher.cli --output prices.csv
  ```
* Manual run: verify CSV is created.

Fri: Practice debugging exercise #1

* Intentionally break import in `cli.py` to get `ModuleNotFoundError`. Reproduce and fix. Time yourself.

**Mental models to use:** First Principles (what must each layer guarantee?), Occam’s razor (keep functions tiny).

---

## Week 2 — Tests, edge cases, and error handling

**Outcome:** solid unit test coverage + one small integration test.

### Day-by-day

Mon: Increase test coverage

* Add tests for network failure: mock `requests` to raise `requests.Timeout`. Ensure `get_price()` raises a clear custom exception `APIFetchError`.

Tue: Input validation

* Validate `io.write_csv` handles empty data / bad path; add tests for permissions error using `tmp_path` with mode changes.

Wed: Integration test

* Create `tests/test_cli_integration.py` that runs CLI with `subprocess.run` pointing to a small local HTTP server (use `http.server` or `responses` lib).

Thu: Logging + structured errors

* Add `logging` (structured: `logger = logging.getLogger(__name__)`). Ensure errors are logged with tracebacks.
* Practice debugging exercise #2: simulate a failing integration (e.g., API returns unexpected JSON) and walk through stack trace.

Fri: Debug patterns practice

* Reproduce `TypeError` from a wrong return type and fix by adding runtime type-checking or docs.

**Debugging checklist (practice):**

1. Reproduce in minimal script.
2. Read full traceback top→bottom, then bottom→top.
3. Identify failing module/file/line.
4. Print/log snapshots of variables near failure.
5. Google exact error message + library.
6. Add failing unit test, fix, run tests.

---

## Week 3 — CI, linters, and the self-debug command

**Outcome:** GitHub Actions runs tests + linters; add `self-debug` command that summarizes failing tests and suggests fixes (mapping common errors to hints).

### Day-by-day

Mon: Pre-commit & linters

* Configure `pre-commit` for `black/isort/flake8`.
* Fix style issues.

Tue: GitHub Actions

* Add simple CI: run `python -m pytest -q` + linters.
* Push and verify CI passes.

Wed: Build `self-debug`:

* Implement `cli.py --self-debug` which runs tests via `pytest` programmatically (using `pytest.main(['-q', '--maxfail=1'])`) and captures results.
* Map common exceptions to hints. Example mapping:

  * `ModuleNotFoundError` → "Check package/module names and PYTHONPATH"
  * `requests.exceptions.Timeout` → "Network timeout; retry or mock in tests"
  * `PermissionError` → "Check file path permissions and working dir"
  * `AssertionError` → "Test assertion failed — inspect expected vs actual"

Thu: Practice debugging exercise #3

* Introduce a subtle bug (off-by-one or JSON key rename). Run `--self-debug`, inspect hint, fix.

Fri: Write documentation

* Add `DEBUGGING.md` with the checklist and `--self-debug` usage.

**Mental models:** TRIZ (use analogies: `self-debug` ≈ automated post-mortem), feedback loops.

---

## Week 4 — Failure injection, error scenarios & polish

**Outcome:** You can reproduce & fix a table of 5 canonical failures; finalize deliverables (README, demo video).

### Day-by-day

Mon: Failure injection suite

* Create `scripts/failures/` that simulate:

  1. Network 502/timeout
  2. JSON schema change (missing key)
  3. Disk full / PermissionError when writing CSV
  4. Dependency version conflict (simulate with fake import or monkeypatch)
  5. Race condition (concurrent write) — simulate with multiprocessing.

Tue: Debug drills

* Time-boxed 30-min exercises: reproduce each failure, add failing test, fix, run CI.

Wed: Demo prep

* Record a 4–6 minute screencast: clone repo, run tests, introduce a failing test, run `--self-debug`, fix it, commit.

Thu: Clean up

* Ensure README covers how to run, how to debug, CI badge, code of conduct for PRs.

Fri: Retrospective + interview lines

* Write 3 bullet points you’ll say in interviews about:

  * The bug you fixed (before/after).
  * What you learned about reading tracebacks.
  * How the `self-debug` idea demonstrates system-level thinking.

---

## Deliverables (end of sprint)

* GitHub repo with:

  * `fetcher/` package
  * `tests/` with unit + integration tests
  * `README.md`, `DEBUGGING.md`
  * Pre-commit + GitHub Actions
  * `--self-debug` CLI feature
* 4–6 minute demo screencast (host on drive/GitHub release)
* Short post-mortem: 1 page with 3 bugs you fixed + what you changed in your dev loop

---

## 5 canonical error scenarios to master (practice)

1. `ModuleNotFoundError` — wrong import path / environment.
2. `requests.exceptions.Timeout` — network resilience / retries.
3. `KeyError` because JSON schema changed — defensive parsing.
4. `PermissionError` on file write — relative paths vs absolute, process rights.
5. `AssertionError` in tests — reading test output to identify expectation mismatch.

---

## Quick interview soundbites (30–45s each)

* On a bug: “I reproduced the failing trace in a minimal script, added a unit that captured it, and used targeted prints + pytest to pin the issue. Fix was X; I validated by adding regression test and CI. That sequence — reproduce → test → fix → CI — is my routine.”
* On `self-debug`: “I built a small mapping that converts common exceptions into human hints so the first 60% of the debug work is automated — it’s like triage for your future self.”
* On mindset: “I treat bugs like experiments: hypothesis about root cause, quick test, then iterate. This avoids heroic fixes and makes the change auditable.”

---

## Tools & commands cheat-sheet

* Run tests: `pytest -q`
* Run CLI: `python -m fetcher.cli --output prices.csv`
* Self-debug: `python -m fetcher.cli --self-debug`
* Run linters: `pre-commit run --all-files`
* Create venv: `python -m venv .venv && source .venv/bin/activate`
* Run CI locally (act) — optional

---

If you want, I’ll:

* produce the exact starter repo skeleton + `cli.py` and test templates, OR
* write the exact `--self-debug` implementation snippet and the mapping table for common errors.

Which one should I build next for you?
