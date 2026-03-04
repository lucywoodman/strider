import os
import tomllib

from strider.config import DEFAULTS, load_config, create_config


class TestLoadConfigDefaults:
    def test_returns_defaults_when_no_config_or_env(self, tmp_path, monkeypatch):
        config_path = tmp_path / "config.toml"
        monkeypatch.delenv("STRIDER_STEPS_PER_KM", raising=False)
        monkeypatch.delenv("STRIDER_SPEED", raising=False)
        monkeypatch.delenv("STRIDER_UNIT", raising=False)

        result, sources = load_config(config_path)

        assert result == DEFAULTS
        assert sources == ["defaults"]

    def test_reads_values_from_config_file(self, tmp_path, monkeypatch):
        config_path = tmp_path / "config.toml"
        config_path.write_text('steps_per_km = 1320\nspeed = 4.8\nunit = "km"\n')
        monkeypatch.delenv("STRIDER_STEPS_PER_KM", raising=False)
        monkeypatch.delenv("STRIDER_SPEED", raising=False)
        monkeypatch.delenv("STRIDER_UNIT", raising=False)

        result, sources = load_config(config_path)

        assert result["steps_per_km"] == 1320
        assert result["speed"] == 4.8
        assert result["unit"] == "km"
        assert sources == ["defaults", "config file"]

    def test_partial_config_fills_rest_from_defaults(self, tmp_path, monkeypatch):
        config_path = tmp_path / "config.toml"
        config_path.write_text("steps_per_km = 1200\n")
        monkeypatch.delenv("STRIDER_STEPS_PER_KM", raising=False)
        monkeypatch.delenv("STRIDER_SPEED", raising=False)
        monkeypatch.delenv("STRIDER_UNIT", raising=False)

        result, sources = load_config(config_path)

        assert result["steps_per_km"] == 1200
        assert result["speed"] == DEFAULTS["speed"]
        assert result["unit"] == DEFAULTS["unit"]
        assert sources == ["defaults", "config file"]


class TestLoadConfigEnvVars:
    def test_env_vars_override_config_file(self, tmp_path, monkeypatch):
        config_path = tmp_path / "config.toml"
        config_path.write_text('steps_per_km = 1320\nspeed = 4.8\nunit = "km"\n')
        monkeypatch.setenv("STRIDER_STEPS_PER_KM", "1500")
        monkeypatch.setenv("STRIDER_SPEED", "6.0")
        monkeypatch.setenv("STRIDER_UNIT", "miles")

        result, sources = load_config(config_path)

        assert result["steps_per_km"] == 1500
        assert result["speed"] == 6.0
        assert result["unit"] == "miles"
        assert sources == ["defaults", "config file", "env vars"]

    def test_env_vars_override_defaults(self, tmp_path, monkeypatch):
        config_path = tmp_path / "config.toml"
        monkeypatch.setenv("STRIDER_SPEED", "3.5")
        monkeypatch.delenv("STRIDER_STEPS_PER_KM", raising=False)
        monkeypatch.delenv("STRIDER_UNIT", raising=False)

        result, sources = load_config(config_path)

        assert result["speed"] == 3.5
        assert result["steps_per_km"] == DEFAULTS["steps_per_km"]
        assert sources == ["defaults", "env vars"]


class TestCreateConfig:
    def test_creates_valid_toml_file(self, tmp_path):
        config_path = tmp_path / "strider" / "config.toml"

        create_config(config_path)

        assert config_path.exists()
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        assert data["steps_per_km"] == DEFAULTS["steps_per_km"]
        assert data["speed"] == DEFAULTS["speed"]
        assert data["unit"] == DEFAULTS["unit"]

    def test_does_not_overwrite_existing_file(self, tmp_path):
        config_path = tmp_path / "config.toml"
        config_path.write_text("steps_per_km = 9999\n")

        created = create_config(config_path)

        assert created is False
        assert "9999" in config_path.read_text()
