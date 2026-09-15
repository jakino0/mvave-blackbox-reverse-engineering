import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "analysis/v20/generated"


class CheckedInMapTests(unittest.TestCase):
    def test_manifest_baseline(self):
        manifest = json.loads((MAP / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["input"]["size"], 655712)
        self.assertEqual(manifest["input"]["runtime_base"], "0x02000120")
        self.assertEqual(manifest["counts"]["recognized_instructions"], 222490)
        self.assertEqual(manifest["counts"]["function_entries_with_seeds"], 2167)
        self.assertEqual(manifest["counts"]["direct_call_sites"], 12152)
        self.assertAlmostEqual(manifest["counts"]["decoded_byte_coverage_percent"], 94.2426)

    def test_corrected_audio_dev_boundary(self):
        landmarks = json.loads((MAP / "landmarks.json").read_text(encoding="utf-8"))["symbols"]
        by_name = {item["name"]: item for item in landmarks}
        item = by_name["audio_dev_string_load"]
        self.assertEqual(item["offset"], "0x43328")
        self.assertEqual(item["runtime"], "0x02043448")
        self.assertIn("inside the instruction", item["note"])

    def test_exact_toolchain_symbols_are_unique(self):
        with (MAP / "library-symbols.csv").open(encoding="utf-8", newline="") as source:
            rows = list(csv.DictReader(source))
        self.assertEqual(len(rows), 16)
        self.assertEqual(len({row["address"] for row in rows}), 16)
        self.assertIn("memcmp", {row["name"] for row in rows})
        self.assertIn("__muldf3", {row["name"] for row in rows})
        self.assertTrue(all(row["confidence"] == "exact-toolchain-match" for row in rows))


if __name__ == "__main__":
    unittest.main()
