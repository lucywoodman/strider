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


class TestStepsDoneToday:
    def test_steps_today_not_set_when_not_provided(self):
        result = calculate(
            goal_type="steps",
            goal=300_000,
            progress=50_000,
            target_date=date(2026, 3, 31),
            today=date(2026, 3, 3),
        )
        assert result.steps_today is None

    def test_steps_today_with_fair_share(self):
        # 30,818 remaining / 2 days = 15,409 fair share
        # Done today: 11,177. Steps today: 15,409 - 11,177 = 4,232
        result = calculate(
            goal_type="steps",
            goal=300_000,
            progress=269_182,
            target_date=date(2026, 4, 30),
            steps_done_today=11_177,
            today=date(2026, 4, 29),
        )
        assert result.steps_today == 4_232

    def test_daily_steps_is_future_average_when_today_provided(self):
        # 30,818 remaining, today does 4,232 more. Future: 30,818 - 4,232 = 26,586 / 1 day
        result = calculate(
            goal_type="steps",
            goal=300_000,
            progress=269_182,
            target_date=date(2026, 4, 30),
            steps_done_today=11_177,
            today=date(2026, 4, 29),
        )
        assert result.daily_steps == 26_586

    def test_steps_today_zero_when_exceeded_fair_share(self):
        # Fair share: 30,818 / 2 = 15,409. Done today: 20,000 > 15,409
        result = calculate(
            goal_type="steps",
            goal=300_000,
            progress=269_182,
            target_date=date(2026, 4, 30),
            steps_done_today=20_000,
            today=date(2026, 4, 29),
        )
        assert result.steps_today == 0

    def test_steps_today_when_target_is_today(self):
        # Only 1 day remaining, 10,000 steps left, done 3,000 today
        result = calculate(
            goal_type="steps",
            goal=10_000,
            progress=0,
            target_date=date(2026, 3, 3),
            steps_done_today=3_000,
            today=date(2026, 3, 3),
        )
        # Fair share is 10,000 (all remaining). Steps today = 10,000 - 3,000 = 7,000
        assert result.steps_today == 7_000
        assert result.daily_steps == 7_000


class TestMaxStepsPerDay:
    def test_always_achievable_without_max(self):
        result = calculate(
            goal_type="steps",
            goal=1_000_000,
            progress=0,
            target_date=date(2026, 3, 31),
            today=date(2026, 3, 3),
        )
        assert result.achievable is True

    def test_achievable_within_capacity(self):
        # 10,000 remaining / 2 days, max 15,000. Capacity: 15,000 * 2 = 30,000 > 10,000
        result = calculate(
            goal_type="steps",
            goal=10_000,
            progress=0,
            target_date=date(2026, 3, 4),
            max_steps_per_day=15_000,
            today=date(2026, 3, 3),
        )
        assert result.achievable is True

    def test_not_achievable_over_capacity(self):
        # 30,818 remaining / 2 days, max 15,000.
        # Capacity: 15,000 * 2 = 30,000 < 30,818
        result = calculate(
            goal_type="steps",
            goal=300_000,
            progress=269_182,
            target_date=date(2026, 4, 30),
            max_steps_per_day=15_000,
            today=date(2026, 4, 29),
        )
        assert result.achievable is False

    def test_not_achievable_with_today_capacity_reduced(self):
        # 30,818 remaining, max 15,000, done today 11,177
        # Capacity: (15,000 - 11,177) + 15,000 = 18,823 < 30,818
        result = calculate(
            goal_type="steps",
            goal=300_000,
            progress=269_182,
            target_date=date(2026, 4, 30),
            max_steps_per_day=15_000,
            steps_done_today=11_177,
            today=date(2026, 4, 29),
        )
        assert result.achievable is False

    def test_steps_today_capped_by_max(self):
        # Fair share: 50,000 / 2 = 25,000. Max: 15,000. Done: 5,000.
        # steps_today = min(25,000, 15,000) - 5,000 = 10,000
        result = calculate(
            goal_type="steps",
            goal=50_000,
            progress=0,
            target_date=date(2026, 3, 4),
            max_steps_per_day=15_000,
            steps_done_today=5_000,
            today=date(2026, 3, 3),
        )
        assert result.steps_today == 10_000
        # Future: 50,000 - 10,000 = 40,000 / 1 day = 40,000
        assert result.daily_steps == 40_000


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


