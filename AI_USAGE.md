# AI Usage Disclosure

<!--
Fill in this file before you submit. Submissions without it are not graded.
If you used no AI tools, delete everything below and write only:
No AI tools were used.
-->

## Tools used

- Gemini

## Conversation links

-https://share.gemini.google/2B73IjxnWcFE

## What I used them for

- to explain me datetime.strptime is not enough for the exact date and how regex + strptime work together
- how the checks from 1-11 and the only first failing code is returned
- physical 1-based line numbers are preserved while skipping headers and why csv.reader is still used on non-skipped lines
- And how the order without sort_by, invalid query keys/types, sort_by stability with sorted(..., reverse=True), and limit interact

## Which parts of the code were AI-generated or substantially AI-assisted

from datetime import datetime
import re

_DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")


def parse_exact_datetime(value: str) -> datetime | None:
    if not _DATETIME_RE.fullmatch(value):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError:
        return None



import math
import re
from datetime import datetime

_FLIGHT_ID_RE = re.compile(r"^[A-Za-z0-9]{2,8}$")
_AIRPORT_RE = re.compile(r"^[A-Z]{3}$")
_DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")


def _parse_dt(value: str) -> datetime | None:
    if not _DATETIME_RE.fullmatch(value):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError:
        return None


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    # 1. WRONG_FIELD_COUNT (check before indexing or stripping!)
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    stripped = [f.strip() for f in fields]
    flight_id, origin, destination, dep_str, arr_str, price_str = stripped

    # 2. MISSING_FIELD
    if any(val == "" for val in stripped):
        return "MISSING_FIELD"

    # 3. INVALID_FLIGHT_ID
    if not _FLIGHT_ID_RE.fullmatch(flight_id):
        return "INVALID_FLIGHT_ID"

    # 4. INVALID_ORIGIN
    if not _AIRPORT_RE.fullmatch(origin) or origin not in airports:
        return "INVALID_ORIGIN"

    # 5. INVALID_DESTINATION
    if not _AIRPORT_RE.fullmatch(destination) or destination not in airports:
        return "INVALID_DESTINATION"

    # 6. SAME_ORIGIN_DESTINATION
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    # 7. INVALID_DEPARTURE
    dep_dt = _parse_dt(dep_str)
    if dep_dt is None:
        return "INVALID_DEPARTURE"

    # 8. INVALID_ARRIVAL
    arr_dt = _parse_dt(arr_str)
    if arr_dt is None:
        return "INVALID_ARRIVAL"

    # 9. ARRIVAL_NOT_AFTER_DEPARTURE (uses dep_dt and arr_dt from checks 7-8)
    if arr_dt <= dep_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    # 10. INVALID_PRICE
    try:
        price = float(price_str)
    except ValueError:
        return "INVALID_PRICE"
    if not math.isfinite(price):
        return "INVALID_PRICE"

    # 11. NON_POSITIVE_PRICE (uses price from check 10)
    if price <= 0:
        return "NON_POSITIVE_PRICE"

    return None




if "sort_by" in query:
    sort_by = query["sort_by"]
    reverse = query.get("order", "asc") == "desc"
    matches = sorted(matches, key=lambda r: r[sort_by], reverse=reverse)

if "limit" in query:
    limit = query["limit"]
    matches = matches[:limit]

## Key prompts

1.In Python's strptime, directives like %m, %d, and %H accept one or two digits by default, and %Y can accept fewer than four digits in some cases. So datetime.strptime("2025-1-5 9:3", "%Y-%m-%d %H:%M") succeeds and returns datetime(2025, 1, 5, 9, 3), even though the spec requires strict zero-padding (YYYY-MM-DD HH:MM, e.g., 2025-01-05 09:03).
Also, strptime won't catch whitespace quirks around the separator if you aren't careful—for example, 2025-01-05  09:03 (two spaces) can still parse depending on whitespace handling
2.In query validation, that inheritance is a trap: isinstance(True, int) and isinstance(False, int) both return True. If you only check isinstance(val, (int, float)) or isinstance(val, int), a query like {"limit": True} or {"min_price": False} would slip through as a valid number or non-negative integer.

## What I changed or verified myself
-Modified parse_files in csv_loader.py to track 1-based physical line numbers while skipping the header, blank lines, and # comment lines, format error messages as <filename>:<line>: <ERROR_CODE> | <raw_line>, and detect DUPLICATE_FLIGHT across multiple CSV files using (flight_id, departure_datetime).
-Updated ALLOWED_KEYS and SORTABLE_KEYS in query.py to match the allowed query filter/sort/limit fields and valid flight record sort keys.
- Updated _build_parser in flight_parser.py to configure the CLI arguments (-i, -d, -j, -a, -o, -q, -r) and use _StrictArgumentParser for clean usage error handling.
