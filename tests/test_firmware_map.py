import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_firmware_map as subject


class FirmwareMapTests(unittest.TestCase):
    def test_synthetic_call_string_reference_and_gap(self):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            image = work / "image.dat"
            listing = work / "listing.txt"
            symbols = work / "symbols.json"
            output = work / "generated"
            data = bytearray(32)
            data[8:14] = b"audio\0"
            image.write_bytes(data)
            listing.write_text(
                "       0:    80 ff 02 00 00 00 \tcall 8 <firmware+0x8 : 8 >\n"
                "       6:    80 00             \trts\n"
                "       8:    c1 ff 28 01 00 02 \tr1 = 33554728 <firmware+0x2000128 : 2000128 >\n",
                encoding="utf-8",
            )
            symbols.write_text(
                json.dumps({"symbols": [{"offset": "0x0", "kind": "function", "name": "entry", "confidence": "verified"}]}),
                encoding="utf-8",
            )
            result = subject.build(image, listing, symbols, output)
            self.assertEqual(result["counts"]["direct_call_sites"], 1)
            self.assertEqual(result["counts"]["function_entries_with_seeds"], 2)
            self.assertEqual(result["counts"]["decoded_bytes"], 14)
            with (output / "functions/functions_000.csv").open(encoding="utf-8") as source:
                rows = list(csv.DictReader(source))
            self.assertEqual(rows[0]["callees"], "0x02000128")
            self.assertEqual(rows[1]["string_refs"], "0x02000128")
            with (output / "gaps/gaps_000.csv").open(encoding="utf-8") as source:
                gaps = list(csv.DictReader(source))
            self.assertEqual(gaps, [{"start_offset": "0xE", "end_offset": "0x20", "length": "18"}])


if __name__ == "__main__":
    unittest.main()
