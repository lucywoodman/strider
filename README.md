# Strider

A walking goal calculator. Figure out how many steps, kilometres, or minutes you need to walk each day to hit a goal by a deadline.

Available as a [CLI tool](#setup) and a [web app](https://lucywoodman.github.io/strider/).

## Setup

```bash
uv sync
```

To install `strider` globally so you can run it from anywhere:

```bash
uv tool install .
```

Then use `strider` directly instead of `uv run strider`.

## Usage

### Calculate daily targets

```bash
# Steps goal
uv run strider calculate \
  --goal-type steps \
  --goal 300000 \
  --progress 50000 \
  --target-date 2026-03-31

# Distance goal (miles, custom stride rate and speed)
uv run strider calculate \
  --goal-type distance \
  --goal 200 \
  --progress 30 \
  --target-date 2026-03-31 \
  --unit miles \
  --steps-per-km 1500 \
  --speed 4.5
```

| Flag | Short | Required | Default | Description |
|---|---|---|---|---|
| `--goal-type` | `-t` | yes | | `steps` or `distance` |
| `--goal` | `-g` | yes | | Target amount |
| `--progress` | `-p` | yes | | Current progress |
| `--target-date` | `-d` | yes | | `YYYY-MM-DD`, `today`, or `tomorrow` |
| `--unit` | `-u` | no | config or `km` | `km` or `miles` (distance goals) |
| `--steps-per-km` | `-s` | no | config or `1400` | Your stride rate |
| `--speed` | `-k` | no | config or `5.0` | Walking speed in km/h |

### Configuration

Set your personal defaults once instead of passing `--steps-per-km`, `--speed`, and `--unit` every time.

```bash
strider config --init   # Create ~/.config/strider/config.toml with defaults
strider config          # Show current resolved values
```

The config file looks like:

```toml
steps_per_km = 1320
speed = 4.8
unit = "km"
```

Values are resolved in this order (highest wins):

1. CLI flags (`--speed 6.0`)
2. Environment variables (`STRIDER_SPEED=6.0`)
3. Config file (`~/.config/strider/config.toml`)
4. Built-in defaults

| Environment variable | Description |
|---|---|
| `STRIDER_STEPS_PER_KM` | Steps per kilometre |
| `STRIDER_SPEED` | Walking speed in km/h |
| `STRIDER_UNIT` | Preferred unit (`km` or `miles`) |

### Help guides

```bash
uv run strider help-stride   # How to estimate steps per km
uv run strider help-speed    # How to estimate walking speed
uv run strider help-config   # How to configure personal defaults
```

## Tests

```bash
uv run pytest
```
