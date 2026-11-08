"""Scan a timestamped sensor CSV for high readings and sampling gaps."""

import argparse
import csv
import json
import math
from pathlib import Path


def analyze(stream, *, limit, max_gap_ms):
    if not math.isfinite(limit):
        raise ValueError("limit must be finite")
    if type(max_gap_ms) is not int or max_gap_ms < 1:
        raise ValueError("max_gap_ms must be a positive integer")

    reader = csv.reader(stream, strict=True)
    if next(reader, None) != ["time_ms", "value"]:
        raise ValueError("CSV header must be time_ms,value")

    previous = None
    active = None
    count = 0
    alerts = []
    gaps = []

    for row in reader:
        line = reader.line_num
        try:
            timestamp_text, value_text = row
            timestamp = int(timestamp_text)
            value = float(value_text)
        except ValueError as exc:
            raise ValueError(f"line {line}: expected integer time_ms and numeric value") from exc
        if timestamp < 0 or not math.isfinite(value):
            raise ValueError(f"line {line}: time_ms must be nonnegative and value finite")

        if previous is not None:
            gap = timestamp - previous
            if gap <= 0:
                raise ValueError(f"line {line}: time_ms must strictly increase")
            if gap > max_gap_ms:
                gaps.append({"after_ms": previous, "before_ms": timestamp, "gap_ms": gap})
                active = None

        if value >= limit:
            if active is None:
                active = {"first_ms": timestamp, "last_ms": timestamp, "samples": 0, "peak": value}
                alerts.append(active)
            active["last_ms"] = timestamp
            active["samples"] += 1
            active["peak"] = max(active["peak"], value)
        else:
            active = None

        previous = timestamp
        count += 1

    if not count:
        raise ValueError("CSV has no samples")
    return {"samples": count, "limit": limit, "max_gap_ms": max_gap_ms,
            "alerts": alerts, "gaps": gaps}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--limit", type=float, required=True)
    parser.add_argument("--max-gap-ms", type=int, required=True)
    args = parser.parse_args()
    try:
        with args.csv_file.open(newline="", encoding="utf-8-sig") as stream:
            report = analyze(stream, limit=args.limit, max_gap_ms=args.max_gap_ms)
    except (OSError, ValueError, csv.Error) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
