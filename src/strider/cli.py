import argparse
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from strider.calculator import calculate
from strider.config import CONFIG_PATH, load_config, create_config
from strider.help_text import CONFIG_HELP, SPEED_HELP, STRIDE_HELP

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


def _config_path() -> Path:
    """Return config path, allowing override via env var for testing."""
    override = os.environ.get("STRIDER_CONFIG_PATH")
    if override:
        return Path(override)
    return CONFIG_PATH


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
    calc.add_argument("-s", "--steps-per-km", type=float, default=None)
    calc.add_argument("-k", "--speed", type=float, default=None)
    calc.add_argument("-u", "--unit", choices=["km", "miles"], default=None)

    subparsers.add_parser("help-stride", help="How to estimate steps per km")
    subparsers.add_parser("help-speed", help="How to estimate walking speed")
    subparsers.add_parser("help-config", help="How to configure personal defaults")

    cfg = subparsers.add_parser("config", help="Show or initialise config")
    cfg.add_argument("--init", action="store_true", help="Create a starter config file")

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

    if args.command == "help-config":
        print(CONFIG_HELP)
        return

    config_path = _config_path()
    config = load_config(config_path)

    if args.command == "config":
        if args.init:
            created = create_config(config_path)
            if created:
                print(f"Created config file at {config_path}")
            else:
                print(f"Config file already exists at {config_path}")
            return

        print(f"Config file: {config_path}")
        if config_path.exists():
            print("Source: config file + defaults")
        else:
            print("Source: defaults (no config file found)")
        print()
        for key, value in config.items():
            print(f"  {key} = {value}")
        return

    # Fill in None args from config
    if args.steps_per_km is None:
        args.steps_per_km = config["steps_per_km"]
    if args.speed is None:
        args.speed = config["speed"]
    if args.unit is None:
        args.unit = config["unit"]

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
