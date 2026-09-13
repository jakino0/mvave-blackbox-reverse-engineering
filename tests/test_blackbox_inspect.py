import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import blackbox_inspect as subject


class InspectorTests(unittest.TestCase):
    def test_address_translation_round_trip(self):
        offset = 0x5BC1A
        runtime = subject.app_to_runtime(offset)
        self.assertEqual(runtime, 0x0205BD3A)
        self.assertEqual(runtime - subject.RUNTIME_BASE, offset)

    def test_find_all_includes_overlaps(self):
        self.assertEqual(subject.find_all(b"aaaa", b"aa"), [0, 1, 2])

    def test_decode_isochronous_endpoint(self):
        prefix = b"\x00" * 7
        descriptor = bytes.fromhex("09 05 83 05 20 01 01 00 00")
        endpoints = subject.decode_uac_endpoints(prefix + descriptor)
        self.assertEqual(len(endpoints), 1)
        self.assertEqual(endpoints[0]["offset"], 7)
        self.assertEqual(endpoints[0]["address"], 0x83)
        self.assertEqual(endpoints[0]["direction"], "IN")
        self.assertEqual(endpoints[0]["max_packet_size"], 0x0120)

    def test_rejects_reserved_endpoint_address_bits(self):
        false_positive = bytes.fromhex("09 05 62 05 4a c2 ff ff ff")
        self.assertEqual(subject.decode_uac_endpoints(false_positive), [])

    def test_sha256(self):
        self.assertEqual(subject.sha256(b"abc"), hashlib.sha256(b"abc").hexdigest())


if __name__ == "__main__":
    unittest.main()
