import os
import tomllib
from pathlib import Path

DEFAULTS = {
    "steps_per_km": 1400,
    "speed": 5.0,
    "unit": "km",
}

CONFIG_PATH = Path.home() / ".config" / "strider" / "config.toml"

ENV_VARS = {
    "steps_per_km": ("STRIDER_STEPS_PER_KM", float),
    "speed": ("STRIDER_SPEED", float),
    "unit": ("STRIDER_UNIT", str),
}


def load_config(config_path: Path = CONFIG_PATH) -> dict:
    """Load config with precedence: env vars > config file > defaults."""
    config = dict(DEFAULTS)

    # Layer config file values
    if config_path.exists():
        with open(config_path, "rb") as f:
            file_config = tomllib.load(f)
        for key in DEFAULTS:
            if key in file_config:
                config[key] = file_config[key]

    # Layer env var values
    for key, (env_name, cast) in ENV_VARS.items():
        value = os.environ.get(env_name)
        if value is not None:
            config[key] = cast(value)

    return config


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
