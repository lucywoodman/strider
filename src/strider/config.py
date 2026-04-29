import os
import tomllib
from pathlib import Path

DEFAULTS = {
    "steps_per_km": 1400,
    "speed": 5.0,
    "unit": "km",
    "max_steps_per_day": None,
}

CONFIG_PATH = Path.home() / ".config" / "strider" / "config.toml"

ENV_VARS = {
    "steps_per_km": ("STRIDER_STEPS_PER_KM", float),
    "speed": ("STRIDER_SPEED", float),
    "unit": ("STRIDER_UNIT", str),
    "max_steps_per_day": ("STRIDER_MAX_STEPS", int),
}


def load_config(config_path: Path = CONFIG_PATH) -> tuple[dict, list[str]]:
    """Load config with precedence: env vars > config file > defaults.

    Returns a (config_dict, sources) tuple where sources lists
    which layers contributed values (e.g. ["defaults", "config file", "env vars"]).
    """
    config = dict(DEFAULTS)
    sources = ["defaults"]

    # Layer config file values
    if config_path.exists():
        with open(config_path, "rb") as f:
            file_config = tomllib.load(f)
        for key in DEFAULTS:
            if key in file_config:
                config[key] = file_config[key]
        sources.append("config file")

    # Layer env var values
    has_env = False
    for key, (env_name, cast) in ENV_VARS.items():
        value = os.environ.get(env_name)
        if value is not None:
            config[key] = cast(value)
            has_env = True
    if has_env:
        sources.append("env vars")

    return config, sources


def create_config(config_path: Path = CONFIG_PATH) -> bool:
    """Write a starter config file with defaults. Returns False if file already exists."""
    if config_path.exists():
        return False

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        f"steps_per_km = {DEFAULTS['steps_per_km']}\n"
        f"speed = {DEFAULTS['speed']}\n"
        f'unit = "{DEFAULTS["unit"]}"\n'
    )
    return True
