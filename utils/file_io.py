"""
File I/O and binary container management for the DAA File Compression Tool.

Handles:
- Structured binary headers: Magic bytes ('DAAC'), version, algorithm ID,
  original file size (uint64), SHA-256 digest (32 bytes), metadata length (uint32).
- Metadata persistence (frequency table, dictionary settings, etc.).
- Complete verification of lossless reconstruction via cryptographic SHA-256 hashes
  and byte-by-byte comparison.
"""

import hashlib
import os
import struct
from typing import Tuple, NamedTuple, Optional

# Magic bytes identifier: "DAAC" (DAA Compressor)
MAGIC_HEADER = b"DAAC"
FORMAT_VERSION = 1

# Algorithm ID constants
ALGO_HUFFMAN = 1
ALGO_RLE = 2
ALGO_LZW = 3

ALGO_NAMES = {
    ALGO_HUFFMAN: "Huffman Coding",
    ALGO_RLE: "Run-Length Encoding (RLE)",
    ALGO_LZW: "LZW Compression",
}

# Header layout format:
# 4 bytes: Magic ("DAAC")
# 1 byte:  Version (0x01)
# 1 byte:  Algorithm ID (1, 2, 3)
# 8 bytes: Original file size (uint64, big-endian)
# 32 bytes: Original SHA-256 hash
# 4 bytes: Metadata length (uint32, big-endian)
# Total fixed header size = 4 + 1 + 1 + 8 + 32 + 4 = 50 bytes
HEADER_FIXED_FORMAT = ">4sBBQ32sI"
HEADER_FIXED_SIZE = struct.calcsize(HEADER_FIXED_FORMAT)


class ContainerHeader(NamedTuple):
    version: int
    algorithm_id: int
    original_size: int
    sha256_hash: bytes
    meta_length: int


class ContainerFile:
    """Manages packing and unpacking of self-contained compressed files."""

    @staticmethod
    def pack(
        algorithm_id: int,
        original_size: int,
        sha256_hash: bytes,
        metadata: bytes,
        compressed_payload: bytes,
    ) -> bytes:
        """
        Packs compressed data into a standardized binary container.
        """
        if len(sha256_hash) != 32:
            raise ValueError(f"SHA-256 hash must be exactly 32 bytes, got {len(sha256_hash)}")

        header_bytes = struct.pack(
            HEADER_FIXED_FORMAT,
            MAGIC_HEADER,
            FORMAT_VERSION,
            algorithm_id,
            original_size,
            sha256_hash,
            len(metadata),
        )

        return header_bytes + metadata + compressed_payload

    @staticmethod
    def unpack(data: bytes) -> Tuple[ContainerHeader, bytes, bytes]:
        """
        Unpacks a binary container into (header, metadata, compressed_payload).
        
        Raises:
            ValueError: If magic bytes mismatch or data is corrupt/truncated.
        """
        if len(data) < HEADER_FIXED_SIZE:
            raise ValueError(
                f"File too small to be a valid DAAC archive ({len(data)} bytes, expected at least {HEADER_FIXED_SIZE})"
            )

        magic, version, algo_id, orig_size, sha256_hash, meta_len = struct.unpack(
            HEADER_FIXED_FORMAT, data[:HEADER_FIXED_SIZE]
        )

        if magic != MAGIC_HEADER:
            raise ValueError(
                f"Invalid file format: Magic bytes mismatch (got {magic!r}, expected {MAGIC_HEADER!r})"
            )

        if version != FORMAT_VERSION:
            raise ValueError(f"Unsupported format version {version} (expected {FORMAT_VERSION})")

        if algo_id not in ALGO_NAMES:
            raise ValueError(f"Unknown algorithm ID: {algo_id}")

        meta_start = HEADER_FIXED_SIZE
        meta_end = meta_start + meta_len

        if len(data) < meta_end:
            raise ValueError("Corrupt file: Archive truncated inside metadata section")

        metadata = data[meta_start:meta_end]
        compressed_payload = data[meta_end:]

        header = ContainerHeader(
            version=version,
            algorithm_id=algo_id,
            original_size=orig_size,
            sha256_hash=sha256_hash,
            meta_length=meta_len,
        )

        return header, metadata, compressed_payload


def compute_sha256(data: bytes) -> bytes:
    """Computes raw 32-byte SHA-256 digest of byte data."""
    return hashlib.sha256(data).digest()


def compute_file_sha256(file_path: str) -> str:
    """Computes hex digest of a file on disk."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_files_identical(file1_path: str, file2_path: str) -> Tuple[bool, str]:
    """
    Performs byte-by-byte and cryptographic SHA-256 verification of two files.
    Returns (is_identical: bool, message: str).
    """
    if not os.path.exists(file1_path):
        return False, f"File does not exist: {file1_path}"
    if not os.path.exists(file2_path):
        return False, f"File does not exist: {file2_path}"

    size1 = os.path.getsize(file1_path)
    size2 = os.path.getsize(file2_path)

    if size1 != size2:
        return False, f"Size mismatch: original={size1:,} bytes vs decompressed={size2:,} bytes"

    hash1 = hashlib.sha256()
    hash2 = hashlib.sha256()

    with open(file1_path, "rb") as f1, open(file2_path, "rb") as f2:
        while True:
            b1 = f1.read(65536)
            b2 = f2.read(65536)
            if b1 != b2:
                return False, "Byte difference detected between original and decompressed data!"
            if not b1:
                break
            hash1.update(b1)
            hash2.update(b2)

    digest1 = hash1.hexdigest()
    digest2 = hash2.hexdigest()

    if digest1 == digest2:
        return True, f"Verified 100% identical! SHA-256: {digest1}"
    else:
        return False, f"Hash mismatch: {digest1} != {digest2}"
