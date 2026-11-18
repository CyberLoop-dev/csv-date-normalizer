#!/usr/bin/env python3
"""Normalize one date column in a CSV without overwriting the source."""
import argparse
import csv
from datetime import datetime
from pathlib import Path
import sys

def normalize_value(value, source_format, target_format):
    if value == "":
        return value
    return datetime.strptime(value.strip(), source_format).strftime(target_format)

def normalize_file(source, destination, column, source_format, target_format, delimiter=",", force=False):
    src, dst = Path(source).resolve(), Path(destination).resolve()
    if src == dst:
        raise ValueError("Output path must differ from input path.")
    if dst.exists() and not force:
        raise FileExistsError(f"{dst} exists; pass --force to replace it.")
    with src.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=delimiter)
        if not reader.fieldnames or column not in reader.fieldnames:
            raise ValueError(f"Column {column!r} was not found.")
        fields = list(reader.fieldnames)
        rows, errors = [], []
        for line_number, row in enumerate(reader, start=2):
            raw = row.get(column, "")
            try:
                row[column] = normalize_value(raw, source_format, target_format)
            except ValueError:
                errors.append({"line": line_number, "value": raw})
            rows.append(row)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)
    return errors, len(rows)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--column", required=True)
    parser.add_argument("--from-format", required=True, help="Python strptime format")
    parser.add_argument("--to-format", default="%Y-%m-%d")
    parser.add_argument("--delimiter", default=",")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        errors, count = normalize_file(args.input, args.output, args.column, args.from_format, args.to_format, args.delimiter, args.force)
    except (OSError, ValueError) as exc:
        print(f"csv-date-normalizer: {exc}", file=sys.stderr)
        return 2
    print(f"Processed {count} rows; wrote {args.output}.")
    for error in errors:
        print(f"Could not parse line {error['line']}: {error['value']!r}", file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
