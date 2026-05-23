# Quickstart

Get from a Selenium repo to a Playwright repo in a few minutes.

## 1. Install

```bash
git clone https://github.com/<you>/selenium2playwright.git
cd selenium2playwright
pip install -e .          # installs deps and the `s2p` command (Python 3.11+)
```

## 2. Add your API key

Copy the example config and drop in a key for the provider you want:

```bash
cp config.example.toml config.toml
```

Edit `config.toml`:

```toml
[llm]
provider = "anthropic"        # or "openai"

[llm.anthropic]
api_key = "sk-ant-..."        # your key
```

`config.toml` is git-ignored, so your key won't be committed. (You can instead
export `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` and leave the file blank.)

## 3. Run the migration

```bash
s2p migrate https://github.com/<org>/<selenium-repo> --out ./playwright-suite
```

or against a local folder:

```bash
s2p migrate ./path/to/selenium-repo --out ./playwright-suite
```

You'll see per-file progress. When it finishes, `./playwright-suite` is a fresh
Playwright project on a `playwright-migration` git branch.

## 4. Review the report

Open `playwright-suite/MIGRATION_REPORT.md`. It lists:
- which files converted cleanly,
- which failed validation, and
- every `TODO[S2P-REVIEW]` marker the model left where something didn't map
  cleanly (custom waits, BDD steps, Selenium Grid, etc.).

That report is your to-do list.

## 5. Run the converted suite

```bash
cd playwright-suite
pip install -r requirements.txt   # rewritten: playwright + pytest-playwright
playwright install                # download browser binaries
pytest                            # add --headed to watch it run
```

## Common overrides

```bash
# Use OpenAI instead of the config default
s2p migrate ./repo --provider openai --model <current-model>

# Allow more auto-fix retries per file
s2p migrate ./repo --max-fix 3

# Convert AND attempt to run the tests in one go
s2p migrate ./repo --run-tests

# Use a config file in a non-default location
s2p migrate ./repo --config ./configs/prod.toml
```

CLI flags override `config.toml`, which overrides environment variables.

## Tuning conversion style

All translation behavior lives in `s2p/prompts.py`. Want `get_by_test_id`
preferred everywhere, or different assertion style? Edit the translation guide
there and re-run — it applies across the whole project.
