"""
Abstract Base Class for Compression Algorithms.

Defines the standard interface that all algorithms (Huffman, RLE, LZW)
must implement, alongside unified file container handling and performance metrics.
"""

from abc import ABC, abstractmethod
import os
import time
from typing import Tuple, NamedTuple
from utils.file_io import ContainerFile, compute_sha256, verify_files_identical


class CompressionStats(NamedTuple):
    algorithm: str
    original_size: int
    compressed_size: int
    compression_ratio: float  # original / compressed
    space_savings: float      # (1 - compressed / original) * 100
    compression_time: float   # seconds
    sha256_hex: str


class DecompressionStats(NamedTuple):
    algorithm: str
    compressed_size: int
    decompressed_size: int
    decompression_time: float # seconds
    sha256_hex: str
    is_verified: bool
    verification_message: str


class BaseCompressor(ABC):
    """
    Abstract base class for all lossless file compression algorithms.
    """

    def __init__(self, name: str, algorithm_id: int):
        self.name = name
        self.algorithm_id = algorithm_id

    @abstractmethod
    def compress(self, data: bytes) -> Tuple[bytes, bytes]:
        """
        Compress raw byte data.
        
        Args:
            data: Raw input bytes.
            
        Returns:
            Tuple of (metadata: bytes, compressed_payload: bytes).
        """
        pass

    @abstractmethod
    def decompress(self, metadata: bytes, compressed_payload: bytes, original_size: int) -> bytes:
        """
        Decompress payload back to exact original bytes.
        
        Args:
            metadata: Metadata stored in file header (e.g., frequency table).
            compressed_payload: Encoded compressed bytes.
            original_size: Expected exact size in bytes.
            
        Returns:
            Decompressed bytes.
        """
        pass

    def compress_file(self, input_path: str, output_path: str) -> CompressionStats:
        """
        Reads input file, compresses it, and writes the standardized self-contained container.
        """
        with open(input_path, "rb") as f:
            raw_data = f.read()

        orig_size = len(raw_data)
        sha256_raw = compute_sha256(raw_data)

        start_time = time.perf_counter()
        metadata, compressed_payload = self.compress(raw_data)
        container_bytes = ContainerFile.pack(
            algorithm_id=self.algorithm_id,
            original_size=orig_size,
            sha256_hash=sha256_raw,
            metadata=metadata,
            compressed_payload=compressed_payload,
        )
        comp_time = time.perf_counter() - start_time

        with open(output_path, "wb") as f:
            f.write(container_bytes)

        comp_size = len(container_bytes)
        ratio = (orig_size / comp_size) if comp_size > 0 else 0.0
        savings = ((1.0 - (comp_size / orig_size)) * 100.0) if orig_size > 0 else 0.0

        return CompressionStats(
            algorithm=self.name,
            original_size=orig_size,
            compressed_size=comp_size,
            compression_ratio=ratio,
            space_savings=savings,
            compression_time=comp_time,
            sha256_hex=sha256_raw.hex(),
        )

    def decompress_file(self, input_path: str, output_path: str, original_for_verify: str = None) -> DecompressionStats:
        """
        Reads container file, validates header & metadata, decompresses,
        and optionally verifies byte-for-byte against the original file.
        """
        with open(input_path, "rb") as f:
            container_bytes = f.read()

        header, metadata, compressed_payload = ContainerFile.unpack(container_bytes)
        
        if header.algorithm_id != self.algorithm_id:
            raise ValueError(
                f"Algorithm mismatch: File was compressed with algorithm #{header.algorithm_id}, "
                f"but {self.name} (#{self.algorithm_id}) was selected."
            )

        start_time = time.perf_counter()
        decompressed_data = self.decompress(metadata, compressed_payload, header.original_size)
        decomp_time = time.perf_counter() - start_time

        # Verify against expected original size
        if len(decompressed_data) != header.original_size:
            raise ValueError(
                f"Decompression size mismatch: Expected {header.original_size:,} bytes, "
                f"got {len(decompressed_data):,} bytes"
            )

        # Verify SHA-256 integrity
        decomp_sha = compute_sha256(decompressed_data)
        if decomp_sha != header.sha256_hash:
            raise ValueError(
                f"Integrity check failed! SHA-256 digest does not match archive header."
            )

        with open(output_path, "wb") as f:
            f.write(decompressed_data)

        # Full disk verification if original is provided
        is_verified = True
        verify_msg = f"Integrity Verified (SHA-256: {decomp_sha.hex()[:16]}...)"
        if original_for_verify and os.path.exists(original_for_verify):
            is_identical, detail = verify_files_identical(original_for_verify, output_path)
            is_verified = is_identical
            verify_msg = detail

        return DecompressionStats(
            algorithm=self.name,
            compressed_size=len(container_bytes),
            decompressed_size=len(decompressed_data),
            decompression_time=decomp_time,
            sha256_hex=decomp_sha.hex(),
            is_verified=is_verified,
            verification_message=verify_msg,
        )
