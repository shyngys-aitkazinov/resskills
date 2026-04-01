#!/usr/bin/env python3
"""Read/write resskills config.yaml values.

Usage:
    uv run python scripts/config.py get <key>
    uv run python scripts/config.py set <key> <value>
    uv run python scripts/config.py path
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml


def _config_search_paths() -> list[Path]:
    """Return config file search paths, highest priority first."""
    return [
        Path.cwd() / "resskills.yaml",
        Path.home() / ".resskills" / "config.yaml",
        Path(__file__).resolve().parent.parent.parent / "config.yaml",  # pack default
    ]


def find_config() -> Path:
    """Find config file, preferring project-local over global over pack default."""
    for loc in _config_search_paths():
        if loc.exists():
            return loc
    # Default to global location (will be created on first set)
    return Path.home() / ".resskills" / "config.yaml"


def read_config(path: Path) -> dict:
    """Read config.yaml and return as dict."""
    if not path.exists():
        return {}
    with path.open() as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def write_config(path: Path, config: dict) -> None:
    """Write config dict to YAML file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def _get_nested(config: dict, key: str) -> str:
    """Get a potentially nested key like 'protect_dirs'."""
    value = config.get(key)
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(str(v) for v in value)
    return str(value)


def main() -> None:
    """Entry point for config command."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "path":
        print(find_config())
        return

    if cmd == "get" and len(sys.argv) >= 3:
        key = sys.argv[2]
        config = read_config(find_config())
        print(_get_nested(config, key))
        return

    if cmd == "set" and len(sys.argv) >= 4:
        key = sys.argv[2]
        value = " ".join(sys.argv[3:])
        path = find_config()
        config = read_config(path)
        if value.lower() in ("true", "false"):
            config[key] = value.lower() == "true"
        else:
            try:
                config[key] = int(value)
            except ValueError:
                try:
                    config[key] = float(value)
                except ValueError:
                    config[key] = value
        write_config(path, config)
        return

    print(__doc__)
    sys.exit(1)


if __name__ == "__main__":
    main()
