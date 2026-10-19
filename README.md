# Lossless File Compression Tool (DAA Project)

An advanced, production-grade **Design and Analysis of Algorithms (DAA)** project implementing lossless compression and decompression on arbitrary binary files using three distinct algorithmic paradigms:

1. **Huffman Coding** — *Greedy Strategy with Min-Heap Priority Queue*
2. **Run-Length Encoding (RLE)** — *Linear Scan with Industrial PackBits Specification*
3. **Lempel-Ziv-Welch (LZW)** — *Adaptive Dictionary-Based Online Substitution*

---

## Table of Contents
- [Project Overview](#project-overview)
- [Architecture & Directory Structure](#architecture--directory-structure)
- [DAA Theoretical Foundations](#daa-theoretical-foundations)
  - [Proof of Huffman Coding Optimality](#proof-of-huffman-coding-optimality)
  - [Run-Length Encoding (PackBits) Analysis](#run-length-encoding-packbits-analysis)
  - [LZW Algorithm & The KwKwK Edge Case](#lzw-algorithm--the-kwkwk-edge-case)
- [Time & Space Complexity Table](#time--space-complexity-table)
- [Self-Contained Binary Container Specification](#self-contained-binary-container-specification)
- [Installation & Requirements](#installation--requirements)
- [Usage Guide](#usage-guide)
  - [Graphical User Interface (GUI)](#1-graphical-user-interface-gui)
  - [Interactive Command-Line Menu (CLI)](#2-interactive-command-line-menu-cli)
  - [CLI Flags / Scripting Mode](#3-cli-flags--scripting-mode)
  - [Running Automated Unit Tests](#4-running-automated-unit-tests)
- [Benchmarking & Sample Output](#benchmarking--sample-output)
- [Edge Case Handling](#edge-case-handling)

---

## Project Overview

In data compression, no single algorithm can compress all possible inputs losslessly (by the Pigeonhole Principle). This project demonstrates the theoretical and empirical trade-offs of three foundational algorithmic approaches:
- **Entropy Coding (Huffman):** Assigns variable-length bit codes based on individual character frequencies.
- **Run-Length Grouping (RLE):** Collapses consecutive sequences of identical bytes into length-value descriptors.
- **Dictionary Substitution (LZW):** Adaptively parses multi-byte phrases into numeric dictionary tokens without transmitting the dictionary.

### Core Features
- **Universal Binary Support:** Operates strictly on raw bytes (`0x00`–`0xFF`), handling text files, executables, images, audio, and archives without encoding corruption.
- **Self-Contained Compressed Archives (`.daac`):** All necessary metadata (such as the Huffman frequency table) is embedded in the binary container header. Archives can be transferred and decompressed on any system independently.
- **Bit-for-Bit Lossless Verification:** Embeds a 32-byte cryptographic SHA-256 digest in the file header to automatically guarantee 100% data integrity upon decompression.
- **Multi-Interface Support:** Includes both a modern **Tkinter GUI** and an **Interactive CLI menu**, alongside direct command-line arguments.
- **Performance Benchmarking & Graphing:** Generates comprehensive multi-panel comparison plots (Compression Ratio, Space Savings %, Compression/Decompression Latency) using Matplotlib (with a standalone SVG fallback).

---

## Architecture & Directory Structure

```
file_compression_tool/
├── algorithms/
│   ├── __init__.py           # Algorithm registry and factory methods
│   ├── base.py               # Abstract Base Class (BaseCompressor) & metrics structures
│   ├── huffman.py            # Huffman coding (min-heap, prefix-free tree traversal)
│   ├── rle.py                # PackBits binary Run-Length Encoding
│   └── lzw.py                # Variable bit-width (9-16 bits) LZW with CLEAR_CODE reset
├── utils/
│   ├── __init__.py           # Utility exports
│   ├── bit_stream.py         # BitWriter and BitReader for exact bit-level I/O
│   ├── file_io.py            # ContainerFile binary packing/unpacking and SHA-256 hashing
│   └── visualizer.py         # Matplotlib multi-panel chart & SVG fallback generator
├── samples/
│   ├── empty.txt             # 0-byte edge case
│   ├── single_char.txt       # 1-byte minimal tree edge case
│   ├── monolithic_same.txt   # 10 KB of identical characters (RLE best case)
│   ├── repetitive.txt        # Structured patterned repetitions (LZW & RLE showcase)
│   ├── natural_text.txt      # Alice in Wonderland excerpt (Huffman showcase)
│   ├── source_code.py        # Python code with recurring syntactic patterns
│   └── random.bin            # High-entropy random bytes (incompressible worst case)
├── benchmark.py              # Automated benchmarking harness across all datasets
├── cli.py                    # Interactive terminal menu & CLI argument parser
├── gui.py                    # Tkinter graphical interface (threaded, responsive)
├── main.py                   # Main dispatcher (auto-selects GUI or CLI fallback)
├── test_compression.py       # Comprehensive unit and integration test suite
├── generate_samples.py       # Dataset generator script
├── requirements.txt          # Optional dependencies (matplotlib, numpy)
└── README.md                 # Complete DAA documentation and analysis
```

---

## DAA Theoretical Foundations

### Proof of Huffman Coding Optimality

Huffman coding builds an optimal prefix-free binary code tree $T$ that minimizes the **weighted external path length** (expected code length):

$$B(T) = \sum_{c \in C} f(c) \cdot d_T(c)$$

where $C$ is the alphabet, $f(c)$ is the frequency of character $c$, and $d_T(c)$ is the depth of leaf $c$ in tree $T$ (corresponding to its bit-code length).

The optimality of Huffman's greedy algorithm rests upon two pillars of algorithm design:
1. **The Greedy Choice Property**
2. **Optimal Substructure**

#### 1. Greedy Choice Property
> **Lemma 1:** Let $C$ be an alphabet in which each character $c \in C$ has frequency $f(c)$. Let $x$ and $y$ be two characters in $C$ having the lowest frequencies. Then there exists an optimal prefix code for $C$ in which the codewords for $x$ and $y$ have the same maximum length and differ only in the last bit (i.e., $x$ and $y$ are sibling leaves at the maximum depth of the tree).

**Proof by Exchange Argument:**
Let $T$ be an optimal prefix-free tree. Let $a$ and $b$ be two sibling leaves of maximum depth in $T$. Without loss of generality, assume $f(a) \le f(b)$ and $f(x) \le f(y)$.
Since $x$ and $y$ have the lowest frequencies in $C$, we have $f(x) \le f(a)$ and $f(y) \le f(b)$.
- Exchange $x$ with $a$ in $T$ to create tree $T'$. The difference in tree cost is:
  $$B(T) - B(T') = \sum_{c} f(c)d_T(c) - \sum_{c} f(c)d_{T'}(c) = f(a)d_T(a) + f(x)d_T(x) - f(a)d_{T'}(a) - f(x)d_{T'}(x)$$
  Since $d_{T'}(a) = d_T(x)$ and $d_{T'}(x) = d_T(a)$:
  $$B(T) - B(T') = (f(a) - f(x))(d_T(a) - d_T(x)) \ge 0$$
  Because $f(a) \ge f(x)$ and $d_T(a) \ge d_T(x)$, the difference is non-negative, meaning $B(T') \le B(T)$. Since $T$ was optimal, $B(T') = B(T)$, so $T'$ is also optimal.
- Now exchange $y$ with $b$ in $T'$ to create $T''$. By the identical argument:
  $$B(T') - B(T'') = (f(b) - f(y))(d_{T'}(b) - d_{T'}(y)) \ge 0$$
  Thus, $B(T'') \le B(T')$, establishing that $T''$ is an optimal tree where $x$ and $y$ are sibling leaves at maximum depth.
  **Conclusion:** The greedy choice of pairing the two lowest-frequency symbols first is guaranteed to lead to a globally optimal solution.

#### 2. Optimal Substructure
> **Lemma 2:** Let $C$ be an alphabet with character frequencies $f(c)$. Let $x, y \in C$ be two characters of lowest frequency. Let $C' = (C \setminus \{x, y\}) \cup \{z\}$ be a reduced alphabet where $f(z) = f(x) + f(y)$. If $T'$ is an optimal prefix code tree for $C'$, then replacing leaf $z$ in $T'$ with an internal node having children $x$ and $y$ produces an optimal prefix code tree $T$ for $C$.

**Proof by Contradiction:**
For each $c \in C \setminus \{x, y\}$, the depth $d_T(c) = d_{T'}(c)$. For $x$ and $y$, $d_T(x) = d_T(y) = d_{T'}(z) + 1$.
The cost of tree $T$ is:
$$B(T) = B(T') - f(z)d_{T'}(z) + f(x)(d_{T'}(z) + 1) + f(y)(d_{T'}(z) + 1)$$
Since $f(z) = f(x) + f(y)$:
$$B(T) = B(T') + f(x) + f(y)$$
Suppose for contradiction that $T$ is not optimal for $C$. Then there exists a tree $T^*$ for $C$ such that $B(T^*) < B(T)$. By Lemma 1, we can assume $x$ and $y$ are siblings in $T^*$.
Let $T^{*'}$ be $T^*$ with $x$ and $y$ replaced by their parent $z$. Then:
$$B(T^{*'}) = B(T^*) - f(x) - f(y) < B(T) - f(x) - f(y) = B(T')$$
This contradicts the optimality of $T'$ for $C'$. Therefore, $T$ must be optimal for $C$.

**Induction Conclusion:** By combining the Greedy Choice Property (Lemma 1) and Optimal Substructure (Lemma 2), mathematical induction on $|C|$ proves that Huffman's algorithm constructs an optimal prefix code.

---

### Run-Length Encoding (PackBits) Analysis

A naive RLE scheme that writes a `(count, byte)` pair for every byte doubles the file size on non-repeating data (`ABC` $\to$ `1A 1B 1C`, +100% overhead).

To solve this, we implement the **Apple Macintosh / TIFF / PDF PackBits specification**:
- Each chunk begins with a signed 8-bit control byte $N \in [-128, +127]$:
  - **Literal Run ($0 \le N \le 127$):** The next $N + 1$ bytes are copied directly without compression. Overhead on completely random data is bounded by only 1 byte per 128 bytes ($\approx +0.78\%$).
  - **Replicated Run ($-127 \le N \le -1$):** The single byte following the control byte is repeated $(-N + 1)$ times (2 to 128 repetitions). Compresses 128 repeated bytes down to 2 bytes ($64\times$ compression ratio).
  - **$N = -128$ (`0x80`):** Reserved as a no-op/padding marker.

---

### LZW Algorithm & The KwKwK Edge Case

LZW adaptively maps variable-length byte phrases to fixed/variable-width integer codes.
- Starts with an initial table of 256 entries (`0x00`–`0xFF`).
- As new multi-byte phrases are encountered, they are added to the dictionary.
- Our implementation uses **variable-width bit packaging (9 to 16 bits)**:
  - Begins with 9 bits (capacity 512).
  - Expands bit width dynamically ($9 \to 10 \to 11 \dots \to 16$) as the dictionary fills up.
  - When the dictionary reaches $2^{16} = 65,536$ entries, it outputs `CLEAR_CODE (256)` and resets the dictionary, enabling seamless adaptation to changing file patterns.

#### The "KwKwK" / `cScSc` Decoder Edge Case:
During decompression, a rare condition occurs when the encoder encounters a pattern where the string being defined is immediately used in the next step (e.g., `ABABABA`).
The decoder receives code $C$, but $C$ is not yet in its dictionary!
- **Mathematical Invariant:** This condition occurs if and only if $C = \text{next\_available\_code}$.
- **Resolution:** The missing phrase is guaranteed to be:
  $$\text{phrase} = \text{previous\_phrase} + \text{previous\_phrase}[0]$$
The decoder reconstructs this phrase, inserts it into the dictionary, and writes it to the output.

---

## Time & Space Complexity Table

Let:
- $N$ = Total file size in bytes
- $K$ = Number of distinct byte symbols in the file ($1 \le K \le 256$)
- $D$ = Maximum LZW dictionary capacity ($D = 65,536 = O(1)$ constant)

| Algorithm | Paradigm | Compression Time (Best / Avg / Worst) | Decompression Time | Space Complexity | Best-Suited File Types |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Huffman Coding** | Greedy (Min-Heap Priority Queue) | $O(N) / O(N + K \log K) / O(N + K \log K)$ | $O(N)$ | $O(K + N)$ bits | Natural text, English prose, skewed frequency distributions |
| **Run-Length Encoding (PackBits)** | Linear Window Scan | $O(N/128) / O(N) / O(N)$ | $O(N)$ | $O(1)$ aux, $O(N)$ output | Monolithic runs, uncompressed bitmaps, sparse masks |
| **LZW Compression** | Adaptive Dictionary Substitution | $O(N) / O(N) / O(N)$ | $O(N)$ | $O(D) = O(1)$ aux, $O(N)$ output | Source code, repetitive logs, structured text, markup |

*Note on Huffman:* Because $K \le 256$ for byte-level compression, $K \log K \le 2048$ is a bounded constant. Hence, Huffman coding runs in strictly linear $O(N)$ time.

---

## Self-Contained Binary Container Specification

Every compressed file produced by this tool uses the standardized `.daac` container format:

```
+-----------------------------------------------------------------------+
| Offset (Bytes) | Field Name       | Type    | Description             |
+-----------------------------------------------------------------------+
| 00 - 03        | Magic Bytes      | 4 Bytes | ASCII "DAAC"            |
| 04             | Format Version   | uint8   | Format version (0x01)   |
| 05             | Algorithm ID     | uint8   | 1=Huffman, 2=RLE, 3=LZW |
| 06 - 13        | Original Size    | uint64  | Exact byte count (BE)   |
| 14 - 45        | SHA-256 Checksum | 32 B    | Cryptographic digest    |
| 46 - 49        | Metadata Length  | uint32  | Size of metadata (BE)   |
| 50 - (50+M-1)  | Metadata Payload | M Bytes | Serialized table/params |
| (50+M) - EOF   | Compressed Data  | Variable| Encoded bit/byte stream |
+-----------------------------------------------------------------------+
```

### Why this design is robust:
1. **Self-Sufficiency:** Decompressors do not require external code tables; the Huffman frequency table is deserialized directly from the metadata section.
2. **Exact Boundary Guarantee:** `Original Size (uint64)` prevents any trailing padding bits (from bitstream byte-alignment) from corrupting the reconstructed file.
3. **Automated Lossless Proof:** The 32-byte SHA-256 digest provides cryptographic assurance that every byte was reconstructed perfectly.

---

## Installation & Requirements

The core compression tool, CLI, and Tkinter GUI run entirely on the **Python Standard Library** (`heapq`, `struct`, `collections`, `hashlib`, `tkinter`).

### Optional Visualization Dependencies
For generating high-resolution PNG charts:
```bash
pip install -r requirements.txt
```
*(If Matplotlib is not installed, the tool automatically generates high-quality vector `.svg` benchmark charts without crashing.)*

---

## Usage Guide

### 1. Graphical User Interface (GUI)

Launch the modern desktop application:
```bash
python main.py
# or explicitly
python main.py --gui
```
- **Compress Tab:** Browse for any file, pick an algorithm (Huffman, RLE, or LZW), and see live compression ratios and space savings.
- **Decompress Tab:** Select any `.daac` archive. The GUI inspects the header, identifies the algorithm, restores the file, and runs a cryptographic SHA-256 lossless check.
- **Benchmark Tab:** Click **"Run Full Benchmark Suite"** to run all algorithms across all test datasets and display results in an interactive table.

---

### 2. Interactive Command-Line Menu (CLI)

Run the interactive terminal interface:
```bash
python main.py --cli
```
Example terminal session:
```text
========================================================================
       LOSSLESS FILE COMPRESSION TOOL (DAA PROJECT)
       Algorithms: Huffman Coding | Run-Length (RLE) | LZW
========================================================================

MAIN MENU:
  1. Compress a file
  2. Decompress a file (.daac archive)
  3. Run comprehensive benchmark & generate comparison graphs
  4. Verify two files are identical (lossless checker)
  5. Exit

Select an option (1-5): 1
```

---

### 3. CLI Flags / Scripting Mode

Directly invoke operations via terminal arguments:

#### Compress a file:
```bash
# Using Huffman Coding
python main.py compress -a huffman -i samples/natural_text.txt -o text.huff.daac

# Using Run-Length Encoding
python main.py compress -a rle -i samples/repetitive.txt -o rep.rle.daac

# Using LZW Compression
python main.py compress -a lzw -i samples/source_code.py -o code.lzw.daac
```

#### Decompress an archive:
```bash
# Decompress and verify against original
python main.py decompress -i text.huff.daac -o restored_text.txt -v samples/natural_text.txt
```

#### Run the benchmark suite from CLI:
```bash
python main.py benchmark -o benchmark_results.png
```

---

### 4. Running Automated Unit Tests

Run the test suite verifying edge cases and lossless roundtrips:
```bash
python -m unittest test_compression.py -v
```

---

## Benchmarking & Sample Output

### Empirical Benchmark Matrix

The following results were recorded across standard test datasets:

```text
===================================================================================================================
Dataset              | Algorithm          | Orig (B)  | Comp (B)  | Ratio   | Savings  | Comp(ms)  | Decomp(ms) | Lossless
-------------------------------------------------------------------------------------------------------------------
Empty (0 Bytes)      | Huffman Coding     | 0         | 50        | 0.00x   |   0.0%   | 0.04      | 0.03       | PASS
Empty (0 Bytes)      | Run-Length (RLE)   | 0         | 50        | 0.00x   |   0.0%   | 0.02      | 0.02       | PASS
Empty (0 Bytes)      | LZW Compression    | 0         | 50        | 0.00x   |   0.0%   | 0.02      | 0.02       | PASS
-------------------------------------------------------------------------------------------------------------------
Single Char (1 B)    | Huffman Coding     | 1         | 58        | 0.02x   | -5700.0% | 0.08      | 0.03       | PASS
Single Char (1 B)    | Run-Length (RLE)   | 1         | 52        | 0.02x   | -5100.0% | 0.02      | 0.02       | PASS
Single Char (1 B)    | LZW Compression    | 1         | 53        | 0.02x   | -5200.0% | 0.05      | 0.03       | PASS
-------------------------------------------------------------------------------------------------------------------
Monolithic (10 KB)   | Huffman Coding     | 10,240    | 1,338     | 7.65x   | +86.9%   | 0.94      | 0.42       | PASS
Monolithic (10 KB)   | Run-Length (RLE)   | 10,240    | 212       | 48.30x  | +97.9%   | 0.38      | 0.09       | PASS
Monolithic (10 KB)   | LZW Compression    | 10,240    | 374       | 27.38x  | +96.3%   | 2.15      | 0.34       | PASS
-------------------------------------------------------------------------------------------------------------------
Repetitive Data      | Huffman Coding     | 11,850    | 6,564     | 1.81x   | +44.6%   | 1.48      | 1.25       | PASS
Repetitive Data      | Run-Length (RLE)   | 11,850    | 2,410     | 4.92x   | +79.7%   | 0.45      | 0.22       | PASS
Repetitive Data      | LZW Compression    | 11,850    | 1,514     | 7.83x   | +87.2%   | 2.40      | 0.48       | PASS
-------------------------------------------------------------------------------------------------------------------
Natural Prose        | Huffman Coding     | 12,416    | 7,242     | 1.71x   | +41.7%   | 1.82      | 1.40       | PASS
Natural Prose        | Run-Length (RLE)   | 12,416    | 12,568    | 0.99x   |  -1.2%   | 0.62      | 0.18       | PASS
Natural Prose        | LZW Compression    | 12,416    | 5,984     | 2.07x   | +51.8%   | 2.85      | 0.65       | PASS
-------------------------------------------------------------------------------------------------------------------
Source Code          | Huffman Coding     | 9,840     | 5,612     | 1.75x   | +43.0%   | 1.35      | 1.10       | PASS
Source Code          | Run-Length (RLE)   | 9,840     | 9,926     | 0.99x   |  -0.9%   | 0.51      | 0.16       | PASS
Source Code          | LZW Compression    | 9,840     | 3,428     | 2.87x   | +65.2%   | 2.22      | 0.52       | PASS
-------------------------------------------------------------------------------------------------------------------
Random Binary        | Huffman Coding     | 10,240    | 11,574    | 0.88x   | -13.0%   | 2.10      | 1.85       | PASS
Random Binary        | Run-Length (RLE)   | 10,240    | 10,372    | 0.99x   |  -1.3%   | 0.58      | 0.17       | PASS
Random Binary        | LZW Compression    | 10,240    | 12,852    | 0.80x   | -25.5%   | 3.10      | 0.92       | PASS
===================================================================================================================
```

### Key Analytical Takeaways:
1. **RLE is Supreme for Monolithic Runs:** Compresses 10 KB of identical bytes down to 212 bytes ($48.3\times$ compression) with virtually instant execution ($0.38\text{ ms}$). However, for natural text and code, PackBits limits negative expansion to only $-1\%$.
2. **Huffman Provides Dependable Compression on Skewed Text:** Consistently reduces natural prose and source code by $41\%\text{--}44\%$ because English letter frequencies (e.g., `'e'`, `'t'`, spaces) have significantly lower Shannon entropy.
3. **LZW Excels on Structured Syntax:** Dominates on repetitive patterns ($7.83\times$ compression) and source code ($65.2\%$ savings) by reusing recurring multi-byte tokens like keywords and indentation.
4. **Random Data Confirms Information Theory Limits:** When Shannon entropy approaches maximum (8 bits per byte), all lossless algorithms yield a ratio $< 1.0\times$ due to container header overhead.

---

## Edge Case Handling

| Edge Case | Potential Pitfall | Tool Implementation Solution |
| :--- | :--- | :--- |
| **0-byte empty file** | Division by zero; empty tree error; EOF crash | Header records `original_size = 0`. Compressor emits empty payload. Decompressor returns immediately without attempting tree traversal. |
| **Single-character file** (`"AAAA"`) | Huffman binary tree cannot split with only 1 leaf | Root node created with single leaf assigned code `'0'`. Decompressor outputs symbol $N$ times according to `original_size`. |
| **Odd bit padding** | Huffman/LZW bitstreams may leave 1–7 trailing bits in final byte | Container header explicitly stores `original_size (uint64)`. Decompression terminates when the exact byte count is reached, discarding trailing padding bits. |
| **KwKwK / cScSc sequence** | LZW decoder encounters a code not yet in its dictionary | Decoder detects `code == len(dictionary)` and constructs `previous_phrase + previous_phrase[0]`. |
| **Dictionary Saturation** | LZW memory consumption grows unboundedly | Dictionary capped at $2^{16} = 65,536$ entries. Automatically emits `CLEAR_CODE` to flush and reset bit width back to 9 bits. |
| **Archive Corruption** | Tampered bits produce silent data corruption | Every archive includes a 32-byte SHA-256 digest. Decompression verifies the hash before confirming success. |
