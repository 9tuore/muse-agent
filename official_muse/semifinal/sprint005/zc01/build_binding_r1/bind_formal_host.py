#!/usr/bin/env python3
"""Bind a signed Intel Mach-O to an unsigned build receipt, without writes.

Only the observed standalone signing transform is supported: a final
LC_CODE_SIGNATURE, trailing signature blob, and expanded __LINKEDIT.
Restored bytes exist in memory only. No binary/signature is written or run.
"""
import argparse
import hashlib
import json
import stat
import struct
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inspect_signed(data):
    if len(data) < 32:
        raise ValueError("truncated Mach-O")
    magic, cpu, _, _, count, command_bytes, _, _ = struct.unpack_from("<8I", data)
    if magic != 0xFEEDFACF or cpu != 0x01000007:
        raise ValueError("expected thin little-endian Intel Mach-O 64")
    if command_bytes > len(data) - 32 or count > 4096:
        raise ValueError("invalid load-command bounds")
    pos, signatures, linkedits, sections, uuid = 32, [], [], [], None
    for _ in range(count):
        if pos + 8 > 32 + command_bytes:
            raise ValueError("truncated command")
        command, length = struct.unpack_from("<II", data, pos)
        if length < 8 or pos + length > 32 + command_bytes:
            raise ValueError("invalid command length")
        if command == 0x1D:
            if length != 16:
                raise ValueError("unsupported signature command")
            signatures.append((pos, *struct.unpack_from("<II", data, pos + 8)))
        if command == 0x1B:
            if length != 24:
                raise ValueError("invalid UUID command")
            uuid = data[pos + 8:pos + 24].hex()
        if command == 0x19:
            if length < 72:
                raise ValueError("truncated segment")
            name = data[pos + 8:pos + 24].split(b"\0")[0].decode("ascii")
            section_count = struct.unpack_from("<I", data, pos + 64)[0]
            if 72 + section_count * 80 != length:
                raise ValueError("invalid section table")
            if name == "__LINKEDIT":
                linkedits.append(pos)
            for number in range(section_count):
                at = pos + 72 + number * 80
                section_name = data[at:at + 16].split(b"\0")[0].decode("ascii")
                segment_name = data[at + 16:at + 32].split(b"\0")[0].decode("ascii")
                size, offset = struct.unpack_from("<QI", data, at + 40)
                kind = struct.unpack_from("<I", data, at + 64)[0] & 0xFF
                if kind not in (1, 12, 18) and size:
                    if not offset or offset + size > len(data):
                        raise ValueError("section outside file")
                    sections.append({"segment": segment_name, "section": section_name,
                                     "bytes": size, "sha256": digest(data[offset:offset + size])})
        pos += length
    if pos != 32 + command_bytes or len(signatures) != 1 or len(linkedits) != 1:
        raise ValueError("expected one signature and one __LINKEDIT")
    signature_at, offset, size = signatures[0]
    if signature_at + 16 != pos or offset + size != len(data) or offset < pos or not size:
        raise ValueError("unsupported signing transform")
    linkedit = linkedits[0]
    fileoff = struct.unpack_from("<Q", data, linkedit + 40)[0]
    if fileoff > offset:
        raise ValueError("invalid __LINKEDIT offset")
    unsigned = bytearray(data[:offset])
    unsigned[signature_at:signature_at + 16] = bytes(16)
    struct.pack_into("<II", unsigned, 16, count - 1, command_bytes - 16)
    filesize = offset - fileoff
    struct.pack_into("<Q", unsigned, linkedit + 32, (filesize + 4095) & ~4095)
    struct.pack_into("<Q", unsigned, linkedit + 48, filesize)
    return {"signed_sha256": digest(data), "signed_bytes": len(data), "cpu": "x86_64",
            "uuid_hex": uuid, "signature_offset": offset, "signature_bytes": size,
            "restored_unsigned_sha256": digest(unsigned), "restored_unsigned_bytes": len(unsigned),
            "restoration": "remove final LC_CODE_SIGNATURE; zero its former padding; truncate signature; restore 4KiB-rounded LINKEDIT vmsize/filesize",
            "sections": sections, "input_modified": False, "binary_written": False, "binary_executed": False}


def bind(binary, receipt_path):
    if binary.is_symlink() or not stat.S_ISREG(binary.stat().st_mode):
        raise ValueError("binary must be a regular public artifact")
    data = binary.read_bytes()
    receipt_data = receipt_path.read_bytes()
    receipt = json.loads(receipt_data)
    result = inspect_signed(data)
    matched = receipt.get("exit_code") == 0 and result["restored_unsigned_sha256"] == receipt.get("host_sha256") and result["restored_unsigned_bytes"] == receipt.get("host_bytes")
    result.update(receipt_sha256=digest(receipt_data),
                  expected_unsigned_sha256=receipt.get("host_sha256"),
                  exact_build_receipt_match=matched,
                  status="BINARY_TO_BUILD_RECEIPT_BOUND" if matched else "BUILD_RECEIPT_MISMATCH",
                  full_source_reproduction_proven=False, runtime_proven=False)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = bind(args.binary, args.receipt)
    except (ValueError, OSError, struct.error) as error:
        print(json.dumps({"status": "AUDIT_REFUSED", "reason": str(error)}))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["exact_build_receipt_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
