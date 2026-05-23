# selenium2playwright (s2p)

An autonomous, Python-based agent that ingests a Selenium test-automation repo
(framework + scripts) and emits an equivalent **Playwright** project using the
**synchronous** API and `pytest-playwright` conventions.

Works with **Claude or OpenAI** behind a single provider-agnostic interface.

## How it works

```
ingest → analyze (AST) → plan (deps first) → convert + validate + self-heal → scaffold → report → git branch
```

1. **Ingest** — clones a GitHub URL (or copies a local path) into a temp workdir.
2. **Analyze** — parses every `.py` with the stdlib `ast` module, classifies each
   file (test / page_object / fixture / util / config), flags selenium usage, and
   builds a local import graph.
3. **Plan** — orders files dependencies-first so page objects/utils convert
   before the tests that import them.
4. **Convert** — per file, sends the source + relevant already-converted context
   to the LLM, guided by the Selenium→Playwright translation guide
   (`s2p/prompts.py`). Non-selenium files are copied through untouched.
5. **Validate + self-heal** — every converted file is syntax-checked and
   ruff-linted; syntax failures are sent back to the model to fix, up to
   `max_fix_attempts`. No human gates — failures are flagged, the run continues.
6. **Scaffold** — rewrites `requirements.txt` and writes `pytest.ini`.
7. **Report** — `MIGRATION_REPORT.md` lists per-file status and every
   `TODO[S2P-REVIEW]` marker for things that didn't map cleanly.
8. **Git** — initialises the output as a `playwright-migration` branch.

## Install

```bash
pip install -e .          # Python 3.11+, installs deps and the `s2p` command
```

## Configure

Settings and API keys live in a TOML config file:

```bash
cp config.example.toml config.toml   # then add your key(s)
```

```toml
[llm]
provider = "anthropic"     # or "openai"

[llm.anthropic]
api_key = "sk-ant-..."     # or leave blank and use ANTHROPIC_API_KEY env var
```

`config.toml` is git-ignored. Precedence: **CLI flag > config.toml > env var > default**.

## Run

```bash
s2p migrate https://github.com/you/selenium-suite --out ./playwright-suite
s2p migrate ./local/repo --provider openai
s2p migrate ./repo --config ./configs/prod.toml --run-tests
```

See **[QUICKSTART.md](QUICKSTART.md)** for the full step-by-step.

## Project layout

```
s2p/
  cli.py          # Typer CLI entry point (also `python -m s2p`)
  config.py       # layered config loading (TOML + env + CLI)
  ingest.py       # clone / copy the source repo
  analyzer.py     # AST classification + import graph
  planner.py      # dependency-ordered conversion plan
  converter.py    # per-file LLM conversion
  validator.py    # syntax / ruff / pytest gates
  pipeline.py     # autonomous orchestration
  report.py       # requirements rewrite, scaffold, migration report
  prompts.py      # the Selenium→Playwright translation guide (tune here)
  llm/            # provider-agnostic clients (anthropic, openai)
```

## Design notes

- **Add a provider** by implementing `complete(system, user)` in `s2p/llm/` and
  registering it in `base.get_client`.
- **Conversion quality** is governed by `s2p/prompts.py` — edit the translation
  guide to change locator preferences, assertion style, etc.
- **Sandboxing**: `--run-tests` runs pytest locally; wrap `validator.run_pytest`
  in Docker for untrusted repos.
- **Known limitations**: BDD step-def rewiring, Selenium Grid/remote
  capabilities, and custom `expected_conditions` are flagged for review rather
  than guessed at.

> Model names change. `claude-sonnet-4-6` is current and recommended for coding;
> override via config/`--model`, and verify OpenAI's current model string before
> using `--provider openai`.

## License

MIT — see [LICENSE](LICENSE).
