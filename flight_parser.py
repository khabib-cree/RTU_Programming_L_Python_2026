"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import logging
from pathlib import Path
import sys

from csv_loader import parse_files
from query import run_queries
from validator import load_airports

STUDENT_ID = "251ADB033"
FIRST_NAME = "Khabibullo"
LAST_NAME = "Khudaykulov"


class _ArgumentParserError(Exception):
    pass


class _StrictArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise _ArgumentParserError(message)


def _build_parser() -> _StrictArgumentParser:
    parser = _StrictArgumentParser(prog="flight_parser.py", add_help=True)
    parser.add_argument("-i", dest="input_file", metavar="FILE", help="Parse a single CSV file")
    parser.add_argument(
        "-d",
        dest="input_dir",
        metavar="FOLDER",
        help="Parse every .csv file in the folder in sorted filename order",
    )
    parser.add_argument(
        "-j",
        dest="json_db",
        metavar="FILE",
        help="Load an existing JSON database instead of parsing CSVs",
    )
    parser.add_argument("-a", dest="airports_file", metavar="FILE", help="Airport list file")
    parser.add_argument(
        "-o",
        dest="output_db",
        metavar="FILE",
        help="Output path for JSON database (default: db.json)",
    )
    parser.add_argument("-q", dest="query_file", metavar="FILE", help="Run queries from JSON file")
    parser.add_argument(
        "-r",
        dest="response_dir",
        metavar="FOLDER",
        default=".",
        help="Folder for query response file (default: current directory)",
    )
    return parser


def _setup_logger(log_path: Path) -> tuple[logging.Logger, logging.FileHandler]:
    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    logger.addHandler(handler)
    return logger, handler


def _cleanup_logger(logger: logging.Logger, handler: logging.FileHandler | None) -> None:
    if handler is not None:
        logger.removeHandler(handler)
        handler.close()


def _fail_runtime(message: str) -> int:
    print(f"Error: {message}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    args_list = sys.argv[1:] if argv is None else argv
    parser = _build_parser()

    try:
        args = parser.parse_args(args_list)
    except _ArgumentParserError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    sources = [
        ("i", args.input_file),
        ("d", args.input_dir),
        ("j", args.json_db),
    ]
    active_sources = [(flag, val) for flag, val in sources if val is not None]

    if len(active_sources) == 0:
        print("Error: Exactly one data source (-i, -d, or -j) is required.", file=sys.stderr)
        return 2
    if len(active_sources) > 1:
        print("Error: Only one data source (-i, -d, or -j) may be specified.", file=sys.stderr)
        return 2

    source_flag, source_val = active_sources[0]

    if source_flag in ("i", "d") and not args.airports_file:
        print("Error: -a is required when using -i or -d.", file=sys.stderr)
        return 2

    if source_flag == "j" and args.output_db is not None:
        print("Error: -o cannot be used with -j.", file=sys.stderr)
        return 2

    db: list[dict] = []
    logger, handler = _setup_logger(Path(".")) if False else (logging.getLogger("flight_parser"), None)

    try:
        if source_flag in ("i", "d"):
            out_path = Path(args.output_db) if args.output_db is not None else Path("db.json")
            log_path = out_path.parent / "errors.log"
            logger, handler = _setup_logger(log_path)

            airports_path = Path(args.airports_file)
            if not airports_path.is_file():
                logger.error("Airport file not found: %s", airports_path)
                return _fail_runtime(f"Airport file not found: {airports_path}")

            try:
                airports = load_airports(str(airports_path))
            except OSError as exc:
                logger.error("Cannot read airport file %s: %s", airports_path, exc)
                return _fail_runtime(f"Cannot read airport file '{airports_path}': {exc}")

            csv_files: list[str] = []
            if source_flag == "i":
                in_file = Path(source_val)
                if not in_file.is_file():
                    logger.error("Input CSV file not found: %s", in_file)
                    return _fail_runtime(f"Input CSV file not found: {in_file}")
                csv_files = [str(in_file)]
            else:
                in_dir = Path(source_val)
                if not in_dir.is_dir():
                    logger.error("Input directory not found: %s", in_dir)
                    return _fail_runtime(f"Input directory not found: {in_dir}")
                try:
                    entries = sorted(
                        (p for p in in_dir.iterdir() if p.is_file() and p.name.endswith(".csv")),
                        key=lambda p: p.name,
                    )
                except OSError as exc:
                    logger.error("Cannot read directory %s: %s", in_dir, exc)
                    return _fail_runtime(f"Cannot read directory '{in_dir}': {exc}")
                if not entries:
                    logger.error("No .csv files found in directory: %s", in_dir)
                    return _fail_runtime(f"No .csv files found in '{in_dir}'.")
                csv_files = [str(p) for p in entries]

            try:
                db, err_messages = parse_files(csv_files, airports)
            except OSError as exc:
                logger.error("Failed reading CSV input: %s", exc)
                return _fail_runtime(f"Failed reading CSV input: {exc}")

            for msg in err_messages:
                logger.warning(msg)

            logger.info("Parsed %d valid flights with %d errors.", len(db), len(err_messages))

            try:
                out_path.write_text(json.dumps(db, indent=2), encoding="utf-8")
            except OSError as exc:
                logger.error("Failed writing database to %s: %s", out_path, exc)
                return _fail_runtime(f"Failed writing database to '{out_path}': {exc}")

        else:
            json_path = Path(source_val)
            if not json_path.is_file():
                return _fail_runtime(f"JSON database file not found: {json_path}")
            try:
                raw_text = json_path.read_text(encoding="utf-8")
                loaded_db = json.loads(raw_text)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                return _fail_runtime(f"Invalid JSON database '{json_path}': {exc}")

            if not isinstance(loaded_db, list) or not all(isinstance(item, dict) for item in loaded_db):
                return _fail_runtime("JSON database must be an array of objects.")

            db = loaded_db

        if args.query_file is not None:
            q_path = Path(args.query_file)
            if not q_path.is_file():
                return _fail_runtime(f"Query file not found: {q_path}")

            try:
                q_text = q_path.read_text(encoding="utf-8")
                parsed_queries = json.loads(q_text)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                return _fail_runtime(f"Invalid JSON query file '{q_path}': {exc}")

            if not isinstance(parsed_queries, (dict, list)):
                return _fail_runtime("Query file must contain a query object or an array of query objects.")

            if isinstance(parsed_queries, list) and not all(isinstance(q, dict) for q in parsed_queries):
                return _fail_runtime("Query array must contain only query objects.")

            resp_dir = Path(args.response_dir)
            if not resp_dir.is_dir():
                return _fail_runtime(f"Response directory not found: {resp_dir}")

            results = run_queries(db, parsed_queries)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            resp_filename = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{timestamp}.json"
            resp_path = resp_dir / resp_filename

            try:
                resp_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
            except OSError as exc:
                return _fail_runtime(f"Failed writing response file '{resp_path}': {exc}")

    finally:
        _cleanup_logger(logger, handler)

    return 0


if __name__ == "__main__":
    sys.exit(main())