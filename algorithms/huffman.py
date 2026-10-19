"""
Huffman Coding Algorithm Implementation (DAA Project).

Algorithmic Paradigm: Greedy Strategy
Data Structure: Min-Heap (Priority Queue)

DESIGN AND ANALYSIS OF ALGORITHMS (DAA) THEORETICAL PRINCIPLES:
===============================================================
1. GREEDY CHOICE PROPERTY:
   Huffman coding produces an optimal variable-length, prefix-free binary code.
   At each step, the algorithm chooses the two symbols (or subtrees) with the
   lowest frequencies and merges them into a single parent node whose frequency
   is the sum of the two children. This local greedy choice is proven to lead to a
   globally optimal prefix-free tree (minimizing the expected code length / weighted
   external path length: sum(freq_i * depth_i)).

2. OPTIMAL SUBSTRUCTURE:
   Let C be an alphabet where each character c in C has frequency c.freq. Let x and y
   be two characters in C with the lowest frequencies. If C' is the alphabet C with
   x and y replaced by a new character z with z.freq = x.freq + y.freq, then the
   optimal tree for C can be obtained by taking the optimal tree for C' and making
   x and y children of z.

COMPLEXITY ANALYSIS:
====================
- Time Complexity:
  * Frequency Calculation: O(N) where N is the number of bytes in the file.
  * Heap Construction: O(K) where K is the number of distinct byte symbols (K <= 256).
  * Tree Construction: O(K log K) - exactly (K - 1) merges, each taking O(log K) heap ops.
  * Code Generation: O(K) via depth-first tree traversal.
  * Data Encoding: O(N) with O(1) table lookup per byte.
  * Total Compression Time: O(N + K log K). Since K <= 256, K log K is <= 2048 operations,
    making the time asymptotically O(N) linear in file size!
  * Total Decompression Time: O(N) traversing tree edges for each encoded bit.

- Space Complexity:
  * Tree and Heap Storage: O(K) nodes (at most 2 * 256 - 1 = 511 nodes).
  * Code Table: O(K) entries.
  * Bit Stream Buffer: O(N) bits (sub-linear to linear in N).
  * Total Auxiliary Space: O(K + N) -> O(N).
"""

import collections
import heapq
import struct
from typing import Dict, Optional, Tuple, List
from algorithms.base import BaseCompressor
from utils.file_io import ALGO_HUFFMAN
from utils.bit_stream import BitWriter, BitReader


class HuffmanNode:
    """
    Binary tree node for Huffman prefix tree.
    """

    def __init__(
        self,
        freq: int,
        byte_val: Optional[int] = None,
        left: Optional["HuffmanNode"] = None,
        right: Optional["HuffmanNode"] = None,
        order: int = 0,
    ):
        self.freq = freq
        self.byte_val = byte_val  # None for internal nodes, 0-255 for leaves
        self.left = left
        self.right = right
        self.order = order        # Tie-breaker for heap stability

    @property
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None

    def __lt__(self, other: "HuffmanNode") -> bool:
        """
        Comparison for min-heap priority queue.
        Greedy choice: lower frequency has higher priority (extracted first).
        Uses unique insertion order as tie-breaker when frequencies are equal.
        """
        if self.freq != other.freq:
            return self.freq < other.freq
        return self.order < other.order


class HuffmanCompressor(BaseCompressor):
    """
    Lossless compressor using Huffman coding on arbitrary byte sequences.
    """

    def __init__(self):
        super().__init__(name="Huffman Coding", algorithm_id=ALGO_HUFFMAN)

    def _build_frequency_table(self, data: bytes) -> Dict[int, int]:
        """Count frequencies of all byte symbols (0-255). Time: O(N)."""
        return dict(collections.Counter(data))

    def _build_huffman_tree(self, freq_table: Dict[int, int]) -> Optional[HuffmanNode]:
        """
        Constructs the optimal prefix-free tree using a min-heap priority queue.
        Demonstrates the Greedy Choice Property: repeatedly combine two minimum-weight nodes.
        Time: O(K log K) where K <= 256.
        """
        if not freq_table:
            return None

        heap: List[HuffmanNode] = []
        counter = 0

        # Step 1: Initialize min-heap with leaf nodes for each distinct symbol
        for byte_val, freq in freq_table.items():
            node = HuffmanNode(freq=freq, byte_val=byte_val, order=counter)
            heapq.heappush(heap, node)
            counter += 1

        # Edge case: Single distinct symbol
        if len(heap) == 1:
            only_node = heapq.heappop(heap)
            # Create a dummy parent so the root is not a leaf
            parent = HuffmanNode(
                freq=only_node.freq,
                left=only_node,
                right=None,
                order=counter,
            )
            return parent

        # Step 2: Greedy Merge Loop
        # Repeatedly pop two nodes with smallest frequencies and merge them.
        while len(heap) > 1:
            left_child = heapq.heappop(heap)
            right_child = heapq.heappop(heap)

            # Internal node: frequency is the sum of children
            merged = HuffmanNode(
                freq=left_child.freq + right_child.freq,
                byte_val=None,
                left=left_child,
                right=right_child,
                order=counter,
            )
            counter += 1
            heapq.heappush(heap, merged)

        return heapq.heappop(heap)

    def _generate_codes(self, root: Optional[HuffmanNode]) -> Dict[int, str]:
        """
        Traverses the Huffman tree to generate prefix-free variable-length binary codes.
        Left edge = '0', Right edge = '1'. Time: O(K).
        """
        code_table: Dict[int, str] = {}

        if root is None:
            return code_table

        def _traverse(node: HuffmanNode, current_code: str):
            if node.is_leaf:
                # If only one symbol exists in file, code is '0'
                code_table[node.byte_val] = current_code if current_code else "0"
                return
            if node.left:
                _traverse(node.left, current_code + "0")
            if node.right:
                _traverse(node.right, current_code + "1")

        _traverse(root, "")
        return code_table

    def _serialize_metadata(self, freq_table: Dict[int, int]) -> bytes:
        """
        Serializes the frequency table into binary format.
        Layout:
          - 2 bytes: number of distinct symbols K (uint16)
          - K entries of:
              - 1 byte: symbol (0-255)
              - 4 bytes: frequency (uint32)
        Total size: 2 + 5 * K bytes (at most 1,282 bytes).
        """
        meta = bytearray()
        meta.extend(struct.pack(">H", len(freq_table)))
        for byte_val, freq in freq_table.items():
            meta.extend(struct.pack(">BI", byte_val, freq))
        return bytes(meta)

    def _deserialize_metadata(self, metadata: bytes) -> Dict[int, int]:
        """
        Deserializes frequency table from header bytes.
        """
        if len(metadata) < 2:
            return {}

        num_symbols = struct.unpack_from(">H", metadata, 0)[0]
        offset = 2
        freq_table: Dict[int, int] = {}

        for _ in range(num_symbols):
            if offset + 5 > len(metadata):
                raise ValueError("Corrupted Huffman metadata: unexpected end of stream")
            byte_val, freq = struct.unpack_from(">BI", metadata, offset)
            freq_table[byte_val] = freq
            offset += 5

        return freq_table

    def compress(self, data: bytes) -> Tuple[bytes, bytes]:
        """
        Compresses input bytes using Huffman Coding.
        
        Returns:
            Tuple of (metadata: bytes, compressed_payload: bytes).
        """
        # Edge case: Empty file
        if not data:
            return b"", b""

        # 1. Frequency Analysis - O(N)
        freq_table = self._build_frequency_table(data)

        # 2. Greedy Huffman Tree Construction - O(K log K)
        tree_root = self._build_huffman_tree(freq_table)

        # 3. Generate Prefix Codes - O(K)
        code_table = self._generate_codes(tree_root)

        # 4. Serialize Metadata Header
        metadata = self._serialize_metadata(freq_table)

        # 5. Encode Data to Bit Stream - O(N)
        writer = BitWriter()
        for byte in data:
            writer.write_code(code_table[byte])

        compressed_payload = writer.flush()
        return metadata, compressed_payload

    def decompress(self, metadata: bytes, compressed_payload: bytes, original_size: int) -> bytes:
        """
        Decompresses payload back to original bytes using serialized frequency table.
        
        Args:
            metadata: Serialized frequency table.
            compressed_payload: Encoded bitstream.
            original_size: Expected number of bytes to reconstruct (prevents padding bit overrun).
        """
        # Edge case: 0-byte file
        if original_size == 0:
            return b""

        # 1. Rebuild Frequency Table & Tree from Metadata
        freq_table = self._deserialize_metadata(metadata)
        if not freq_table:
            raise ValueError("Corrupt or empty Huffman metadata table")

        tree_root = self._build_huffman_tree(freq_table)
        if tree_root is None:
            return b""

        # Edge case: File with only 1 distinct character repeated
        if len(freq_table) == 1:
            single_byte = next(iter(freq_table.keys()))
            return bytes([single_byte] * original_size)

        # 2. Decode Bit Stream by Traversing the Tree
        reader = BitReader(compressed_payload)
        output = bytearray()
        current_node = tree_root

        while len(output) < original_size:
            try:
                bit = reader.read_bit()
            except EOFError:
                break

            current_node = current_node.right if bit == 1 else current_node.left

            if current_node is None:
                raise ValueError("Corrupted Huffman bitstream: traversed invalid path")

            if current_node.is_leaf:
                output.append(current_node.byte_val)
                current_node = tree_root  # Reset back to root for next symbol

        if len(output) != original_size:
            raise ValueError(
                f"Huffman decompression size mismatch: expected {original_size} bytes, got {len(output)} bytes"
            )

        return bytes(output)
