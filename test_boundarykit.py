"""Comparator negative controls and fixed date expectations; no dependencies."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import boundarykit as kit


class ComparatorTests(unittest.TestCase):
    def setUp(self):
        self.cases = kit.load_cases()
        self.actual = {c["id"]: list(c["expected"]) for c in self.cases}
        self.key = "month_31_skip"

    def test_correct_output_passes(self):
        self.assertTrue(kit.compare(self.cases, self.actual)["passed"])

    def test_every_case_detects_missing_occurrence(self):
        for case in self.cases:
            with self.subTest(case=case["id"]):
                actual = copy.deepcopy(self.actual)
                actual[case["id"]].pop()
                self.assertFalse(kit.compare(self.cases, actual)["passed"])

    def test_every_case_detects_extra_occurrence(self):
        for case in self.cases:
            with self.subTest(case=case["id"]):
                actual = copy.deepcopy(self.actual)
                actual[case["id"]].append("2099-01-01T00:00:00Z")
                self.assertFalse(kit.compare(self.cases, actual)["passed"])

    def test_duplicate_is_not_silently_deduplicated(self):
        self.actual[self.key].insert(0, self.actual[self.key][0])
        self.assertFalse(kit.compare(self.cases, self.actual)["passed"])

    def test_order_matters(self):
        self.actual[self.key].reverse()
        result = kit.compare(self.cases, self.actual)
        self.assertFalse(result["passed"])
        self.assertTrue(result["cases"][0]["out_of_order"])

    def test_missing_case(self):
        del self.actual[self.key]
        self.assertFalse(kit.compare(self.cases, self.actual)["passed"])

    def test_unknown_case(self):
        self.actual["typo"] = []
        self.assertFalse(kit.compare(self.cases, self.actual)["passed"])

    def test_empty_result(self):
        self.assertFalse(kit.compare(self.cases, {})["passed"])

    def test_timezone_must_be_normalized_by_caller(self):
        self.actual[self.key][0] = "2026-01-31T10:00:00+01:00"
        with self.assertRaises(ValueError):
            kit.compare(self.cases, self.actual)

    def test_invalid_timestamp(self):
        for value in [None, 1, "bad", "2026-02-30T00:00:00Z"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                kit.validate_stamps([value])

    def test_json_duplicate_keys_rejected(self):
        with self.assertRaises(ValueError):
            json.loads('{"a": [], "a": []}', object_pairs_hook=kit.unique_object)

    def test_dst_is_wall_clock_not_fixed_utc(self):
        by_id = {c["id"]: c for c in self.cases}
        self.assertEqual(by_id["new_york_spring"]["expected"], [
            "2026-03-01T14:00:00Z", "2026-03-08T13:00:00Z", "2026-03-15T13:00:00Z"])
        self.assertEqual(by_id["new_york_autumn"]["expected"], [
            "2026-10-25T13:00:00Z", "2026-11-01T14:00:00Z", "2026-11-08T14:00:00Z"])

    def test_exit_codes(self):
        script = str(Path(kit.__file__).resolve())
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "actual.json"
            for content, code in [(json.dumps(self.actual), 0), ('{}', 1), ('{', 2)]:
                output.write_text(content)
                result = subprocess.run([sys.executable, script, 'check', str(output)], capture_output=True)
                self.assertEqual(result.returncode, code)


if __name__ == "__main__":
    unittest.main()
