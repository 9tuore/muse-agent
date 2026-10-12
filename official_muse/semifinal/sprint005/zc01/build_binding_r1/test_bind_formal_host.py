import hashlib
import json
import struct
import tempfile
import unittest
from pathlib import Path

import bind_formal_host as audit


def fixture():
    unsigned = bytearray(4124)
    struct.pack_into("<8I", unsigned, 0, 0xFEEDFACF, 0x01000007, 3, 2, 2, 96, 0, 0)
    struct.pack_into("<II16sQQQQIIII", unsigned, 32, 0x19, 72, b"__LINKEDIT", 0x1000, 4096, 4096, 28, 7, 1, 0, 0)
    struct.pack_into("<II16s", unsigned, 104, 0x1B, 24, bytes(range(16)))
    unsigned[4096:] = b"synthetic public linkedit data"
    # Length remains 4125 after this literal assignment; restore the segment size.
    struct.pack_into("<Q", unsigned, 32 + 48, len(unsigned) - 4096)
    signed = bytearray(unsigned)
    struct.pack_into("<II", signed, 16, 3, 112)
    struct.pack_into("<IIII", signed, 128, 0x1D, 16, len(unsigned), 32)
    signed += b"x" * 32
    struct.pack_into("<Q", signed, 32 + 48, len(signed) - 4096)
    return bytes(unsigned), bytes(signed)


class BindingTests(unittest.TestCase):
    def test_memory_restoration_matches_original_bytes(self):
        unsigned, signed = fixture()
        result = audit.inspect_signed(signed)
        self.assertEqual(result["restored_unsigned_sha256"], hashlib.sha256(unsigned).hexdigest())
        self.assertEqual(result["restored_unsigned_bytes"], len(unsigned))
        self.assertFalse(result["binary_written"])
        self.assertFalse(result["binary_executed"])

    def test_binding_preserves_artifacts_and_rejects_wrong_receipt(self):
        unsigned, signed = fixture()
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent, prefix=".binding-test-") as directory:
            path = Path(directory) / "synthetic-host"
            receipt = Path(directory) / "receipt.json"
            path.write_bytes(signed)
            record = {"host_sha256": hashlib.sha256(unsigned).hexdigest(), "host_bytes": len(unsigned), "exit_code": 0}
            receipt.write_text(json.dumps(record))
            before = (path.read_bytes(), path.stat().st_mtime_ns, receipt.read_bytes())
            self.assertTrue(audit.bind(path, receipt)["exact_build_receipt_match"])
            self.assertEqual(before, (path.read_bytes(), path.stat().st_mtime_ns, receipt.read_bytes()))
            record["host_sha256"] = "0" * 64
            receipt.write_text(json.dumps(record))
            self.assertFalse(audit.bind(path, receipt)["exact_build_receipt_match"])

    def test_rejects_unsupported_or_truncated_transform(self):
        _, signed = fixture()
        for data in [signed[:30], signed[:-1], signed + b"extra"]:
            with self.subTest(length=len(data)), self.assertRaises(ValueError):
                audit.inspect_signed(data)
        changed = bytearray(signed)
        struct.pack_into("<I", changed, 4, 0x0100000C)
        with self.assertRaises(ValueError):
            audit.inspect_signed(changed)


if __name__ == "__main__":
    unittest.main()
