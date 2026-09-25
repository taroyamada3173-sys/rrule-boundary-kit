"""RRULE Boundary Kit 0.1.0: compare occurrence output against fixed fixtures.

Python 3.10+, standard library only. This is a comparator, not an RRULE engine.
"""
import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import re
import sys

VERSION = "0.1.0"
FIXTURES = Path(__file__).with_name("cases.json")
STAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle, object_pairs_hook=unique_object)


def validate_stamps(items):
    if not isinstance(items, list):
        raise ValueError("Each case must contain an array of UTC timestamps")
    for value in items:
        if not isinstance(value, str) or not STAMP.fullmatch(value):
            raise ValueError("Use YYYY-MM-DDTHH:MM:SSZ for every occurrence")
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")


def load_cases():
    data = read_json(FIXTURES)
    if data.get("version") != VERSION or not isinstance(data.get("cases"), list):
        raise ValueError("Fixture version or structure mismatch")
    ids = set()
    for case in data["cases"]:
        if not isinstance(case.get("id"), str) or case["id"] in ids:
            raise ValueError("Invalid or duplicate fixture ID")
        ids.add(case["id"])
        validate_stamps(case["expected"])
        if case["expected"] != sorted(set(case["expected"])):
            raise ValueError("Expected fixtures must be ordered and unique")
    if not ids:
        raise ValueError("Empty fixture suite")
    return data["cases"]


def compare(cases, actual):
    if not isinstance(actual, dict):
        raise ValueError("Result JSON must be an object keyed by case ID")
    expected_ids = {case["id"] for case in cases}
    unknown = sorted(set(actual) - expected_ids)
    results = []
    for case in cases:
        case_id = case["id"]
        if case_id not in actual:
            results.append({"id": case_id, "passed": False, "error": "missing_case"})
            continue
        values = actual[case_id]
        validate_stamps(values)
        missing = list((Counter(case["expected"]) - Counter(values)).elements())
        extra = list((Counter(values) - Counter(case["expected"])).elements())
        results.append({
            "id": case_id, "passed": values == case["expected"],
            "missing": missing, "extra": extra,
            "out_of_order": values != sorted(values),
        })
    passed = not unknown and all(row["passed"] for row in results)
    return {"version": VERSION, "passed": passed, "cases": results,
            "unknown_cases": unknown, "passed_count": sum(row["passed"] for row in results),
            "total": len(cases)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="Show the fixed fixture descriptions")
    sub.add_parser("example", help="Print expected JSON to show the output contract; not an engine test")
    check = sub.add_parser("check", help="Compare YOUR engine output with the fixed expectations")
    check.add_argument("actual", help="Path to JSON output keyed by case ID")
    args = parser.parse_args(argv)
    try:
        cases = load_cases()
        if args.command == "list":
            for case in cases:
                print(case["id"] + ": " + case["description"])
            return 0
        if args.command == "example":
            print(json.dumps({case["id"]: case["expected"] for case in cases}, indent=2))
            return 0
        result = compare(cases, read_json(args.actual))
        print(json.dumps(result, indent=2))
        return 0 if result["passed"] else 1
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"passed": False, "input_error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
