from datetime import date

import pytest

from strider.calculator import calculate


class TestBasicStepsGoal:
    def test_calculates_daily_steps(self):
        result = calculate(
            goal_type="steps",
            goal=300_000,
            progress=50_000,
            target_date=date(2026, 3, 31),
            today=date(2026, 3, 3),
        )
        # 29 days remaining (March 3 to March 31 inclusive)
        # 250,000 steps / 29 = 8621 (ceiling)
        assert result.daily_steps == 8_621
        assert result.days_remaining == 29
        assert result.steps_remaining == 250_000

    def test_calculates_daily_distance_km(self):
        result = calculate(
            goal_type="steps",
            goal=300_000,
            progress=50_000,
            target_date=date(2026, 3, 31),
            today=date(2026, 3, 3),
        )
        # 8620.69 steps / 1400 steps_per_km ≈ 6.2 km
        assert result.daily_km == pytest.approx(6.2, abs=0.1)

    def test_calculates_daily_distance_miles(self):
        result = calculate(
            goal_type="steps",
            goal=300_000,
            progress=50_000,
            target_date=date(2026, 3, 31),
            today=date(2026, 3, 3),
        )
        assert result.daily_miles == pytest.approx(3.8, abs=0.1)

    def test_calculates_walking_time(self):
        result = calculate(
            goal_type="steps",
            goal=300_000,
            progress=50_000,
            target_date=date(2026, 3, 31),
            today=date(2026, 3, 3),
        )
        # 6.16 km / 5.0 km/h = 1.23h → 1h 14min
        assert result.time_hours == 1
        assert result.time_minutes == 14


class TestDistanceGoals:
    def test_distance_in_km(self):
        result = calculate(
            goal_type="distance",
            goal=200,
            progress=30,
            target_date=date(2026, 3, 31),
            today=date(2026, 3, 3),
        )
        # 170 km remaining, converted to steps: 170 * 1400 = 238,000
        # 238,000 / 29 = 8207 (ceiling)
        assert result.steps_remaining == 238_000
        assert result.daily_steps == 8_207

    def test_distance_in_miles(self):
        result = calculate(
            goal_type="distance",
            goal=200,
            progress=30,
            target_date=date(2026, 3, 31),
            unit="miles",
            today=date(2026, 3, 3),
        )
        # 170 miles * 1.60934 = 273.59 km → 273.59 * 1400 = 383,027 steps
        assert result.steps_remaining == pytest.approx(383_027, abs=10)


class TestCustomParameters:
    def test_custom_stride_rate(self):
        result = calculate(
            goal_type="steps",
            goal=100_000,
            progress=0,
            target_date=date(2026, 3, 13),
            steps_per_km=1500,
            today=date(2026, 3, 3),
        )
        # 11 days, 100k steps, 9091 steps/day
        # 9090.9 / 1500 = 6.06 km
        assert result.daily_km == pytest.approx(6.1, abs=0.1)

    def test_custom_speed(self):
        result = calculate(
            goal_type="steps",
            goal=100_000,
            progress=0,
            target_date=date(2026, 3, 13),
            speed=4.0,
            today=date(2026, 3, 3),
        )
        # 9090.9 steps / 1400 = 6.49 km, 6.49 / 4.0 = 1.62h → 1h 37min
        assert result.time_hours == 1
        assert result.time_minutes == 37


class TestAlreadyAchieved:
    def test_goal_already_met(self):
        result = calculate(
            goal_type="steps",
            goal=100_000,
            progress=100_000,
            target_date=date(2026, 3, 31),
            today=date(2026, 3, 3),
        )
        assert result.achieved is True
        assert result.steps_remaining == 0

    def test_goal_exceeded(self):
        result = calculate(
            goal_type="steps",
            goal=100_000,
            progress=150_000,
            target_date=date(2026, 3, 31),
            today=date(2026, 3, 3),
        )
        assert result.achieved is True


class TestAchievability:
    def test_achievable_goal(self):
        result = calculate(
            goal_type="steps",
            goal=300_000,
            progress=50_000,
            target_date=date(2026, 3, 31),
            today=date(2026, 3, 3),
        )
        assert result.achievable is True

    def test_challenging_goal(self):
        result = calculate(
            goal_type="steps",
            goal=1_000_000,
            progress=0,
            target_date=date(2026, 3, 31),
            today=date(2026, 3, 3),
        )
        # 1,000,000 / 29 = 34,483 steps/day > 25,000 threshold
        assert result.achievable is False


class TestEdgeCases:
    def test_past_date_raises(self):
        with pytest.raises(ValueError, match="future"):
            calculate(
                goal_type="steps",
                goal=100_000,
                progress=0,
                target_date=date(2026, 3, 1),
                today=date(2026, 3, 3),
            )

    def test_target_is_today(self):
        result = calculate(
            goal_type="steps",
            goal=10_000,
            progress=0,
            target_date=date(2026, 3, 3),
            today=date(2026, 3, 3),
        )
        # 1 day remaining (today counts)
        assert result.days_remaining == 1
        assert result.daily_steps == 10_000

    def test_defaults_today_to_real_today(self):
        # Just verify it doesn't crash without explicit today
        result = calculate(
            goal_type="steps",
            goal=1_000_000,
            progress=0,
            target_date=date(2030, 12, 31),
        )
        assert result.days_remaining > 0
