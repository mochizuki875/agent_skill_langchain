#!/usr/bin/env python3
"""
Fetch weather forecast and export to table format.

Usage:
    python export_weather.py 2026-02-03
    python export_weather.py 2026-02-10 --format csv
"""

import argparse
from pathlib import Path


# Mock weather data
MOCK_WEATHER = {
    "days": [
        {"date": "Sunday", "condition": "Clear", "temp_high_c": 11, "temp_low_c": 0, "precip_mm": 0},
        {"date": "Monday", "condition": "Windy", "temp_high_c": 9, "temp_low_c": 1, "precip_mm": 0},
        {"date": "Tuesday", "condition": "Sunny", "temp_high_c": 12, "temp_low_c": 3, "precip_mm": 0},
        {"date": "Wednesday", "condition": "Partly Cloudy", "temp_high_c": 10, "temp_low_c": 2, "precip_mm": 0},
        {"date": "Thursday", "condition": "Cloudy", "temp_high_c": 9, "temp_low_c": 1, "precip_mm": 0},
        {"date": "Friday", "condition": "Light Rain", "temp_high_c": 8, "temp_low_c": 2, "precip_mm": 3},
        {"date": "Saturday", "condition": "Rain", "temp_high_c": 7, "temp_low_c": 1, "precip_mm": 8}
    ]
}


def get_weather_forecast(start_date: str) -> list:
    """Get weather forecast data (returns mock data)."""
    # In a real implementation, this would call an API with start_date
    return MOCK_WEATHER["days"]


def format_markdown(days):
    """Format weather data as Markdown table."""
    if not days:
        return "| Date | Condition | High (°C) | Low (°C) | Precipitation (mm) |\n" + \
               "|------|-----------|-----------|----------|--------------------|\n" + \
               "| - | No data available | - | - | - |"
    
    lines = [
        "| Date | Condition | High (°C) | Low (°C) | Precipitation (mm) |",
        "|------|-----------|-----------|----------|--------------------| "
    ]
    
    for day in days:
        date = day.get('date', '-')
        condition = day.get('condition', '-')
        high = day.get('temp_high_c', '-')
        low = day.get('temp_low_c', '-')
        precip = day.get('precip_mm', '-')
        lines.append(f"| {date} | {condition} | {high} | {low} | {precip} |")
    
    return '\n'.join(lines)


def format_csv(days, delimiter=','):
    """Format weather data as CSV/TSV."""
    if not days:
        header = f"Date{delimiter}Condition{delimiter}High (°C){delimiter}Low (°C){delimiter}Precipitation (mm)"
        row = f"-{delimiter}No data available{delimiter}-{delimiter}-{delimiter}-"
        return f"{header}\n{row}"
    
    lines = [f"Date{delimiter}Condition{delimiter}High (°C){delimiter}Low (°C){delimiter}Precipitation (mm)"]
    
    for day in days:
        date = day.get('date', '-')
        condition = day.get('condition', '-')
        high = day.get('temp_high_c', '-')
        low = day.get('temp_low_c', '-')
        precip = day.get('precip_mm', '-')
        lines.append(f"{date}{delimiter}{condition}{delimiter}{high}{delimiter}{low}{delimiter}{precip}")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description="Fetch weather forecast and export to table")
    parser.add_argument("start_date", help="Start date in YYYY-MM-DD format")
    parser.add_argument("--format", choices=["md", "csv", "tsv"], default="md")
    parser.add_argument("--output", help="Output file path (default: weather-<start-date>.<ext>)")
    args = parser.parse_args()
    
    # Get weather forecast data
    weather_data = get_weather_forecast(args.start_date)
    
    # Format output
    if args.format == "md":
        output = format_markdown(weather_data)
        default_filename = f"weather-{args.start_date}.md"
    elif args.format == "csv":
        output = format_csv(weather_data, delimiter=',')
        default_filename = f"weather-{args.start_date}.csv"
    elif args.format == "tsv":
        output = format_csv(weather_data, delimiter='\t')
        default_filename = f"weather-{args.start_date}.tsv"
    
    # Determine output file
    output_file = args.output or default_filename
    
    # Write to file
    output_path = Path(output_file)
    output_path.write_text(output + '\n', encoding='utf-8')
    print(f"Weather forecast written to: {output_file}")


if __name__ == '__main__':
    main()
