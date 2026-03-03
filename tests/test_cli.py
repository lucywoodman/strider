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
