"""
BitStream utilities for bit-level reading and writing.

Provides BitWriter (accumulates bits into bytes) and BitReader (extracts
individual or multi-bit words from byte sequences). Crucial for prefix-free
codes like Huffman and variable-width dictionary codes like LZW.
"""


class BitWriter:
    """
    Accumulates bits and produces a bytearray.
    
    Bits are packed into bytes from Most Significant Bit (MSB) to
    Least Significant Bit (LSB).
    """

    def __init__(self):
        self.buffer = bytearray()
        self.current_byte = 0
        self.bit_count = 0  # Number of bits accumulated in current_byte (0 to 7)

    def write_bit(self, bit: int) -> None:
        """Write a single bit (0 or 1)."""
        self.current_byte = (self.current_byte << 1) | (bit & 1)
        self.bit_count += 1
        if self.bit_count == 8:
            self.buffer.append(self.current_byte)
            self.current_byte = 0
            self.bit_count = 0

    def write_bits(self, value: int, num_bits: int) -> None:
        """
        Write multiple bits from an integer value (MSB first).
        
        Args:
            value: The integer value whose bits will be written.
            num_bits: Number of bits to write (1 to 32).
        """
        for i in range(num_bits - 1, -1, -1):
            bit = (value >> i) & 1
            self.write_bit(bit)

    def write_code(self, code_str: str) -> None:
        """Write a binary code string like '01101'."""
        for char in code_str:
            if char == '1':
                self.write_bit(1)
            elif char == '0':
                self.write_bit(0)
            else:
                raise ValueError(f"Invalid bit character '{char}', must be '0' or '1'")

    def flush(self) -> bytes:
        """
        Pad the remaining bits with zeros to complete the final byte and return bytes.
        """
        if self.bit_count > 0:
            # Shift remaining bits to align with MSB
            self.current_byte <<= (8 - self.bit_count)
            self.buffer.append(self.current_byte)
            self.current_byte = 0
            self.bit_count = 0
        return bytes(self.buffer)

    def get_data(self) -> bytes:
        """Flushes and returns the resulting byte string."""
        return self.flush()


class BitReader:
    """
    Reads individual bits or multi-bit words from a bytes/bytearray object.
    
    Bits are unpacked MSB to LSB.
    """

    def __init__(self, data: bytes):
        self.data = data
        self.byte_index = 0
        self.bit_index = 0  # 0 (MSB) to 7 (LSB)
        self.total_bytes = len(data)

    def read_bit(self) -> int:
        """
        Read the next bit. Returns 0 or 1.
        Raises EOFError if end of data is reached.
        """
        if self.byte_index >= self.total_bytes:
            raise EOFError("Attempted to read past the end of the bit stream")

        current_byte = self.data[self.byte_index]
        bit = (current_byte >> (7 - self.bit_index)) & 1
        
        self.bit_index += 1
        if self.bit_index == 8:
            self.bit_index = 0
            self.byte_index += 1

        return bit

    def read_bits(self, num_bits: int) -> int:
        """
        Read `num_bits` as an unsigned integer (MSB first).
        Raises EOFError if there aren't enough bits remaining.
        """
        value = 0
        for _ in range(num_bits):
            value = (value << 1) | self.read_bit()
        return value

    def has_more(self) -> bool:
        """Check if there are more bits remaining to read."""
        return self.byte_index < self.total_bytes
