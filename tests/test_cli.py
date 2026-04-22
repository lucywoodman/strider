import os
import subprocess
import sys


def run_strider(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "strider.cli", *args],
        capture_output=True,
        text=True,
    )


class TestCalculateCommand:
    def test_valid_steps_calculation(self):
        result = run_strider(
            "calculate",
            "--goal-type", "steps",
            "--goal", "300000",
            "--progress", "50000",
            "--target-date", "2030-12-31",
        )
        assert result.returncode == 0
        assert "Daily Steps Needed" in result.stdout
        assert "steps/day" in result.stdout

    def test_valid_distance_calculation(self):
        result = run_strider(
            "calculate",
            "--goal-type", "distance",
            "--goal", "200",
            "--progress", "30",
            "--target-date", "2030-12-31",
            "--unit", "miles",
        )
        assert result.returncode == 0
        assert "Daily Steps Needed" in result.stdout

    def test_already_achieved(self):
        result = run_strider(
            "calculate",
            "--goal-type", "steps",
            "--goal", "100000",
            "--progress", "100000",
            "--target-date", "2030-12-31",
        )
        assert result.returncode == 0
        assert "already achieved" in result.stdout.lower()

    def test_past_date_error(self):
        result = run_strider(
            "calculate",
            "--goal-type", "steps",
            "--goal", "100000",
            "--progress", "0",
            "--target-date", "2020-01-01",
        )
        assert result.returncode != 0
        assert "future" in result.stderr.lower()


class TestShortFlags:
    def test_short_flags(self):
        result = run_strider(
            "calculate",
            "-t", "steps",
            "-g", "300000",
            "-p", "50000",
            "-d", "2030-12-31",
        )
        assert result.returncode == 0
        assert "Daily Steps Needed" in result.stdout

    def test_short_flags_distance(self):
        result = run_strider(
            "calculate",
            "-t", "distance",
            "-g", "200",
            "-p", "30",
            "-d", "2030-12-31",
            "-u", "miles",
            "-s", "1500",
            "-k", "4.5",
        )
        assert result.returncode == 0
        assert "Daily Steps Needed" in result.stdout


class TestMissingFlags:
    def test_missing_goal_type(self):
        result = run_strider(
            "calculate",
            "--goal", "100000",
            "--progress", "0",
            "--target-date", "2030-12-31",
        )
        assert result.returncode != 0

    def test_no_subcommand_shows_help(self):
        result = run_strider()
        assert result.returncode == 0
        assert "calculate" in result.stdout
        assert "help-stride" in result.stdout
        assert "help-speed" in result.stdout

    def test_calculate_no_flags_shows_help(self):
        result = run_strider("calculate")
        assert result.returncode == 0
        assert "--goal-type" in result.stdout
        assert "--goal" in result.stdout


class TestDateShortcuts:
    def test_today_as_target_date(self):
        result = run_strider(
            "calculate",
            "--goal-type", "steps",
            "--goal", "10000",
            "--progress", "0",
            "--target-date", "today",
        )
        assert result.returncode == 0
        assert "1 days" in result.stdout or "already achieved" in result.stdout.lower()

    def test_tomorrow_as_target_date(self):
        result = run_strider(
            "calculate",
            "--goal-type", "steps",
            "--goal", "10000",
            "--progress", "0",
            "--target-date", "tomorrow",
        )
        assert result.returncode == 0


class TestInvalidInput:
    def test_invalid_date_format(self):
        result = run_strider(
            "calculate",
            "--goal-type", "steps",
            "--goal", "100000",
            "--progress", "0",
            "--target-date", "not-a-date",
        )
        assert result.returncode != 0


class TestHelpSubcommands:
    def test_help_stride(self):
        result = run_strider("help-stride")
        assert result.returncode == 0
        assert "steps per kilometre" in result.stdout.lower()

    def test_help_speed(self):
        result = run_strider("help-speed")
        assert result.returncode == 0
        assert "walking speed" in result.stdout.lower()


class TestConfigSubcommand:
    def test_config_shows_current_values(self):
        result = run_strider("config")
        assert result.returncode == 0
        assert "steps_per_km" in result.stdout
        assert "speed" in result.stdout
        assert "unit" in result.stdout

    def test_config_init_creates_file(self, tmp_path):
        config_path = tmp_path / "config.toml"
        env = os.environ.copy()
        env["STRIDER_CONFIG_PATH"] = str(config_path)
        result = subprocess.run(
            [sys.executable, "-m", "strider.cli", "config", "--init"],
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0
        assert config_path.exists()
        assert "Created" in result.stdout

    def test_config_init_does_not_overwrite(self, tmp_path):
        config_path = tmp_path / "config.toml"
        config_path.write_text("steps_per_km = 9999\n")
        env = os.environ.copy()
        env["STRIDER_CONFIG_PATH"] = str(config_path)
        result = subprocess.run(
            [sys.executable, "-m", "strider.cli", "config", "--init"],
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0
        assert "already exists" in result.stdout.lower()


class TestWarningFlag:
    def test_warning_shown_when_target_exceeds_2x_average(self):
        result = run_strider(
            "calculate",
            "-t", "steps",
            "-g", "300000",
            "-p", "0",
            "-d", "tomorrow",
            "--current-average", "1000",
        )
        assert result.returncode == 0
        assert "Note:" in result.stdout
        assert "doubling" in result.stdout

    def test_no_warning_when_average_not_provided(self):
        result = run_strider(
            "calculate",
            "-t", "steps",
            "-g", "300000",
            "-p", "50000",
            "-d", "2030-12-31",
        )
        assert result.returncode == 0
        assert "Note:" not in result.stdout

    def test_short_flag(self):
        result = run_strider(
            "calculate",
            "-t", "steps",
            "-g", "300000",
            "-p", "0",
            "-d", "tomorrow",
            "-a", "1000",
        )
        assert result.returncode == 0
        assert "Note:" in result.stdout


class TestEnvVarsAffectCalculation:
    def test_env_speed_affects_walking_time(self):
        env = os.environ.copy()
        env["STRIDER_SPEED"] = "10.0"
        result = subprocess.run(
            [
                sys.executable, "-m", "strider.cli",
                "calculate",
                "-t", "steps", "-g", "300000", "-p", "50000", "-d", "2030-12-31",
            ],
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0
        assert "Daily Walking Time" in result.stdout
