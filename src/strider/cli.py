import argparse
import sys
from datetime import date, datetime

from strider.calculator import calculate
from strider.help_text import SPEED_HELP, STRIDE_HELP


def parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {value!r} (expected YYYY-MM-DD)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="strider",
        description="Walking goal calculator",
    )
    subparsers = parser.add_subparsers(dest="command")

    calc = subparsers.add_parser("calculate", help="Calculate daily walking targets")
    calc.add_argument("--goal-type", required=True, choices=["steps", "distance"])
    calc.add_argument("--goal", required=True, type=float)
    calc.add_argument("--progress", required=True, type=float)
    calc.add_argument("--target-date", required=True, type=parse_date)
    calc.add_argument("--steps-per-km", type=float, default=1400)
    calc.add_argument("--speed", type=float, default=5.0)
    calc.add_argument("--unit", choices=["km", "miles"], default="km")

    subparsers.add_parser("help-stride", help="How to estimate steps per km")
    subparsers.add_parser("help-speed", help="How to estimate walking speed")

    return parser


def format_result(result) -> str:
    if result.achieved:
        return "Congratulations! You've already achieved your goal!"

    status = "Achievable!" if result.achievable else "Challenging!"
    advice = (
        "This target looks achievable with consistent effort."
        if result.achievable
        else "This target is quite ambitious - consider if it's realistic for your lifestyle."
    )

    lines = [
        f"  {status} {advice}",
        "",
        f"  {'Steps Remaining:':<24} {result.steps_remaining:>10,} steps",
        f"  {'Days Remaining:':<24} {result.days_remaining:>10,} days",
        f"  {'Daily Steps Needed:':<24} {result.daily_steps:>10,} steps/day",
        f"  {'Daily Distance Needed:':<24} {result.daily_km:>10.1f} km ({result.daily_miles:.1f} miles)",
        f"  {'Daily Walking Time:':<24} {result.time_hours:>4}h {result.time_minutes:02}min",
    ]
    return "\n".join(lines)


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_usage(sys.stderr)
        sys.exit(2)

    if args.command == "help-stride":
        print(STRIDE_HELP)
        return

    if args.command == "help-speed":
        print(SPEED_HELP)
        return

    try:
        result = calculate(
            goal_type=args.goal_type,
            goal=args.goal,
            progress=args.progress,
            target_date=args.target_date,
            steps_per_km=args.steps_per_km,
            speed=args.speed,
            unit=args.unit,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(format_result(result))


if __name__ == "__main__":
    main()
