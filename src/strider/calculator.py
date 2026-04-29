import math
from dataclasses import dataclass
from datetime import date

MILES_TO_KM = 1.60934


@dataclass
class WalkingResult:
    steps_remaining: int
    days_remaining: int
    daily_steps: int
    daily_km: float
    daily_miles: float
    time_hours: int
    time_minutes: int
    achieved: bool
    achievable: bool
    steps_today: int | None = None


def calculate(
    goal_type: str,
    goal: float,
    progress: float,
    target_date: date,
    steps_per_km: float = 1400,
    speed: float = 5.0,
    unit: str = "km",
    today: date | None = None,
    max_steps_per_day: int | None = None,
    steps_done_today: int | None = None,
) -> WalkingResult:
    if today is None:
        today = date.today()

    days_remaining = (target_date - today).days + 1

    if days_remaining <= 0:
        raise ValueError("Target date must be in the future!")

    # Convert to steps
    if goal_type == "distance":
        km_multiplier = MILES_TO_KM if unit == "miles" else 1
        goal_steps = goal * km_multiplier * steps_per_km
        current_steps = progress * km_multiplier * steps_per_km
    else:
        goal_steps = goal
        current_steps = progress

    steps_remaining = goal_steps - current_steps

    if steps_remaining <= 0:
        return WalkingResult(
            steps_remaining=0,
            days_remaining=days_remaining,
            daily_steps=0,
            daily_km=0.0,
            daily_miles=0.0,
            time_hours=0,
            time_minutes=0,
            achieved=True,
            achievable=True,
        )

    # Achievability check based on max_steps_per_day
    if max_steps_per_day is not None:
        today_capacity = max_steps_per_day - (steps_done_today or 0)
        total_capacity = max(0, today_capacity) + max_steps_per_day * (days_remaining - 1)
        achievable = steps_remaining <= total_capacity
    else:
        achievable = True

    # Calculate today-aware breakdown when steps_done_today is provided
    steps_today = None
    if steps_done_today is not None:
        fair_share = steps_remaining / days_remaining
        if max_steps_per_day is not None:
            capped_today = min(fair_share, max_steps_per_day)
        else:
            capped_today = fair_share
        steps_today = max(0, math.ceil(capped_today - steps_done_today))

        if days_remaining > 1:
            steps_after_today = steps_remaining - steps_today
            daily_steps_needed = steps_after_today / (days_remaining - 1)
        else:
            daily_steps_needed = steps_today
    else:
        daily_steps_needed = steps_remaining / days_remaining

    daily_km = daily_steps_needed / steps_per_km
    daily_miles = daily_km / MILES_TO_KM
    daily_time = daily_km / speed  # hours

    return WalkingResult(
        steps_remaining=math.ceil(steps_remaining),
        days_remaining=days_remaining,
        daily_steps=math.ceil(daily_steps_needed),
        daily_km=daily_km,
        daily_miles=daily_miles,
        time_hours=int(daily_time),
        time_minutes=round((daily_time % 1) * 60),
        achieved=False,
        achievable=achievable,
        steps_today=steps_today,
    )
