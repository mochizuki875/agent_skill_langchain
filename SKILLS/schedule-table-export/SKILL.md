---
name: schedule-table-export
description: Run a schedule API via a script and export a specified date's schedule to a table file. Use when requests involve "today", "next Wednesday", specific dates like "2026-02-20", or when a user wants a date-based schedule in a file/table format.
---

# Schedule Table Export

## Overview

Fetch a date's schedule by running `get_schedule.py <date>`, then format the results as a table and write them to a file (Markdown by default).

## Workflow

1. Resolve the requested date key.
   - Accept `today`, `tomorrow`, or an absolute `YYYY-MM-DD`.
   - If the user says "next Wednesday", convert to an explicit date and confirm if ambiguous.
   - Use the user's locale/timezone when resolving relative dates.

2. **REQUIRED**: Ensure the output directory exists:
   - Always run this command first: `mkdir -p output`
   - This creates the output directory at project root if it doesn't exist
   - The script will fail without this directory

3. Run the export script with output path:
   - Command: `SKILLS/schedule-table-export/scripts/export_schedule.py <date> --output output/schedule-<date>.md`
   - The `--output` parameter specifies the output file path relative to project root
   - File will be created at: `<project-root>/output/schedule-<date>.md`
   - Accepts `today`, `tomorrow`, or `YYYY-MM-DD`
   - Automatically fetches schedule and exports to table file

4. Read the generated file (optional):
   - Command: `cat output/schedule-<date>.md`
   - This displays the content to the user

## Script Usage

### Examples

- Markdown output to output directory:
  ```bash
  mkdir -p output
  SKILLS/schedule-table-export/scripts/export_schedule.py today --output output/schedule-today.md
  ```

- CSV output to output directory:
  ```bash
  mkdir -p output
  SKILLS/schedule-table-export/scripts/export_schedule.py 2026-02-03 --format csv --output output/schedule-2026-02-03.csv
  ```

- Tomorrow's schedule:
  ```bash
  mkdir -p output
  SKILLS/schedule-table-export/scripts/export_schedule.py tomorrow --output output/schedule-tomorrow.md
  ```

### Output Formats

- `md`: Markdown table (default)
- `csv`: Comma-separated values
- `tsv`: Tab-separated values

### Output Structure

- Default filename: `schedule-<date>.<format>`
- Columns: `Time`, `Event`, `Location`
- If `location` is missing or empty, renders `-`
- If no events, writes header + a single row with `Event` = `No events`

## Notes

- Always echo the resolved date back to the user when they used a relative date.
- If multiple keys are returned, only export the requested key.
- Keep outputs deterministic and stable for diffing.
