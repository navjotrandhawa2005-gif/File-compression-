"""
Comprehensive Unit & Integration Test Suite for DAA File Compression Tool.

Tests edge cases, correctness, and lossless roundtrips for:
- Huffman Coding (Greedy min-heap)
- Run-Length Encoding (PackBits)
- LZW Compression (Adaptive dictionary)
- Binary container packing and cryptographic SHA-256 integrity validation
"""

import unittest
import os
import tempfile
import random
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from algorithms.huffman import HuffmanCompressor
from algorithms.rle import RLECompressor
from algorithms.lzw import LZWCompressor
from utils.file_io import ContainerFile, verify_files_identical, compute_sha256


class BaseCompressionTestCase(unittest.TestCase):
    def _test_roundtrip_bytes(self, compressor, data: bytes):
        """Helper to test in-memory roundtrip."""
        meta, payload = compressor.compress(data)
        restored = compressor.decompress(meta, payload, original_size=len(data))
        self.assertEqual(data, restored, f"{compressor.name} failed in-memory roundtrip!")

    def _test_roundtrip_file(self, compressor, raw_bytes: bytes):
        """Helper to test containerized file-level roundtrip with SHA-256 verification."""
        with tempfile.TemporaryDirectory() as temp_dir:
            orig_path = os.path.join(temp_dir, "orig.bin")
            comp_path = os.path.join(temp_dir, "archive.daac")
            rest_path = os.path.join(temp_dir, "restored.bin")

            with open(orig_path, "wb") as f:
                f.write(raw_bytes)

            stats = compressor.compress_file(orig_path, comp_path)
            d_stats = compressor.decompress_file(comp_path, rest_path, original_for_verify=orig_path)

            self.assertTrue(d_stats.is_verified, f"{compressor.name} file verification failed!")
            self.assertEqual(os.path.getsize(orig_path), os.path.getsize(rest_path))
            
            with open(rest_path, "rb") as f:
                restored_bytes = f.read()
            self.assertEqual(raw_bytes, restored_bytes)


class TestHuffmanCoding(BaseCompressionTestCase):
    def setUp(self):
        self.compressor = HuffmanCompressor()

    def test_empty_data(self):
        self._test_roundtrip_bytes(self.compressor, b"")
        self._test_roundtrip_file(self.compressor, b"")

    def test_single_character(self):
        self._test_roundtrip_bytes(self.compressor, b"A")
        self._test_roundtrip_file(self.compressor, b"A")

    def test_all_same_characters(self):
        data = b"X" * 5000
        self._test_roundtrip_bytes(self.compressor, data)
        self._test_roundtrip_file(self.compressor, data)

    def test_natural_text(self):
        text = b"The quick brown fox jumps over the lazy dog. Lossless compression algorithms are fascinating!" * 20
        self._test_roundtrip_bytes(self.compressor, text)
        self._test_roundtrip_file(self.compressor, text)

    def test_all_byte_values(self):
        # All 256 byte values present
        data = bytes(range(256)) * 4
        self._test_roundtrip_bytes(self.compressor, data)
        self._test_roundtrip_file(self.compressor, data)


class TestRunLengthEncoding(BaseCompressionTestCase):
    def setUp(self):
        self.compressor = RLECompressor()

    def test_empty_data(self):
        self._test_roundtrip_bytes(self.compressor, b"")
        self._test_roundtrip_file(self.compressor, b"")

    def test_single_character(self):
        self._test_roundtrip_bytes(self.compressor, b"Z")
        self._test_roundtrip_file(self.compressor, b"Z")

    def test_repeating_runs(self):
        # Long runs exceeding 128 bytes to test PackBits chunk splitting
        data = b"A" * 300 + b"B" * 50 + b"C" * 256
        self._test_roundtrip_bytes(self.compressor, data)
        self._test_roundtrip_file(self.compressor, data)

    def test_literal_runs(self):
        # Non-repeating bytes
        data = bytes(range(256))
        self._test_roundtrip_bytes(self.compressor, data)
        self._test_roundtrip_file(self.compressor, data)


class TestLZWCompression(BaseCompressionTestCase):
    def setUp(self):
        self.compressor = LZWCompressor()

    def test_empty_data(self):
        self._test_roundtrip_bytes(self.compressor, b"")
        self._test_roundtrip_file(self.compressor, b"")

    def test_single_character(self):
        self._test_roundtrip_bytes(self.compressor, b"M")
        self._test_roundtrip_file(self.compressor, b"M")

    def test_classic_kwkwk_edge_case(self):
        # cScSc pattern that triggers decoderKwKwK lookup
        data = b"ABABABABABABABABABABABABABABABABABABAB"
        self._test_roundtrip_bytes(self.compressor, data)
        self._test_roundtrip_file(self.compressor, data)

    def test_repetitive_phrases(self):
        data = b"TOBEORNOTTOBETHATISTHEQUESTION" * 15
        self._test_roundtrip_bytes(self.compressor, data)
        self._test_roundtrip_file(self.compressor, data)

    def test_large_random_stream(self):
        rng = random.Random(999)
        data = bytes([rng.randint(0, 255) for _ in range(5000)])
        self._test_roundtrip_bytes(self.compressor, data)
        self._test_roundtrip_file(self.compressor, data)


class TestContainerAndIntegrity(unittest.TestCase):
    def test_invalid_magic_header(self):
        corrupt = b"BADH" + b"\x01" + b"\x00" * 60
        with self.assertRaises(ValueError):
            ContainerFile.unpack(corrupt)

    def test_checksum_computation(self):
        data = b"Lossless file verification"
        digest = compute_sha256(data)
        self.assertEqual(len(digest), 32)


if __name__ == "__main__":
    unittest.main()
