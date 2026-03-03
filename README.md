# Strider

A CLI walking goal calculator. Figure out how many steps, kilometres, or minutes you need to walk each day to hit a goal by a deadline.

## Setup

```bash
uv sync
```

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

| Flag | Required | Default | Description |
|---|---|---|---|
| `--goal-type` | yes | | `steps` or `distance` |
| `--goal` | yes | | Target amount |
| `--progress` | yes | | Current progress |
| `--target-date` | yes | | Deadline (`YYYY-MM-DD`) |
| `--unit` | no | `km` | `km` or `miles` (distance goals) |
| `--steps-per-km` | no | `1400` | Your stride rate |
| `--speed` | no | `5.0` | Walking speed in km/h |

### Help guides

```bash
uv run strider help-stride   # How to estimate steps per km
uv run strider help-speed    # How to estimate walking speed
```

## Tests

```bash
uv run pytest
```
