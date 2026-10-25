"""YAML or JSON configuration. Secrets stay in the environment."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_SECRET_KEY = re.compile(
    r"(secret|token|password|webhook|api[_-]?key|access[_-]?key|credential)",
    re.IGNORECASE,
)


class ConfigError(Exception):
    pass


@dataclass
class Destination:
    enabled: bool = True
    username: str | None = None
    name: str | None = None
    url: str | None = None


@dataclass
class Config:
    users: list[str]
    projects: list[str]
    ignore: list[str]
    destinations: dict[str, Destination]
    interval_seconds: int = 1800
    store_path: Path = field(default_factory=lambda: Path(".pip-release/state.sqlite"))
    path: Path | None = None


def resolve_config_path(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    env = os.environ.get("PIP_RELEASE_CONFIG")
    if env:
        return Path(env)
    return Path("config.yaml")


def load_config(path: Path) -> Config:
    if not path.is_file():
        raise ConfigError(
            f"No config at {path}. Copy config.example.yaml to config.yaml, "
            "or pass --example dragonhound to init."
        )
    data = _read(path)
    if not isinstance(data, dict):
        raise ConfigError("Config must be a mapping")
    _reject_secrets(data, str(path))
    pypi = data.get("pypi") or {}
    if not isinstance(pypi, dict):
        raise ConfigError("pypi must be a mapping")
    users = _strings(pypi.get("users") or [])
    single = pypi.get("user")
    if isinstance(single, str) and single.strip():
        users.insert(0, single.strip())
    projects = _dedupe(_strings(pypi.get("projects") or []))
    ignore = _strings(pypi.get("ignore") or [])
    destinations = _destinations(data.get("destinations") or {})
    poll = data.get("poll") or {}
    store = data.get("store") or {}
    if not isinstance(poll, dict) or not isinstance(store, dict):
        raise ConfigError("poll and store must be mappings")
    interval = int(poll.get("interval_seconds") or 1800)
    if interval < 60:
        interval = 60
    store_path = Path(str(store.get("path") or ".pip-release/state.sqlite"))
    env_store = os.environ.get("PIP_RELEASE_STORE")
    if env_store:
        store_path = Path(env_store)
    return Config(
        users=users,
        projects=projects,
        ignore=ignore,
        destinations=destinations,
        interval_seconds=interval,
        store_path=store_path,
        path=path,
    )


def load_env_file(path: Path, environ: dict[str, str] | None = None) -> None:
    """Load KEY=VALUE lines. Existing variables are left alone."""

    target = os.environ if environ is None else environ
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in target:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        target[key] = value


def _read(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ConfigError(f"{path} is not valid JSON: {exc}") from exc
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover
        raise ConfigError("Install PyYAML to read YAML config files") from exc
    try:
        return yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"{path} is not valid YAML: {exc}") from exc


def _reject_secrets(value: Any, where: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if _SECRET_KEY.search(str(key)):
                raise ConfigError(
                    f"{where} key {key!r} looks like a secret. Put it in .env instead."
                )
            _reject_secrets(child, where)
    elif isinstance(value, list):
        for child in value:
            _reject_secrets(child, where)


def _strings(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ConfigError("Expected a list of strings")
    out: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ConfigError("Expected a list of strings")
        out.append(item.strip())
    return out


def _dedupe(names: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for name in names:
        key = normalize_name(name)
        if key in seen:
            continue
        seen.add(key)
        out.append(name)
    return out


def normalize_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).strip().lower()


def _destinations(value: Any) -> dict[str, Destination]:
    if not isinstance(value, dict):
        raise ConfigError("destinations must be a mapping")
    out: dict[str, Destination] = {}
    for key, raw in value.items():
        if raw is None:
            raw = {}
        if not isinstance(raw, dict):
            raise ConfigError(f"destinations.{key} must be a mapping")
        url = raw.get("url")
        if url is not None and not isinstance(url, str):
            raise ConfigError(f"destinations.{key}.url must be a string")
        out[str(key)] = Destination(
            enabled=bool(raw.get("enabled", True)),
            username=_optional_str(raw.get("username")),
            name=_optional_str(raw.get("name")),
            url=url.strip() if isinstance(url, str) else None,
        )
    return out


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ConfigError("Expected a string")
    text = value.strip()
    return text or None
