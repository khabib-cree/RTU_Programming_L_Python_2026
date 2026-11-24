"""Reading CSV files into flight records and error messages."""


from __future__ import annotations

import csv
import os
from pathlib import Path

from validator import to_record, validate_row


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Parse CSV files in order, returning (valid_records, error_messages)."""
    records: list[dict] = []
    errors: list[str] = []
    seen_flights: set[tuple[str, str]] = set()

    for file_path in paths:
        base_name = os.path.basename(file_path)
        content = Path(file_path).read_text(encoding="utf-8")
        lines = content.splitlines()

        for line_no, raw_line in enumerate(lines, start=1):
            if line_no == 1:
                continue

            if raw_line.strip() == "":
                continue

            if raw_line.lstrip().startswith("#"):
                continue

            fields = next(csv.reader([raw_line]))
            err_code = validate_row(fields, airports)
            if err_code is not None:
                errors.append(f"{base_name}:{line_no}: {err_code} | {raw_line}")
                continue

            record = to_record(fields)
            dedup_key = (record["flight_id"], record["departure_datetime"])
            if dedup_key in seen_flights:
                errors.append(f"{base_name}:{line_no}: DUPLICATE_FLIGHT | {raw_line}")
                continue

            seen_flights.add(dedup_key)
            records.append(record)

    return records, errors
