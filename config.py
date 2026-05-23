"""Run configuration with layered loading.

Precedence (highest wins):  CLI flags  >  config file  >  environment  >  default

The config file is TOML (read with the stdlib `tomllib`, no dependency).
API keys may live in the config file OR in the usual env vars
(ANTHROPIC_API_KEY / OPENAI_API_KEY). Keep real keys out of git — see
`.gitignore`, which excludes `config.toml`.
"""
from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_CANDIDATES = ("config.toml", "s2p.config.toml")


def _clean(v):
    """Treat empty strings / None uniformly as 'not set'."""
    if v is None:
        return None
    if isinstance(v, str) and v.strip() == "":
        return None
    return v


@dataclass
class LLMConfig:
    provider: str = "anthropic"          # anthropic | openai
    model: str | None = None             # blank -> provider default
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    openai_model: str | None = None      # default OpenAI model if none given


@dataclass
class Settings:
    repo: str
    out_dir: Path
    llm: LLMConfig = field(default_factory=LLMConfig)
    max_fix_attempts: int = 2
    run_tests: bool = False
    branch: str = "playwright-migration"


def _read_toml(path: Path) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def find_config(explicit: str | Path | None) -> Path | None:
    if explicit:
        p = Path(explicit)
        return p if p.exists() else None
    for name in CONFIG_CANDIDATES:
        if Path(name).exists():
            return Path(name)
    return None


def load_settings(
    repo: str,
    *,
    out_dir: str | Path | None = None,
    provider: str | None = None,
    model: str | None = None,
    max_fix_attempts: int | None = None,
    run_tests: bool | None = None,
    config_path: str | Path | None = None,
) -> Settings:
    """Merge config file + env + CLI overrides into a Settings object."""
    cfg_path = find_config(config_path)
    data = _read_toml(cfg_path) if cfg_path else {}

    llm_data = data.get("llm", {})
    run_data = data.get("run", {})
    anth = llm_data.get("anthropic", {})
    oai = llm_data.get("openai", {})

    llm = LLMConfig(
        provider=_clean(provider) or _clean(llm_data.get("provider"))
        or _clean(os.getenv("S2P_PROVIDER")) or "anthropic",
        model=_clean(model) or _clean(llm_data.get("model"))
        or _clean(os.getenv("S2P_MODEL")),
        anthropic_api_key=_clean(anth.get("api_key")) or _clean(os.getenv("ANTHROPIC_API_KEY")),
        openai_api_key=_clean(oai.get("api_key")) or _clean(os.getenv("OPENAI_API_KEY")),
        openai_model=_clean(oai.get("model")) or _clean(os.getenv("OPENAI_MODEL")),
    )

    return Settings(
        repo=repo,
        out_dir=Path(_clean(out_dir) or _clean(run_data.get("out_dir")) or "./playwright-migration"),
        llm=llm,
        max_fix_attempts=max_fix_attempts if max_fix_attempts is not None
        else int(run_data.get("max_fix_attempts", 2)),
        run_tests=run_tests if run_tests is not None
        else bool(run_data.get("run_tests", False)),
        branch=_clean(run_data.get("branch")) or "playwright-migration",
    )
