import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from match_toolchain_libs import canonical


class ToolchainMatchingTests(unittest.TestCase):
    def test_operands_and_annotations_are_normalized(self):
        first = canonical("call 176 <firmware+0xC6 : c6 >")
        second = canonical("call -24 <symbol+0x20 : 20 >")
        self.assertEqual(first, "call #")
        self.assertEqual(second, "call #")

    def test_registers_and_opcode_remain_significant(self):
        self.assertNotEqual(canonical("r1 = r2 + 4"), canonical("r3 = r2 + 4"))
        self.assertNotEqual(canonical("r1 = r2 + 4"), canonical("r1 = r2 - 4"))


if __name__ == "__main__":
    unittest.main()
