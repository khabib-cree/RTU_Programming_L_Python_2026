"""Running queries against the flight database."""


from __future__ import annotations

import copy

from validator import parse_exact_datetime

ALLOWED_KEYS = {
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price",
    "min_price",
    "sort_by",
    "order",
    "limit",
}
SORTABLE_KEYS = {
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price",
}


def _is_number(val: object) -> bool:
    return isinstance(val, (int, float)) and not isinstance(val, bool)


def _is_int(val: object) -> bool:
    return isinstance(val, int) and not isinstance(val, bool)


def _validate_query(query: object) -> bool:
    if not isinstance(query, dict):
        return False

    for key in query:
        if not isinstance(key, str) or key not in ALLOWED_KEYS:
            return False

    for str_key in ("flight_id", "origin", "destination"):
        if str_key in query and not isinstance(query[str_key], str):
            return False

    for dt_key in ("departure_datetime", "arrival_datetime"):
        if dt_key in query:
            if not isinstance(query[dt_key], str) or parse_exact_datetime(query[dt_key]) is None:
                return False

    for price_key in ("price", "min_price"):
        if price_key in query and not _is_number(query[price_key]):
            return False

    if "order" in query and "sort_by" not in query:
        return False

    if "sort_by" in query:
        sort_by = query["sort_by"]
        if not isinstance(sort_by, str) or sort_by not in SORTABLE_KEYS:
            return False

    if "order" in query:
        if query["order"] not in ("asc", "desc"):
            return False

    if "limit" in query:
        limit = query["limit"]
        if not _is_int(limit) or limit < 0:
            return False

    return True


def _matches_flight(flight: dict, query: dict) -> bool:
    if "flight_id" in query and flight.get("flight_id") != query["flight_id"]:
        return False
    if "origin" in query and flight.get("origin") != query["origin"]:
        return False
    if "destination" in query and flight.get("destination") != query["destination"]:
        return False
    if "departure_datetime" in query and flight.get("departure_datetime", "") < query["departure_datetime"]:
        return False
    if "arrival_datetime" in query and flight.get("arrival_datetime", "") > query["arrival_datetime"]:
        return False
    if "price" in query and flight.get("price", float("inf")) > query["price"]:
        return False
    if "min_price" in query and flight.get("price", float("-inf")) < query["min_price"]:
        return False
    return True


def run_query(db: list[dict], query: dict) -> dict:
    """Execute a single query dictionary against the flight database."""
    query_snapshot = copy.deepcopy(query)
    if not _validate_query(query):
        return {
            "query": query_snapshot,
            "error": "INVALID_QUERY",
            "matches": [],
        }

    matched = [copy.deepcopy(flight) for flight in db if _matches_flight(flight, query)]

    if "sort_by" in query:
        sort_key = query["sort_by"]
        reverse = query.get("order", "asc") == "desc"
        matched = sorted(matched, key=lambda item: item[sort_key], reverse=reverse)

    if "limit" in query:
        matched = matched[: query["limit"]]

    return {
        "query": query_snapshot,
        "matches": matched,
    }


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Run a single query dict or a list of query dicts and return results."""
    query_list = [queries] if isinstance(queries, dict) else list(queries)
    return [run_query(db, q) for q in query_list]
