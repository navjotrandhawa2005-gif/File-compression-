"""
Run-Length Encoding (RLE) Algorithm Implementation (DAA Project).

Algorithmic Paradigm: Linear Scan / Run-Length Grouping (PackBits Specification)
Data Structure: Sequential Buffer Scan

DESIGN AND ANALYSIS OF ALGORITHMS (DAA) THEORETICAL PRINCIPLES:
===============================================================
1. CORE STRATEGY:
   RLE exploits spatial locality and high redundancy by replacing contiguous runs of
   identical symbols with a single frequency count and the symbol.

2. BINARY PACKBITS SPECIFICATION:
   Naive byte-level RLE (storing count + byte for every run) causes catastrophic 200%
   expansion on non-repeating data (e.g., 'ABC' -> '1A 1B 1C').
   To work flawlessly on any binary file, we implement the PackBits standard
   (used in TIFF, PDF RunLengthDecode, and Apple QuickDraw):
     - Signed control byte N (-128 to +127):
       * 0 <= N <= 127: LITERAL RUN. Copy the following (N + 1) literal bytes verbatim.
         Overhead on completely non-repeating data is only 1 byte per 128 bytes (< 1%).
       * -127 <= N <= -1: REPEATED RUN. Replicate the next 1 byte (-N + 1) times (2 to 128 times).
         Compresses 128 identical bytes down to just 2 bytes (64x compression ratio!).
       * N = -128 (0x80): No-op / padding marker.

COMPLEXITY ANALYSIS:
====================
- Time Complexity:
  * Compression:
    - Best Case: O(N) when data consists of large repeating runs. (N/128 iterations).
    - Average Case: O(N) single-pass scan with run-length counter.
    - Worst Case: O(N) when data has no consecutive repeating bytes.
    - Overall Time: O(N) strictly linear.
  * Decompression:
    - O(N) strictly linear single-pass decoding into output buffer.

- Space Complexity:
  * Best Case: O(N / 128) -> O(1) for repeated patterns.
  * Worst Case: N + ceil(N / 128) bytes -> O(N) (at most 0.78% expansion).
  * Auxiliary Space: O(1) auxiliary variables beyond I/O buffers.
"""

from typing import Tuple
from algorithms.base import BaseCompressor
from utils.file_io import ALGO_RLE


class RLECompressor(BaseCompressor):
    """
    Byte-level Run-Length Encoder using the robust PackBits algorithm.
    """

    def __init__(self):
        super().__init__(name="Run-Length Encoding (RLE)", algorithm_id=ALGO_RLE)

    def compress(self, data: bytes) -> Tuple[bytes, bytes]:
        """
        Compresses arbitrary byte sequences using PackBits RLE.
        
        Returns:
            Tuple of (metadata: bytes, compressed_payload: bytes).
            Metadata is empty (b"") as PackBits is self-contained.
        """
        if not data:
            return b"", b""

        output = bytearray()
        i = 0
        n = len(data)

        while i < n:
            # Check for a repeated run of identical bytes
            run_length = 1
            while (i + run_length < n) and (data[i + run_length] == data[i]) and (run_length < 128):
                run_length += 1

            if run_length >= 2:
                # Repeated run detected: emit control byte (- (run_length - 1)) as signed 8-bit
                # In Python bytearray: (- (run_length - 1)) & 0xFF
                control_byte = (-(run_length - 1)) & 0xFF
                output.append(control_byte)
                output.append(data[i])
                i += run_length
            else:
                # Literal run: find sequence of non-repeating bytes (or isolated runs of 1)
                lit_start = i
                lit_length = 0
                while i < n and lit_length < 128:
                    # Look ahead: if next 3 bytes are identical, stop literal run here
                    if (i + 2 < n) and (data[i] == data[i + 1] == data[i + 2]):
                        break
                    lit_length += 1
                    i += 1

                # Emit control byte (lit_length - 1) followed by literal bytes
                output.append(lit_length - 1)
                output.extend(data[lit_start:lit_start + lit_length])

        return b"", bytes(output)

    def decompress(self, metadata: bytes, compressed_payload: bytes, original_size: int) -> bytes:
        """
        Decompresses PackBits RLE stream back into exact original bytes.
        """
        if original_size == 0 or not compressed_payload:
            return b""

        output = bytearray()
        idx = 0
        payload_len = len(compressed_payload)

        while idx < payload_len and len(output) < original_size:
            header_byte = compressed_payload[idx]
            idx += 1

            # Convert unsigned byte to signed 8-bit integer (-128 to 127)
            if header_byte > 127:
                n = header_byte - 256
            else:
                n = header_byte

            if 0 <= n <= 127:
                # Literal run: copy (n + 1) literal bytes
                count = n + 1
                if idx + count > payload_len:
                    raise ValueError("Corrupt RLE stream: literal run exceeds payload size")
                output.extend(compressed_payload[idx:idx + count])
                idx += count
            elif -127 <= n <= -1:
                # Repeated run: repeat next byte (-n + 1) times
                count = -n + 1
                if idx >= payload_len:
                    raise ValueError("Corrupt RLE stream: repeated run missing value byte")
                repeat_byte = compressed_payload[idx]
                idx += 1
                output.extend(bytes([repeat_byte]) * count)
            elif n == -128:
                # 0x80 is no-op / skip
                continue

        if len(output) != original_size:
            raise ValueError(
                f"RLE decompression size mismatch: expected {original_size} bytes, got {len(output)} bytes"
            )

        return bytes(output)
