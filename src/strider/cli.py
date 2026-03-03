import argparse
import sys
from datetime import date, datetime, timedelta

from strider.calculator import calculate
from strider.help_text import SPEED_HELP, STRIDE_HELP

DATE_SHORTCUTS = {
    "today": lambda: date.today(),
    "tomorrow": lambda: date.today() + timedelta(days=1),
}


def parse_date(value: str) -> date:
    if value.lower() in DATE_SHORTCUTS:
        return DATE_SHORTCUTS[value.lower()]()
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid date format: {value!r} (expected YYYY-MM-DD, 'today', or 'tomorrow')"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="strider",
        description="Walking goal calculator — figure out daily targets to hit your step or distance goal.",
        epilog="Run 'strider <command> --help' for more info on a command.",
    )
    subparsers = parser.add_subparsers(dest="command")

    calc = subparsers.add_parser("calculate", help="Calculate daily walking targets")
    calc.add_argument("-t", "--goal-type", choices=["steps", "distance"])
    calc.add_argument("-g", "--goal", type=float)
    calc.add_argument("-p", "--progress", type=float)
    calc.add_argument("-d", "--target-date", type=parse_date)
    calc.add_argument("-s", "--steps-per-km", type=float, default=1400)
    calc.add_argument("-k", "--speed", type=float, default=5.0)
    calc.add_argument("-u", "--unit", choices=["km", "miles"], default="km")

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
        parser.print_help()
        return

    if args.command == "help-stride":
        print(STRIDE_HELP)
        return

    if args.command == "help-speed":
        print(SPEED_HELP)
        return

    required = {"goal_type": "--goal-type/-t", "goal": "--goal/-g",
                "progress": "--progress/-p", "target_date": "--target-date/-d"}
    missing = [flag for attr, flag in required.items() if getattr(args, attr) is None]
    if len(missing) == len(required):
        # No flags at all — show help
        parser.parse_args(["calculate", "--help"])
    elif missing:
        parser.error(f"the following arguments are required: {', '.join(missing)}")

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
