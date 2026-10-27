# SYNOPSIS & VIVA PREPARATION GUIDE

## Lossless File Compression Tool — Design and Analysis of Algorithms (DAA) Project

> A single, self-contained document covering the project synopsis, deep theoretical foundations, code-level understanding, benchmark analysis, and a comprehensive bank of likely viva questions with model answers.

---

# PART A — PROJECT SYNOPSIS

---

## A1. Project Title

**Lossless File Compression and Decompression Tool using Huffman Coding, Run-Length Encoding (PackBits) and Lempel-Ziv-Welch (LZW) Compression**

## A2. Introduction / Background

Data compression is the process of encoding information using fewer bits than the original representation. It is one of the most direct practical applications of information theory and algorithm design.

**Lossless compression** guarantees that the decompressed data is *bit-for-bit identical* to the original — essential for text, source code, executables, medical records, and archival data. Unlike lossy compression (JPEG, MP3) which discards imperceptible information, lossless methods exploit only *redundancy* and never discard information.

A fundamental result from information theory (and a consequence of the **pigeonhole principle**) is that **no single lossless compression algorithm can compress all possible input files**. If an algorithm compressed *every* possible file, then, because there are more files of length `n + k` than of length `n`, two distinct long files would have to map to the same short compressed file — making decompression ambiguous. Therefore, any practical compressor must be specialized: it will compress some file types well and may even *expand* others. This project empirically demonstrates this truth through three algorithms with three completely different "specializations".

## A3. Problem Statement

Design and implement a unified, platform-independent tool that:

1. Compresses **arbitrary binary files** (text, images, executables, archives) losslessly.
2. Decompresses them back to the exact original bytes.
3. Embeds all metadata (code tables, checksums) inside a self-contained container file, so archives are independently portable.
4. Provides cryptographic (SHA-256) proof of bit-for-bit lossless reconstruction.
5. Benchmarks and compares the algorithms across diverse datasets.
6. Offers multiple user interfaces (GUI, interactive CLI, scriptable CLI).

## A4. Objectives

| # | Objective | Status |
|---|-----------|--------|
| 1 | Implement Huffman coding using a greedy min-heap strategy | Done |
| 2 | Implement PackBits-standard Run-Length Encoding | Done |
| 3 | Implement variable-width (9–16 bit) LZW with dictionary reset | Done |
| 4 | Design a self-contained binary container format | Done |
| 5 | Add SHA-256 integrity verification for lossless proof | Done |
| 6 | Handle all critical edge cases (empty file, single symbol, bit padding, KwKwK, dictionary saturation) | Done |
| 7 | Build GUI (Tkinter), interactive CLI, and argparse CLI | Done |
| 8 | Build a benchmarking harness with multi-panel visualizations | Done |
| 9 | Write a comprehensive unit/integration test suite | Done |

## A5. Scope and Limitations

**Scope:**
- Byte-level (0x00–0xFF) lossless compression of any file type.
- Three classic algorithms representing three distinct DAA paradigms.
- Files of arbitrary size (dictionary is bounded; container uses uint64 for original size).

**Limitations:**
- Huffman and LZW implementations are educational pure-Python; real systems (zlib, zstd) use hand-tuned C with larger windows and adaptive arithmetic coding.
- Huffman stores the full frequency table in metadata (max ~1.3 KB overhead). Real implementations transmit canonical Huffman codes or use adaptive Huffman (Vitter's algorithm) to avoid the table.
- No multi-threading, streaming, or dictionary reuse across files (no "pre-loaded dictionary" mode like GIF/LZW or LZ77 sliding window).
- Single-threaded; not designed for real-time or GB-scale files, though nothing prevents it.

## A6. Algorithmic Paradigms Adopted (The DAA Core)

| Algorithm | DAA Paradigm | Key Data Structure | Exploits |
|-----------|--------------|---------------------|----------|
| **Huffman Coding** | **Greedy Strategy** (proven optimal via greedy-choice property + optimal substructure) | Min-heap priority queue → binary prefix tree | Skewed symbol frequency distributions (statistical redundancy) |
| **RLE (PackBits)** | **Linear Scan / Divide into runs** | Sequential buffer scan with lookahead | Spatial locality — long runs of identical bytes |
| **LZW** | **Adaptive (online) dictionary / dynamic programming over phrases** | Hash map (encoder) / indexed array (decoder) | Repeated multi-byte phrases (structural redundancy) |

These three cover the three classical redundancy types:
1. **Statistical redundancy** → Huffman (entropy coding)
2. **Run redundancy** → RLE (run-length grouping)
3. **Phrase/pattern redundancy** → LZW (dictionary substitution)

## A7. Methodology

1. **Abstraction via OOP:** An abstract base class `BaseCompressor` (`algorithms/base.py:35`) defines the contract — `compress(data) -> (metadata, payload)` and `decompress(metadata, payload, original_size) -> data`. File I/O, container packing, timing, and verification are implemented once in the base class so each algorithm implements only its pure logic (**Template Method pattern**).
2. **Bit-level I/O:** Custom `BitWriter`/`BitReader` (`utils/bit_stream.py`) pack bits MSB-first into bytes, essential for Huffman (variable-length codes) and LZW (9–16-bit codes).
3. **Self-contained container:** Every archive carries a 50-byte fixed header + algorithm-specific metadata + payload (`utils/file_io.py`).
4. **Verification:** SHA-256 of the original is stored in the header; after decompression the hash is recomputed and compared, plus optional byte-by-byte file comparison.
5. **Benchmarking:** `benchmark.py` runs every algorithm on every dataset, records size/ratio/savings/time/verification, prints a table, and plots a 2×2 dashboard (`utils/visualizer.py`, with a pure-SVG fallback if Matplotlib is absent).
6. **Testing:** `test_compression.py` uses `unittest` to verify in-memory and containerized round-trips for every algorithm across edge cases, including the KwKwK pattern and all 256 byte values.

## A8. Software Requirements

- **Language:** Python 3.8+ (developed and tested on Python 3.14)
- **Core dependencies:** None — pure Python standard library (`heapq`, `struct`, `collections`, `hashlib`, `argparse`, `tempfile`, `unittest`)
- **GUI:** Tkinter (ships with standard Python)
- **Optional:** `matplotlib` + `numpy` for PNG charts (auto-fallback to generated SVG)

## A9. Hardware Requirements

Any machine capable of running Python 3 — no special hardware needed.

---

# PART B — DEEP TECHNICAL UNDERSTANDING

---

## B1. Information-Theoretic Foundations

### B1.1 Why compression is possible at all
Files contain **redundancy**. English text has highly skewed letter frequencies; images have smooth regions; executables repeat opcodes. Compression replaces redundant patterns with shorter codes.

### B1.2 Shannon Entropy — the theoretical limit
For a source with symbol probabilities $p_i$, the average number of bits per symbol cannot go below:

$$H = -\sum_{i} p_i \log_2 p_i \quad \text{(bits/symbol)}$$

- Uniform distribution over 256 bytes (random data): $H = 8$ bits/byte → **no lossless compression possible**; any container adds overhead, so compressed size > original.
- English prose: $H \approx 1.3$–$1.5$ bits/character → Huffman typically achieves ~40–50% savings.
- Monolithic run of one symbol: $H \to 0$ → RLE achieves near-perfect ~64× compression.

### B1.3 The pigeonhole argument (why no universal compressor)
There are $256^n$ files of length $n$ but only $256^{n/2}$ files of length $n/2$. A compressor mapping every length-$n$ file to a length-$n/2$ file must map two different files to the same output → decompression is ambiguous. Hence, a correct lossless compressor must *sometimes* expand. Our benchmarks confirm this: on `random.bin`, all three algorithms expand the file.

### B1.4 Kraft inequality (prefix-free codes)
A set of codeword lengths $l_i$ is decodable without ambiguity (prefix property) iff:

$$\sum_i 2^{-l_i} \le 1$$

Huffman's algorithm produces lengths that satisfy Kraft's inequality with equality (a full tree) and minimize $\sum f_i l_i$ among all integer lengths satisfying it.

---

## B2. Huffman Coding — Complete Deep Dive

### B2.1 What it does
Assigns a variable-length binary codeword to each byte such that **no codeword is a prefix of another** (prefix-free / instantaneous code), giving frequent bytes short codes and rare bytes long codes.

### B2.2 Algorithm (as implemented in `algorithms/huffman.py`)

**Compression:**
1. **Frequency counting** — `collections.Counter(data)` → O(N). (`huffman.py:94`)
2. **Tree construction** — push all K leaves into a `heapq` min-heap; repeatedly pop the two smallest, merge into a parent with frequency = sum, push back. K−1 merges. (`huffman.py:98`)
3. **Code generation** — DFS from root: left edge = `'0'`, right edge = `'1'`; leaf code = path string. O(K). (`huffman.py:147`)
4. **Serialization of metadata** — frequency table written as: `uint16 K` followed by K × (`uint8 symbol` + `uint32 frequency`) = `2 + 5K` bytes (max 1,282 bytes). (`huffman.py:170`)
5. **Bit-level encoding** — each byte replaced by its code string, written via `BitWriter`. O(N). (`huffman.py:206`)

**Decompression:**
1. Deserialize the frequency table from metadata, **rebuild the exact same tree** (the greedy algorithm is deterministic given frequencies and insertion order).
2. Read bits one at a time, walking left (0) / right (1); on reaching a leaf, emit the symbol and return to root. Stop exactly at `original_size` bytes (discarding padding bits). (`huffman.py:264`)

### B2.3 Optimality Proof (the two pillars — memorize this)

**Goal:** Minimize weighted external path length $B(T) = \sum_{c} f(c)\cdot d_T(c)$.

**Lemma 1 — Greedy Choice Property:**
Let $x, y$ be the two lowest-frequency symbols. There exists an optimal prefix code where $x$ and $y$ are siblings at maximum depth.

*Proof (exchange argument):* Take an optimal tree $T$; let $a, b$ be deepest siblings with $f(a) \le f(b)$ and assume $f(x) \le f(a)$, $f(y) \le f(b)$ (since $x,y$ are minimal). Swap $x \leftrightarrow a$ to get $T'$. Cost difference:

$$B(T) - B(T') = (f(a)-f(x))(d_T(a)-d_T(x)) \ge 0$$

since both factors are non-negative. So $B(T') \le B(T)$; by optimality of $T$, $B(T') = B(T)$. Repeat for $y \leftrightarrow b$. ∎

**Lemma 2 — Optimal Substructure:**
Let $C' = (C \setminus \{x,y\}) \cup \{z\}$ with $f(z)=f(x)+f(y)$. If $T'$ is optimal for $C'$, then replacing leaf $z$ with an internal node having children $x,y$ yields an optimal $T$ for $C$.

*Proof:* $B(T) = B(T') + f(x) + f(y)$. If some $T^*$ were better for $C$, merging $x,y$ in $T^*$ would give a better tree for $C'$ — contradiction with optimality of $T'$. ∎

**Conclusion (induction on |C|):** Greedy choice + optimal substructure ⟹ Huffman's algorithm is optimal among all prefix-free binary codes. *(Note: it is optimal among integer code lengths; arithmetic/range coding can approach entropy even more closely with fractional lengths.)*

### B2.4 Worked example
Text = `"banana"`: frequencies b:1, a:3, n:2.
Heap: (1,b),(2,n),(3,a) → merge b+n = 3 → heap: (3,a),(3,bn) → merge = 6.
Codes: a→0, n→10, b→11. Encoded: `0 10 0 10 0 11` = 11 bits vs 48 bits raw.

### B2.5 Complexity
- Time: O(N) counting + O(K log K) heap merges + O(K) codegen + O(N) encoding = **O(N + K log K)**; since K ≤ 256, this is effectively **O(N)**.
- Space: O(K) tree nodes (≤ 511) + O(N) bit buffer.

### B2.6 Key implementation details to mention in viva
- **Heap tie-breaking:** `HuffmanNode.__lt__` falls back to insertion `order` when frequencies are equal (`huffman.py:75`), guaranteeing the encoder and decoder build **identical trees** — a subtle but critical correctness requirement.
- **Single-symbol edge case:** a tree with one leaf has no edges, so the code would be the empty string. The code wraps the leaf in a dummy parent so its code becomes `"0"` (`huffman.py:117`); decoder special-cases `len(freq_table)==1` and emits the symbol `original_size` times (`huffman.py:260`).
- **Decompression stops by byte count, not by tree state** — this is what makes trailing pad bits harmless (`huffman.py:269`).
- **Metadata cost:** up to 1,282 bytes; hence Huffman loses on tiny files.

---

## B3. Run-Length Encoding (PackBits) — Complete Deep Dive

### B3.1 The problem with naive RLE
Storing `(count, byte)` per run doubles size on non-repeating data: `ABC` → `1A 1B 1C`. That's +100% expansion — unacceptable.

### B3.2 The PackBits solution (Apple/TIFF/PDF standard) — `algorithms/rle.py`
Each chunk starts with a **signed 8-bit control byte** N ∈ [−128, +127]:

| Control byte N | Meaning | Output |
|---|---|---|
| `0 ≤ N ≤ 127` | **Literal run** | Copy next N+1 bytes verbatim (1–128 bytes) |
| `−127 ≤ N ≤ −1` | **Replicated run** | Repeat next 1 byte (−N+1) times (2–128 times) |
| `−128` (0x80) | Reserved no-op | Skip (padding marker) |

**Why it bounds expansion:** worst case (no repeats) costs 1 control byte per 128 data bytes ≈ **+0.78%** expansion. Best case: 128 identical bytes → 2 bytes = **64× compression**.

### B3.3 Encoder logic (`rle.py:55`)
- Scan for a run of identical bytes, capped at 128. If run length ≥ 2 → emit `(-(run_length-1)) & 0xFF` + the byte.
- Otherwise emit a literal run, but **stop the literal run early if the next 3 bytes are identical** (`rle.py:89`) — a lookahead heuristic so a newly-started run is handled by the replicated branch (runs of exactly 2 are efficiently encoded as replicated runs).
- Runs longer than 128 are split into multiple chunks.

### B3.4 Decoder logic (`rle.py:100`)
Convert control byte to signed (`n = b if b ≤ 127 else b − 256`), dispatch on the three cases, and stop at `original_size`. Bounds-checks against payload truncation to detect corruption.

### B3.5 Complexity
- Time: O(N) both directions (single pass).
- Space: O(1) auxiliary (only counters/indices); output buffer O(N) worst case.
- Metadata: empty (`b""`) — PackBits is **self-describing**, zero header cost inside the payload.

### B3.6 When it wins / loses
- **Wins:** bitmap images, monochrome masks, fax-like data, runs of zeros (our monolithic sample: 10,240 → 212 bytes ≈ 48×).
- **Loses:** natural text / random data → still only −1% thanks to PackBits (this is exactly *why* PackBits replaced naive RLE in real standards).

---

## B4. LZW — Complete Deep Dive

### B4.1 Core idea
Instead of describing *how* to reproduce data, describe it as a sequence of **dictionary indices**. The dictionary is built **online, identically, at both encoder and decoder** — so it is never transmitted. This is an **adaptive / incremental** algorithm (a member of the LZ78 family; Welch added the greedy longest-match encoding in 1984).

### B4.2 Encoder (`algorithms/lzw.py:73`)
Constants: `INIT_BITS=9`, `MAX_BITS=16`, `MAX_DICT_SIZE=65536`, `CLEAR_CODE=256`, `END_OF_STREAM=257`, first free code = 258.

1. Emit `CLEAR_CODE` (resets decoder deterministically at start).
2. Initialize dictionary with 256 single-byte strings → codes 0..255.
3. `current_phrase = first byte`. For each next byte:
   - If `current_phrase + byte` ∈ dictionary → extend `current_phrase`.
   - Else → **emit** code of `current_phrase`; **add** `current_phrase + byte` as the next code; reset `current_phrase = byte`.
4. Emit the final phrase's code, then `END_OF_STREAM`.

**Variable bit-width:** codes are written using `current_bits`, starting at 9. When `next_code == (1 << current_bits)`, increment width (9→10→…→16). This is what makes LZW efficient — early short codes use few bits.

**Critical synchronization detail — "early change":** the decoder is always exactly **one dictionary entry behind** the encoder (it cannot add the current phrase until it reads the *next* code). Therefore the decoder must widen its code width one entry early — when `len(dictionary) == (1 << current_bits) - 1`, not when it equals `1 << current_bits` (`lzw.py:181`). Without this off-by-one correction, the decoder reads a 9-bit code where the encoder wrote 10 bits and the stream desynchronizes (this was caught by `test_large_random_stream`). This is the same "early change" nuance found in TIFF's LZW variant.

**Dictionary saturation:** when `next_code` reaches 65,536, the encoder emits `CLEAR_CODE` and resets the dictionary and bit width to 9 (`lzw.py:111`). This adapts to "phase changes" in the data and bounds memory. (Real GIF uses a similar clear mechanism; TIFF's LZW uses an early-change off-by-one variant.)

### B4.3 Decoder (`lzw.py:129`)
Uses a **list** for O(1) indexed lookup. Maintains `previous_phrase`. For each code:
- `code < len(dict)` → phrase = dict[code]
- **`code == len(dict)` → the KwKwK case** (see below)
- else → corrupt stream error

After emitting, add `previous_phrase + phrase[0]` to the dictionary (mirrors encoder exactly — the encoder added that same string one step earlier).

### B4.4 The KwKwK / cScSc edge case (guaranteed viva question)

**Scenario:** encoder is processing `...ScSc...`. It emits code for `Sc`, then next iteration wants `ScS`; `ScS` is not in the dictionary, so it will be added as code K. But then immediately the phrase continues and the encoder emits **K itself** in the very next output — before the decoder has had a chance to add K.

**Decoder observation:** it receives a code equal to `len(dictionary)` — the next code that *would* be assigned.

**Mathematical invariant:** that missing phrase is always:

$$\text{phrase} = \text{previous\_phrase} + \text{previous\_phrase}[0]$$

**Resolution** (`lzw.py:167`): reconstruct the phrase from the previous phrase, output it, and add it to the dictionary as usual. The classic triggering pattern is `ABABABAB...` — our test `test_classic_kwkwk_edge_case` uses exactly this.

**How to explain it in one sentence for viva:** *"When the decoder receives a code that is not yet in its dictionary, it must be the code the encoder is defining right now, and that string is guaranteed to be the previous string with its first character appended."*

### B4.5 Complexity
- Time: O(N) — amortized O(1) dictionary operations per input byte (hash map for encoder, array for decoder).
- Space: dictionary ≤ 65,536 entries = **O(1) in asymptotic terms** (bounded constant), plus O(N) output.
- Metadata: empty — LZW is fully self-describing from the code stream.

### B4.6 Why LZW wins on source code
Keywords, indentation (`    self.`), and repeated syntactic fragments get dictionary entries early and are then emitted as single short codes — multi-byte redundancy, which Huffman (byte-level) cannot capture at all.

---

## B5. The Self-Contained Binary Container Format

Defined in `utils/file_io.py:40` with `struct` format `">4sBBQ32sI"` (big-endian):

```
+---------------------------+-----------------------------------------------+
| Offset                    | Field                                         |
+---------------------------+-----------------------------------------------+
| 0–3                       | Magic bytes "DAAC" (4 bytes)                  |
| 4                         | Format version (uint8, = 1)                   |
| 5                         | Algorithm ID (uint8: 1=Huffman, 2=RLE, 3=LZW) |
| 6–13                      | Original size (uint64, big-endian)            |
| 14–45                     | SHA-256 digest of original (32 bytes)         |
| 46–49                     | Metadata length M (uint32)                    |
| 50–49+M                   | Metadata payload (M bytes)                    |
| 50+M–EOF                  | Compressed payload                            |
+---------------------------+-----------------------------------------------+
Fixed header size = 50 bytes. Max metadata = Huffman's 2 + 5×256 = 1,282 bytes.
```

**Design rationale (expect this question):**
1. **Magic bytes** → instant format identification + corruption detection (`file_io.py:98`).
2. **Algorithm ID** → decompressor auto-selects the right decoder without user input (CLI peeks at 64 bytes to detect the algorithm before full decompression, `cli.py:120`).
3. **uint64 original size** → the *only* reliable way to discard trailing padding bits from bit-packing; also validates reconstruction length.
4. **SHA-256** → cryptographic (not just checksum) proof of lossless round-trip; catches silent corruption that a length check would miss.
5. **Metadata length** → makes the format extensible (v2 could add per-file dictionaries, canonical Huffman codes, etc.) while keeping parsing O(1) offsets.

This is the same philosophy as real archive formats (PNG's IHDR chunks, gzip's FEXTRA, ZIP's local file headers).

---

## B6. Bit-Level I/O (`utils/bit_stream.py`)

- **BitWriter:** accumulates bits MSB-first into `current_byte`; when 8 bits are collected, appends to buffer. `flush()` left-shifts any remainder and zero-pads the final byte.
- **BitReader:** tracks `byte_index` and `bit_index` (0=MSB); `read_bits(n)` assembles an n-bit integer MSB-first; raises `EOFError` past the end.
- **Why needed:** Huffman codes have arbitrary length (1..255 bits theoretically); LZW codes are 9–16 bits. Byte-aligned storage would waste up to 7 bits per code.

---

## B7. Architecture & Design Patterns

```
main.py ──── dispatcher (GUI if Tkinter works, else CLI)
   ├── gui.py      Tkinter, 3 tabs (Compress / Decompress / Benchmark), threaded
   ├── cli.py      Interactive menu + argparse subcommands
   ├── benchmark.py  Test-matrix runner + table + graphs
   └── algorithms/
         ├── base.py       ABC + CompressionStats/DecompressionStats + file workflows
         ├── huffman.py    HuffmanCompressor(BaseCompressor)
         ├── rle.py        RLECompressor(BaseCompressor)
         └── lzw.py        LZWCompressor(BaseCompressor)
       utils/
         ├── file_io.py    ContainerFile.pack/unpack, SHA-256, file verification
         ├── bit_stream.py BitWriter / BitReader
         └── visualizer.py 2×2 matplotlib dashboard + pure-SVG fallback
```

**Design patterns used (good viva talking points):**
- **Template Method** — `BaseCompressor.compress_file()` defines the workflow (read → hash → compress → pack → time → write → stats); subclasses implement only `compress`/`decompress`.
- **Strategy Pattern** — the three compressors are interchangeable strategies behind a common interface.
- **Registry / Factory** — `ALGORITHM_REGISTRY` and `get_compressor_by_id/name()` (`algorithms/__init__.py:9`) decouple algorithm selection from instantiation (used by CLI auto-detection).
- **Null-object metadata** — RLE and LZW return `b""` metadata; the container handles uniformly.
- **Graceful degradation** — visualizer falls back to hand-written SVG if Matplotlib missing; `main.py` falls back to CLI if Tkinter/display unavailable (headless SSH).

---

## B8. Edge-Case Engineering (a very common viva topic)

| Edge case | Risk | Solution (with code ref) |
|---|---|---|
| 0-byte file | Division by zero, empty tree, crash | Header stores size 0; compressors return empty payload; decompressor returns `b""` immediately (`huffman.py:247`, `rle.py:104`, `lzw.py:133`) |
| Single distinct symbol (`"AAAA"`) | Huffman tree cannot split into two leaves | Dummy parent makes code `"0"`; decoder emits symbol × original_size (`huffman.py:117`, `huffman.py:260`) |
| Trailing bit padding | Huffman/LZW payloads end mid-byte; padding bits could produce extra symbols | Decoder loops until `len(output) == original_size`; extra bits discarded (`huffman.py:269`) |
| Runs > 128 in RLE | Control byte range overflow | Encoder caps run_length at 128 and starts a new chunk (`rle.py:73`) |
| KwKwK in LZW | Decoder sees undefined code | `code == len(dictionary)` → `previous + previous[0]` (`lzw.py:167`) |
| LZW dictionary growth | Unbounded memory | Hard cap 65,536 + `CLEAR_CODE` reset (`lzw.py:111`) |
| Corrupt archive | Silent data corruption | Magic/version/algo validation + SHA-256 compare (`base.py:138`, `file_io.py:98`) |
| Wrong algorithm selected | Garbage output | Header algorithm ID checked against instance (`base.py:120`) |
| Truncated metadata | Struct unpack error | Bounds check `meta_end` vs file length (`file_io.py:112`) |
| Heap tie in Huffman | Encoder/decoder trees diverge | Stable `order` tie-breaker (`huffman.py:75`) |

---

## B9. Benchmark Results & Their Interpretation

Recorded matrix (abridged; full table in README):

| Dataset | Best algorithm | Why |
|---|---|---|
| Monolithic 10 KB same byte | **RLE 48.3×** (10,240→212 B) | Perfect runs; Huffman limited by 1-symbol tree + freq table; LZW also good (27×) |
| Repetitive patterns | **LZW 7.83×** | Multi-byte phrases captured in dictionary |
| Natural prose | **LZW 2.07×**, Huffman 1.71×, RLE 0.99× | LZW captures digrams/words; Huffman exploits letter skew; RLE has nothing to compress |
| Source code | **LZW 2.87×** (65% savings) | Repeated keywords/indentation are dictionary phrases |
| Random binary | All < 1.0× (expansion) | Entropy = 8 bits/byte; only container overhead remains |
| Empty / 1-byte | Expansion (50+ B header) | Fixed 50-byte header dominates; proves no universal compressor |

**Discussion points for viva:**
1. RLE has the fastest compression (simple counter loop, no heap/hash).
2. LZW compression is slowest (hash lookups on byte-string concatenations — Python-level overhead) but decompression is fast (array indexing).
3. Huffman decompression is slower than compression when codes are long (bit-by-bit tree walking vs O(1) table lookup on encode).
4. The results validate the pigeonhole principle: high-entropy data always expands under lossless compression with metadata.
5. Container overhead (50 B fixed + metadata) explains why tiny files always "fail" to compress — an important real-world design insight (formats like gzip therefore skip incompressible members or store them raw with a flag).

---

# PART C — VIVA QUESTIONS BANK (with model answers)

---

## C1. General / Opening Questions

**Q1. What is your project about in one line?**
A: A lossless file compression tool implementing three classic algorithms — Huffman (greedy), PackBits RLE (linear scan), and LZW (adaptive dictionary) — inside a self-contained, SHA-256-verified binary container, with GUI, CLI, and benchmarking.

**Q2. What is lossless vs lossy compression? Give examples.**
A: Lossless — decompressed output is bit-identical to input (gzip, ZIP, PNG, our tool). Lossy — discards perceptually insignificant data for higher ratios (JPEG images, MP3/AAC audio, H.264 video). Lossy is acceptable for media; unacceptable for text, code, or medical/legal archives.

**Q3. Why can't one algorithm compress every file?**
A: Pigeonhole principle — there are more files of length n+1 than of length n, so any map from longer to shorter files must collide; decompression would be ambiguous. Equivalently, incompressible (high-entropy) data must be stored at ≥ its entropy rate. Empirically, our random.bin benchmarks expand under all three algorithms.

**Q4. What is entropy in information theory?**
A: Shannon entropy $H = -\sum p_i \log_2 p_i$ is the average minimum bits per symbol needed to represent a source without loss. It is the theoretical lower bound for lossless compression. Random bytes: H = 8 (incompressible); English text: ≈ 1.3–1.5 bits/char.

**Q5. What is a prefix-free (instantaneous) code and why does Huffman need it?**
A: No codeword is a prefix of another, so the bitstream can be decoded greedily without lookahead or delimiters (Kraft inequality: $\sum 2^{-l_i} \le 1$). Huffman trees are full binary trees; leaf-to-root paths are automatically prefix-free because no leaf is an ancestor of another.

**Q6. Name three different algorithmic paradigms in your project.**
A: Greedy (Huffman — proven optimal via greedy-choice property + optimal substructure), linear-time scanning (RLE), and online/adaptive dictionary construction (LZW — incremental dynamic programming over phrases).

## C2. Huffman-Specific

**Q7. Prove Huffman coding is optimal.**
A: (Give Lemmas 1 & 2 from section B2.3 — greedy choice via exchange argument, optimal substructure via contradiction, then induction on alphabet size.)

**Q8. Is Huffman optimal in all senses?**
A: It is optimal among all *prefix-free binary codes with integer lengths* (minimizes $\sum f_i l_i$). It is *not* the absolute entropy limit: arithmetic coding and range coding use fractional bit lengths and can approach H arbitrarily closely; adaptive Huffman (Vitter's D-algorithm) avoids transmitting the table.

**Q9. How does the decoder know the Huffman tree?**
A: The frequency table is serialized into the archive metadata (`2 + 5K` bytes). The decoder deserializes it and deterministically re-runs the same greedy tree construction. Tie-breaking by insertion order (`__lt__` uses `order`) guarantees encoder and decoder build identical trees even with equal frequencies.

**Q10. What happens with a file containing only one distinct character?**
A: A single-leaf tree would give an empty code. We create a dummy parent so the symbol's code is `"0"`; the decoder detects `len(freq_table)==1` and simply emits that byte `original_size` times — never reading the bitstream (which is just padding).

**Q11. Why does Huffman expand random data?**
A: For uniform byte distribution every symbol gets an 8-bit code, so payload size ≈ original size; plus the frequency table (up to 1,282 bytes) and 50-byte container header, total size grows. Also the bitstream is byte-aligned with padding.

**Q12. Time complexity of Huffman and why it is effectively linear.**
A: O(N + K log K). Counting is O(N); K−1 heap merges are O(K log K); encoding is O(N). Since K ≤ 256 for byte-level coding, K log K ≤ 256·8 = 2048 — a constant. So total time is Θ(N).

**Q13. What data structure is the min-heap and why?**
A: Python's `heapq` module — a binary min-heap giving O(1) access to the minimum and O(log K) extract-min/insert. This makes each of the K−1 merges cost O(log K). Alternatives: a sorted list (O(K²) total) or two queues (O(K)); the heap is the textbook standard.

**Q14. How many nodes does a Huffman tree have?**
A: For K leaves in a full binary tree there are exactly K−1 internal nodes, total 2K−1 ≤ 511 nodes for K = 256.

## C3. RLE-Specific

**Q15. Why not use naive RLE (count+byte always)?**
A: It doubles the size of non-repeating data (+100%). PackBits avoids this by mixing literal runs (bounded +0.78% overhead) with replicated runs, which is why TIFF, PDF (RunLengthDecode filter), and Apple formats standardized it.

**Q16. Explain the PackBits control byte encoding.**
A: Signed 8-bit N: 0..127 → next N+1 bytes are literals; −127..−1 → next byte repeated −N+1 times (2–128); −128 is a reserved no-op. Runs longer than 128 are chunked into multiple control sequences.

**Q17. What is the best and worst case for RLE?**
A: Best: 128 identical bytes → 2 bytes = 64× ratio; a 10 KB monolithic file compresses to 212 bytes (~48×) in our benchmark. Worst: no consecutive repeats → +1 byte per 128 bytes ≈ 0.78% expansion, never worse.

**Q18. Does RLE need a header/metadata?**
A: No — PackBits is self-describing: the control bytes fully determine decoding. Its metadata field is empty (`b""`), though the 50-byte container header still applies.

**Q19. Where is RLE used in the real world?**
A: TIFF (PackBits option), PDF RunLengthDecode filter, PCX, BMP RLE4/RLE8, Apple QuickDraw/PackBits, fax (modified Huffman/READ — related run-length ideas), and as a pre-pass in PAKE/gzip-like pipelines for run-heavy data.

## C4. LZW-Specific

**Q20. Explain the LZW algorithm step by step.**
A: (Encoder) Start with 256 one-byte entries; greedily extend the current phrase while it exists in the dictionary; on failure, emit the code of the current phrase and add the failed extension to the dictionary. (Decoder) Rebuild the dictionary from the code stream: each code emits its phrase and adds `previous_phrase + phrase[0]`. Dictionaries stay in sync without transmission.

**Q21. What is the KwKwK case and how do you handle it?**
A: See B4.4. When the decoder receives `code == len(dictionary)`, the missing phrase is `previous_phrase + previous_phrase[0]`; reconstruct it, output it, and add it to the dictionary as usual. Triggered by patterns like `ABABABAB`.

**Q22. Why variable bit-width in LZW?**
A: Early dictionary codes are small numbers; using 16 bits for all of them wastes space. Starting at 9 bits (enough for 0–511) and growing to 16 as the dictionary fills keeps average code length low. GIF uses the same 9→12 scheme (with an "early change" off-by-one).

**Q22b. Why must the decoder widen its code width one entry early?**
A: The decoder's dictionary always lags the encoder's by exactly one entry, because it adds the phrase for the *previous* code only after reading the next code. If both used the same threshold (`== 2^w`), the decoder would still be reading 9 bits while the encoder had already switched to 10 — desynchronizing the stream. Hence the decoder uses `len(dict) == 2^w − 1` ("early change"), which we verified with a 5,000-byte random round-trip test. TIFF's LZW variant uses the same correction.

**Q23. What is CLEAR_CODE and why reset the dictionary?**
A: A special code (256 in our format) that tells the decoder to reset its dictionary and bit width to initial state. We emit it (a) at the very start for deterministic sync and (b) when the dictionary fills (65,536 entries) to bound memory and let the encoder adapt to new data phases (like GIF's block terminator / TIFF's early-change behavior).

**Q24. Why is LZW memory O(1) asymptotically?**
A: The dictionary is hard-capped at 2^16 = 65,536 entries — a constant independent of N. So auxiliary space is Θ(1) in DAA terms, even though real memory usage is proportional to that constant.

**Q25. LZW encoder uses a hash map, decoder uses a list — why the difference?**
A: The encoder searches by *phrase* (byte strings of growing length) → hash map for O(1) lookup. The decoder receives *integer codes* → direct-indexed list/array for O(1) lookup. Both mirror each other's dictionary contents.

**Q26. Is LZW adaptive? What does that mean?**
A: Yes — it builds its model (dictionary) *while* processing the data, with no separate training/statistics pass. Huffman (as implemented here) is *static*: it needs a full frequency pre-pass and stores the table. Adaptive methods respond to local statistics and avoid transmitting models.

**Q27. Where is LZW used in practice?**
A: GIF (LZW variant), TIFF (LZW deflate-compatible variant), UNIX `compress`, PDF (optional predictor+LZW filter), and as a conceptual ancestor of LZ77/LZ78/gzip's deflate (which is LZ77+Huffman).

## C5. Container, Verification & Engineering

**Q28. Why do you store the SHA-256 hash in the header?**
A: To provide cryptographic proof that decompression is bit-for-bit lossless. A size check alone could pass while bytes differ; SHA-256 collision resistance makes silent corruption practically impossible to miss. We also offer an optional byte-by-byte file comparison as a second layer.

**Q29. Why is the original size stored?**
A: Huffman and LZW bitstreams end mid-byte; the final byte is zero-padded. Decoding by bit patterns alone could emit spurious symbols from pad bits. Stopping at exactly `original_size` bytes discards padding safely and also validates output length.

**Q30. How does the tool auto-detect which algorithm an archive used?**
A: The 6th byte of the container is the algorithm ID (1/2/3). The CLI reads the first 64 bytes, unpacks the header, looks up `ALGORITHM_REGISTRY`, and instantiates the matching decompressor — the user never has to remember which algorithm they used.

**Q31. What happens if a compressed file is corrupted?**
A: Layered defenses: (1) magic-byte mismatch → immediate error; (2) version/algorithm-ID validation; (3) metadata bounds checks; (4) size mismatch after decode → error; (5) SHA-256 mismatch → integrity failure raised before writing success. Corrupt LZW streams additionally raise "invalid code" errors.

**Q32. How do you handle empty files?**
A: `original_size = 0` in the header, empty payload; every decompressor has an early `if original_size == 0: return b""` guard. The archive still contains the 50-byte header, so empty files "expand" — consistent with compression theory.

**Q33. What is the Template Method pattern and where do you use it?**
A: A base class defines the algorithm skeleton (`compress_file`: read → hash → compress → pack → time → write → stats) and delegates the variable steps (`compress`/`decompress`) to subclasses. Used in `BaseCompressor` so Huffman/RLE/LZW share identical file I/O, timing, and verification logic without duplication.

**Q34. How do you ensure reproducible benchmarks?**
A: Random datasets use a fixed seed (`random.Random(1337)` / `Random(42)`); sample generation is deterministic; every decompression is verified with SHA-256 before being counted; temp directories isolate artifacts.

## C6. Complexity Summary (memorize this table)

| Algorithm | Compress time | Decompress time | Aux space | Metadata |
|---|---|---|---|---|
| Huffman | O(N + K log K) ≈ O(N) | O(N) bit-walks | O(K) ≤ 511 nodes | 2 + 5K bytes (≤1,282) |
| RLE (PackBits) | O(N) | O(N) | O(1) | 0 |
| LZW | O(N) amortized | O(N) | O(1) (dict ≤ 65,536) | 0 |

(N = file size in bytes, K = distinct symbols ≤ 256)

## C7. Demo Preparation — Commands to Show

```bash
# Launch GUI
python main.py

# Interactive CLI menu
python main.py --cli

# Scripted compression with each algorithm
python main.py compress -a huffman -i samples/natural_text.txt -o compressed_natural_text.txt
python main.py compress -a rle     -i samples/monolithic_same.txt -o compressed_monolithic_same.txt
python main.py compress -a lzw     -i samples/source_code.py -o compressed_source_code.py

# Decompress with automatic algorithm detection + verification against original
python main.py decompress -i compressed_natural_text.txt -o restored.txt -v samples/natural_text.txt

# Full benchmark suite + graphs
python main.py benchmark -o benchmark_results.png

# Run the test suite (16 tests)
python -m unittest test_compression.py -v

# Inspect a container header manually (hexdump first 50 bytes)
xxd -l 50 compressed_natural_text.txt
```

Expected test output: `Ran 16 tests ... OK`.

## C8. Anticipated Tricky Questions & Short Answers

| Question | Answer |
|---|---|
| Is your Huffman implementation canonical Huffman? | No — it's standard Huffman with a stored frequency table. Canonical Huffman (as in DEFLATE/JPEG) lets the decoder rebuild codes from code *lengths* only, shrinking metadata. |
| Does decompression run backwards through the tree? | No; Huffman decoding walks the tree from the root for each bit and resets to the root at each leaf. (Building codes walks from root down; decoding walks bits root-down too.) |
| Why is Huffman decompression slower than compression? | Encoding is an O(1) table lookup per byte; decoding is a bit-by-bit tree walk (O(code length) per symbol). Real systems precompute decode tables to mitigate this. |
| What is the difference between LZ77, LZ78 and LZW? | LZ77 uses a sliding window with (offset, length) pairs; LZ78 emits dictionary codes for phrases built from previous entries; LZW = LZ78 + greedy longest-match encoding by Welch, which emits fewer, longer codes. |
| Could you improve the tool? | Yes: canonical Huffman metadata, adaptive Huffman (Vitter), DEFLATE-style combination (LZ77 + Huffman), arithmetic coding to approach entropy, streaming/chunked processing, multi-threading, and a "store raw if expansion" fallback flag. |
| Why big-endian in the container? | Conventional for file formats (network byte order); `struct` format `">..."` makes it explicit and platform-independent. |
| How do you prove losslessness empirically? | Every benchmark and test decompresses the archive and compares SHA-256 digests (and optionally byte-by-byte) against the original file — 100% match required for a PASS. |
| What is the space complexity of the compressed output? | O(N) worst case for all three algorithms (nothing can exceed N + N/128 + 50 + metadata for our formats). |
| Why is Tkinter used? | It ships with Python (zero dependencies), is cross-platform, and sufficient for a desktop demo; the threaded design keeps the GUI responsive during long benchmarks. |
| What does "bit padding" mean here? | Huffman/LZW payloads may not be a multiple of 8 bits; `BitWriter.flush()` left-shifts the last partial byte and zero-fills. These pad bits are ignored because decoding stops at `original_size`. |

## C9. One-Minute Elevator Explanation (memorize)

> "This project is a lossless file compression tool built purely on the Python standard library. It implements three algorithms, each representing a different DAA paradigm: **Huffman coding**, a greedy algorithm using a min-heap that is provably optimal for prefix-free codes and exploits skewed character frequencies; **PackBits Run-Length Encoding**, a linear-time scheme that collapses byte runs while bounding worst-case expansion to under 1%; and **LZW**, an adaptive dictionary method that maps repeated multi-byte phrases to short codes without ever transmitting its dictionary, including proper handling of the classic KwKwK decoder edge case and 9-to-16-bit variable-width codes with dictionary reset. All archives use a self-contained 50-byte-header binary container embedding the algorithm ID, original size, algorithm metadata, and a SHA-256 digest that cryptographically proves bit-for-bit lossless reconstruction. The tool ships with a Tkinter GUI, an interactive and a scriptable CLI, an automated benchmark suite with visualizations, and a unittest suite covering every edge case from empty files to dictionary saturation. Our benchmarks confirm information theory: RLE wins on runs (48×), LZW wins on structured text and code, Huffman wins on natural prose, and all three expand on high-entropy random data — exactly as the pigeonhole principle predicts."

---

# PART D — QUICK REVISION CHECKLIST (before the viva)

- [ ] Can state the three algorithms + their DAA paradigms in one breath
- [ ] Can sketch the Huffman optimality proof (exchange argument + optimal substructure) on paper
- [ ] Can hand-simulate Huffman on `"banana"` and RLE PackBits on `"AAAAABBBCC"`
- [ ] Can hand-simulate LZW on `"ABABABA"` and explain the KwKwK resolution
- [ ] Knows the binary container header layout (50 bytes) field by field
- [ ] Knows all three complexity triples and why Huffman is O(N) in practice
- [ ] Knows the Shannon entropy argument and why random data expands
- [ ] Knows every edge case in B8 and where it is handled in code
- [ ] Has run `python -m unittest test_compression.py -v` (all green) and the benchmark at least once
- [ ] Has the one-minute elevator explanation memorized
