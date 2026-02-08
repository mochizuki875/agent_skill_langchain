---
name: week-weather-export
description: Get 1-week weather forecast via API script and export to a table file. Use when users request "this week's weather", "weather for the next 7 days", or want weather forecast in a file/table format.
---

# Week Weather Export

## Overview

Fetch a 7-day weather forecast by running `get_week_weather.sh <date>`, then format the results as a table and write them to a file (Markdown by default).

## Workflow

1. Determine the start date for the forecast.
   - If user requests "this week", use today's date (2026-02-03).
   - If user requests "next week", calculate the appropriate start date.
   - Accept absolute dates in `YYYY-MM-DD` format.
   - Use the user's locale/timezone when resolving relative dates.

2. **REQUIRED**: Ensure the output directory exists:
   - Always run this command first: `mkdir -p output`
   - This creates the output directory at project root if it doesn't exist
   - The script will fail without this directory

3. Run the export script with output path:
   - Command: `SKILLS/week-weather-export/scripts/export_weather.py <YYYY-MM-DD> --output output/weather-<YYYY-MM-DD>.md`
   - The `--output` parameter specifies the output file path relative to project root
   - File will be created at: `<project-root>/output/weather-<YYYY-MM-DD>.md`
   - Automatically fetches 7-day weather forecast and exports to table file

4. Read the generated file (optional):
   - Command: `cat output/weather-<YYYY-MM-DD>.md`
   - This displays the content to the user

## Script Usage

### Examples

- Markdown output to output directory:
  ```bash
  mkdir -p output
  SKILLS/week-weather-export/scripts/export_weather.py 2026-02-03 --output output/weather-2026-02-03.md
  ```

- CSV output to output directory:
  ```bash
  mkdir -p output
  SKILLS/week-weather-export/scripts/export_weather.py 2026-02-03 --format csv --output output/weather-2026-02-03.csv
  ```

- Next week's forecast:
  ```bash
  mkdir -p output
  SKILLS/week-weather-export/scripts/export_weather.py 2026-02-10 --output output/weather-2026-02-10.md
  ```

### Output Formats

- `md`: Markdown table (default)
- `csv`: Comma-separated values
- `tsv`: Tab-separated values

### Output Structure

- Default filename: `weather-<start-date>.<format>`
- Columns: `Date`, `Condition`, `High (°C)`, `Low (°C)`, `Precipitation (mm)`
- Returns a 7-day forecast starting from the provided date
- If no data is available, writes header + a single row with `Condition` = `No data available`

## Notes

- Always echo the resolved start date back to the user when they used a relative date.
- Keep outputs deterministic and stable for diffing.
- Temperature is always in Celsius (°C).
- Precipitation is in millimeters (mm).
