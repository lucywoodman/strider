STRIDE_HELP = """\
How to Estimate Steps per Kilometre
====================================

Quick Averages by Height:
  - Shorter (under 5'4"/163cm):     ~1,500-1,600 steps/km
  - Average (5'4"-5'10"/163-178cm): ~1,300-1,500 steps/km
  - Taller (over 5'10"/178cm):      ~1,200-1,400 steps/km

More Accurate Methods:
  - Walk a known distance: Find a 1km route (track, measured path)
    and count your steps
  - Use a football pitch: About 100m long - walk 10 lengths and
    count steps, then multiply by 10
  - Smartphone step counter: Many phones have built-in step counters
    you can test against known distances

Default used: 1,400 steps/km (a good average for most people)"""

SPEED_HELP = """\
How to Estimate Walking Speed
==============================

Typical Walking Speeds:
  - Leisurely stroll:      3-4 km/h (1.9-2.5 mph)
  - Comfortable pace:      4-5 km/h (2.5-3.1 mph)
  - Brisk walk:            5-6 km/h (3.1-3.7 mph)
  - Fast walk/power walk:  6-7 km/h (3.7-4.3 mph)

Quick Test:
  - Time yourself walking 1km (or 0.6 miles)
  - If it takes 12 minutes = 5 km/h
  - If it takes 15 minutes = 4 km/h
  - If it takes 10 minutes = 6 km/h

Factors that affect speed:
  - Terrain (hills, paths vs roads)
  - Weather conditions
  - Whether you're walking the dog (usually slower!)
  - Your fitness level

Default used: 5 km/h (a comfortable brisk pace for most people)"""

CONFIG_HELP = """\
Configuration
==============

Strider reads personal defaults from ~/.config/strider/config.toml
so you don't have to pass --steps-per-km, --speed, and --unit every time.

Quick start:
  strider config --init    Create a starter config file
  strider config           Show current resolved values

Precedence (highest to lowest):
  1. CLI flags (--speed 6.0)
  2. Environment variables (STRIDER_SPEED=6.0)
  3. Config file (~/.config/strider/config.toml)
  4. Built-in defaults

Environment variables:
  STRIDER_STEPS_PER_KM     Steps per kilometre
  STRIDER_SPEED            Walking speed in km/h
  STRIDER_UNIT             Preferred unit (km or miles)"""
