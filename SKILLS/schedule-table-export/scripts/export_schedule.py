#!/usr/bin/env python3
"""
Fetch schedule and export to table format.

Usage:
    python export_schedule.py today
    python export_schedule.py 2026-02-03 --format csv
"""

import argparse
import json
from pathlib import Path


# Mock schedule data
MOCK_SCHEDULE = {
    "today": [
        {"time": "01:00", "event": "Talk with Stefan at NativeCamp", "location": "NativeCamp"},
        {"time": "09:00", "event": "Drop off kids at kindergarten", "location": "Kindergarten"},
        {"time": "13:30", "event": "Get a haircut in Shinjuku", "location": "Shinjuku"},
        {"time": "17:00", "event": "Pick up kids from kindergarten", "location": "Kindergarten"},
        {"time": "18:00", "event": "AI meeting with colleagues", "location": "Online"}
    ],
    "tomorrow": [
        {"time": "10:00", "event": "Team standup", "location": "Office"},
        {"time": "14:00", "event": "Client presentation", "location": "Conference Room A"}
    ]
}


def get_schedule(date_key: str) -> list:
    """Get schedule data for the given date key."""
    return MOCK_SCHEDULE.get(date_key, [])


def normalize_rows(rows):
    """Normalize schedule rows."""
    normalized = []
    for item in rows:
        time = str(item.get("time", "")).strip()
        event = str(item.get("event", "")).strip()
        location = str(item.get("location", "")).strip() or "-"
        normalized.append({"time": time, "event": event, "location": location})
    normalized.sort(key=lambda r: r["time"])
    return normalized


def format_markdown(rows):
    """Format schedule as Markdown table."""
    if not rows:
        return "| Time | Event | Location |\n|------|-------|----------|\n| - | No events | - |"
    
    lines = ["| Time | Event | Location |", "|------|-------|----------|"]
    for row in rows:
        lines.append(f"| {row['time']} | {row['event']} | {row['location']} |")
    return "\n".join(lines)


def format_csv(rows, delimiter=","):
    """Format schedule as CSV/TSV."""
    if not rows:
        return f"Time{delimiter}Event{delimiter}Location\n-{delimiter}No events{delimiter}-"
    
    lines = [f"Time{delimiter}Event{delimiter}Location"]
    for row in rows:
        lines.append(f"{row['time']}{delimiter}{row['event']}{delimiter}{row['location']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Fetch schedule and export to table")
    parser.add_argument("date", help="Date: today, tomorrow, or YYYY-MM-DD")
    parser.add_argument("--format", choices=["md", "csv", "tsv"], default="md")
    parser.add_argument("--output", help="Output file path (default: schedule-<date>.<ext>)")
    args = parser.parse_args()
    
    # Get schedule data
    schedule_data = get_schedule(args.date)
    
    # Normalize rows
    rows = normalize_rows(schedule_data)
    
    # Format output
    if args.format == "md":
        output = format_markdown(rows)
        default_filename = f"schedule-{args.date}.md"
    elif args.format == "csv":
        output = format_csv(rows, delimiter=",")
        default_filename = f"schedule-{args.date}.csv"
    elif args.format == "tsv":
        output = format_csv(rows, delimiter="\t")
        default_filename = f"schedule-{args.date}.tsv"
    
    # Determine output file
    output_file = args.output or default_filename
    
    # Write to file
    output_path = Path(output_file)
    output_path.write_text(output + "\n", encoding="utf-8")
    print(f"Schedule written to: {output_file}")


if __name__ == "__main__":
    main()
