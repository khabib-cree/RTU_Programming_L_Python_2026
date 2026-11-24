"""Row validation: airport list loading, single-row checks, record building."""


from __future__ import annotations

from datetime import datetime
import math
from pathlib import Path
import re

FLIGHT_ID_RE = re.compile(r"^[A-Za-z0-9]{2,8}$")
AIRPORT_CODE_RE = re.compile(r"^[A-Z]{3}$")
DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")
DATETIME_FMT = "%Y-%m-%d %H:%M"


def parse_exact_datetime(value: str) -> datetime | None:
    """Parse YYYY-MM-DD HH:MM strictly with zero-padded fields and 24-hour clock."""
    if not isinstance(value, str) or not DATETIME_RE.fullmatch(value):
        return None
    try:
        return datetime.strptime(value, DATETIME_FMT)
    except ValueError:
        return None


def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of airport codes."""
    airports: set[str] = set()
    content = Path(path).read_text(encoding="utf-8")
    for line in content.splitlines():
        code = line.strip()
        if not code or code.startswith("#"):
            continue
        airports.add(code)
    return airports


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Validate a single CSV row (checks 1-11). Returns None if valid or error code."""
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    stripped = [f.strip() for f in fields]
    flight_id, origin, destination, dep_str, arr_str, price_str = stripped

    if any(val == "" for val in stripped):
        return "MISSING_FIELD"

    if not FLIGHT_ID_RE.fullmatch(flight_id):
        return "INVALID_FLIGHT_ID"

    if not AIRPORT_CODE_RE.fullmatch(origin) or origin not in airports:
        return "INVALID_ORIGIN"

    if not AIRPORT_CODE_RE.fullmatch(destination) or destination not in airports:
        return "INVALID_DESTINATION"

    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    dep_dt = parse_exact_datetime(dep_str)
    if dep_dt is None:
        return "INVALID_DEPARTURE"

    arr_dt = parse_exact_datetime(arr_str)
    if arr_dt is None:
        return "INVALID_ARRIVAL"

    if arr_dt <= dep_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        price_val = float(price_str)
    except ValueError:
        return "INVALID_PRICE"

    if not math.isfinite(price_val):
        return "INVALID_PRICE"

    if price_val <= 0:
        return "NON_POSITIVE_PRICE"

    return None


def to_record(fields: list[str]) -> dict:
    """Convert a valid row into a flight record dictionary."""
    flight_id, origin, destination, dep_str, arr_str, price_str = (
        f.strip() for f in fields
    )
    return {
        "flight_id": flight_id,
        "origin": origin,
        "destination": destination,
        "departure_datetime": dep_str,
        "arrival_datetime": arr_str,
        "price": float(price_str),
    }
