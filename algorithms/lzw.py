"""
Lempel-Ziv-Welch (LZW) Compression Algorithm (DAA Project).

Algorithmic Paradigm: Adaptive Dictionary-Based Substitution
Data Structures: Hash Table (Compression) / Direct Indexed Array (Decompression)

DESIGN AND ANALYSIS OF ALGORITHMS (DAA) THEORETICAL PRINCIPLES:
===============================================================
1. ADAPTIVE DICTIONARY CONSTRUCTION:
   Unlike static Huffman coding (which requires a pre-pass to calculate frequencies
   and explicitly stores the tree/table in the file), LZW dynamically builds its
   dictionary online during both compression and decompression.
   Neither the encoder nor decoder needs to transmit the dictionary: the decoder
   reconstructs the exact identical dictionary on-the-fly from the sequence of code tokens!

2. VARIABLE BIT-WIDTH ENCODING:
   - Initial alphabet size: 256 (single bytes 0x00 to 0xFF).
   - Control Codes:
     * CLEAR_CODE = 256 (resets dictionary when table fills up, adapting to phase shifts).
     * END_OF_STREAM = 257 (marks completion).
   - Dictionary entries start from index 258.
   - Code width starts at 9 bits (capable of 0..511).
   - When dictionary entries reach 2^current_width, bit width dynamically expands
     (9 -> 10 -> 11 -> 12 -> ... up to MAX_BITS = 16 bits, capacity 65,536 entries).

3. THE CLASSIC LZW EDGE CASE ("KwKwK" / cScSc):
   Occurs when the encoder encounters a string already in the table, finds that appending
   the next character creates a new string (say code K), emits the previous code, and in
   the very next step outputs code K before the decoder has even defined K!
   The decoder detects this condition whenever: code == next_available_code.
   The decoded string is mathematically guaranteed to be:
       decoded = previous_string + previous_string[0]

COMPLEXITY ANALYSIS:
====================
- Time Complexity:
  * Compression:
    - Best Case: O(N) where long repeated phrases match multi-byte dictionary entries.
    - Average Case: O(N) using amortized O(1) hash map lookups per byte.
    - Worst Case: O(N) linear scan through input bytes.
  * Decompression:
    - O(N) linear array lookups for each received bit-token.

- Space Complexity:
  * Dictionary Memory: O(D) where D is MAX_DICT_SIZE = 2^16 = 65,536 entries.
    Since D is bounded by a constant, auxiliary space is strictly O(1) in DAA terms!
  * Encoded Output: O(N) bits.
"""

from typing import Tuple, List, Dict
from algorithms.base import BaseCompressor
from utils.file_io import ALGO_LZW
from utils.bit_stream import BitWriter, BitReader


INIT_BITS = 9
MAX_BITS = 16
MAX_DICT_SIZE = 1 << MAX_BITS  # 65,536 entries
CLEAR_CODE = 256
END_OF_STREAM = 257
FIRST_AVAIL_CODE = 258


class LZWCompressor(BaseCompressor):
    """
    Byte-level Lempel-Ziv-Welch (LZW) compressor with variable bit-width (9-16 bits)
    and automatic dictionary reset via CLEAR_CODE.
    """

    def __init__(self):
        super().__init__(name="LZW Compression", algorithm_id=ALGO_LZW)

    def compress(self, data: bytes) -> Tuple[bytes, bytes]:
        """
        Compresses input bytes using variable-width LZW.
        
        Returns:
            Tuple of (metadata: bytes, compressed_payload: bytes).
        """
        if not data:
            return b"", b""

        writer = BitWriter()
        
        # Initialize dictionary with 256 single-byte entries
        dictionary: Dict[bytes, int] = {bytes([i]): i for i in range(256)}
        next_code = FIRST_AVAIL_CODE
        current_bits = INIT_BITS

        # Emit initial CLEAR_CODE
        writer.write_bits(CLEAR_CODE, current_bits)

        current_phrase = bytes([data[0]])

        for byte_val in data[1:]:
            next_phrase = current_phrase + bytes([byte_val])
            if next_phrase in dictionary:
                current_phrase = next_phrase
            else:
                # Output code for current_phrase
                writer.write_bits(dictionary[current_phrase], current_bits)

                # Add next_phrase to dictionary if space permits
                if next_code < MAX_DICT_SIZE:
                    dictionary[next_phrase] = next_code
                    next_code += 1

                    # Check if bit width needs expansion
                    if next_code == (1 << current_bits) and current_bits < MAX_BITS:
                        current_bits += 1
                else:
                    # Dictionary is full: emit CLEAR_CODE and reset
                    writer.write_bits(CLEAR_CODE, current_bits)
                    dictionary = {bytes([i]): i for i in range(256)}
                    next_code = FIRST_AVAIL_CODE
                    current_bits = INIT_BITS

                current_phrase = bytes([byte_val])

        # Output the remaining phrase
        if current_phrase:
            writer.write_bits(dictionary[current_phrase], current_bits)

        # Emit END_OF_STREAM
        writer.write_bits(END_OF_STREAM, current_bits)

        return b"", writer.flush()

    def decompress(self, metadata: bytes, compressed_payload: bytes, original_size: int) -> bytes:
        """
        Decompresses variable-width LZW payload back to exact original bytes.
        """
        if original_size == 0 or not compressed_payload:
            return b""

        reader = BitReader(compressed_payload)
        output = bytearray()

        def _init_dictionary() -> List[bytes]:
            # Array lookup for O(1) decompression speed
            table = [bytes([i]) for i in range(256)]
            table.append(b"")  # CLEAR_CODE (256)
            table.append(b"")  # END_OF_STREAM (257)
            return table

        dictionary = _init_dictionary()
        current_bits = INIT_BITS
        previous_phrase = b""

        while len(output) < original_size and reader.has_more():
            try:
                code = reader.read_bits(current_bits)
            except EOFError:
                break

            if code == END_OF_STREAM:
                break

            if code == CLEAR_CODE:
                dictionary = _init_dictionary()
                current_bits = INIT_BITS
                previous_phrase = b""
                continue

            if code < len(dictionary):
                phrase = dictionary[code]
            elif code == len(dictionary) and previous_phrase:
                # THE CLASSIC LZW KwKwK / cScSc EDGE CASE:
                # The code was just added by the encoder in this turn.
                phrase = previous_phrase + bytes([previous_phrase[0]])
            else:
                raise ValueError(f"Corrupt LZW bitstream: invalid code {code} (dict size {len(dictionary)})")

            output.extend(phrase)

            if previous_phrase and len(dictionary) < MAX_DICT_SIZE:
                new_entry = previous_phrase + bytes([phrase[0]])
                dictionary.append(new_entry)

                # Check if bit width should expand:
                # Since decoder dictionary addition lags by 1 step relative to encoder,
                # bit width expands when len(dictionary) + 1 >= (1 << current_bits).
                if len(dictionary) + 1 >= (1 << current_bits) and current_bits < MAX_BITS:
                    current_bits += 1

            previous_phrase = phrase

        if len(output) != original_size:
            raise ValueError(
                f"LZW decompression size mismatch: expected {original_size} bytes, got {len(output)} bytes"
            )

        return bytes(output)
