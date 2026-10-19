"""
Benchmarking Suite for DAA File Compression Tool.

Runs all implemented algorithms (Huffman, RLE, LZW) on diverse dataset categories:
1. Highly repetitive data (e.g., long runs of identical bytes)
2. Natural English prose (skewed symbol distribution, medium entropy)
3. Source code (structured syntax, recurring keywords)
4. High-entropy pseudorandom binary (tests worst-case expansion resistance)
5. Edge cases: Single-character file, empty file

Calculates:
- Original vs. Compressed size (Bytes)
- Compression Ratio (Original / Compressed)
- Space Savings Percentage
- Execution Time for Compression & Decompression (seconds / milliseconds)
- Exact SHA-256 Bit-for-Bit Lossless Verification
- Generates comparative Matplotlib graphs (or SVG fallback)
"""

import os
import sys
import time
import random
import tempfile
from typing import List, Dict, Any

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from algorithms.huffman import HuffmanCompressor
from algorithms.rle import RLECompressor
from algorithms.lzw import LZWCompressor
from utils.visualizer import plot_benchmark_results


def ensure_benchmark_datasets(samples_dir: str) -> Dict[str, str]:
    """
    Ensures that standard benchmark datasets exist on disk.
    If missing, generates them deterministically.
    """
    os.makedirs(samples_dir, exist_ok=True)
    dataset_paths = {}

    # 1. Edge Case: Empty file (0 bytes)
    empty_path = os.path.join(samples_dir, "empty.txt")
    if not os.path.exists(empty_path):
        with open(empty_path, "wb") as f:
            pass
    dataset_paths["Empty (0 Bytes)"] = empty_path

    # 2. Edge Case: Single Character (1 byte)
    single_path = os.path.join(samples_dir, "single_char.txt")
    if not os.path.exists(single_path):
        with open(single_path, "wb") as f:
            f.write(b"A")
    dataset_paths["Single Char (1 B)"] = single_path

    # 3. Highly Repetitive Data (RLE & LZW ideal scenario)
    repetitive_path = os.path.join(samples_dir, "repetitive.txt")
    if not os.path.exists(repetitive_path):
        rep_content = (
            ("A" * 150 + "B" * 200 + "C" * 80 + "\n") * 15
            + ("REPEAT_ME_OVER_AND_OVER_PATTERN_1234567890\n" * 60)
            + ("\x00\x00\x00\x00\xFF\xFF\xFF\xFF" * 100)
        ).encode("utf-8")
        with open(repetitive_path, "wb") as f:
            f.write(rep_content)
    dataset_paths["Repetitive Data"] = repetitive_path

    # 4. Monolithic Single Byte (10 KB of identical byte)
    monolithic_path = os.path.join(samples_dir, "monolithic_same.txt")
    if not os.path.exists(monolithic_path):
        with open(monolithic_path, "wb") as f:
            f.write(b"X" * 10240)
    dataset_paths["Monolithic (10 KB)"] = monolithic_path

    # 5. Natural Language Text (English Prose - Alice in Wonderland)
    natural_path = os.path.join(samples_dir, "natural_text.txt")
    if not os.path.exists(natural_path):
        prose = """Alice was beginning to get very tired of sitting by her sister on the bank,
and of having nothing to do: once or twice she had peeped into the book her sister
was reading, but it had no pictures or conversations in it, "and what is the use of
a book," thought Alice "without pictures or conversation?"

So she was considering in her own mind (as well as she could, for the hot day made
her feel very sleepy and stupid), whether the pleasure of making a daisy-chain would
be worth the trouble of getting up and picking the daisies, when suddenly a White
Rabbit with pink eyes ran close by her.

There was nothing so very remarkable in that; nor did Alice think it so very much
out of the way to hear the Rabbit say to itself, "Oh dear! Oh dear! I shall be late!"
(when she thought it over afterwards, it occurred to her that she ought to have wondered
at this, but at the time it all seemed quite natural); but when the Rabbit actually
took a watch out of its waistcoat-pocket, and looked at it, and then hurried on,
Alice started to her feet, for it flashed across her mind that she had never before
seen a rabbit with either a waistcoat-pocket, or a watch to take out of it, and burning
with curiosity, she ran across the field after it, and fortunately was just in time to
see it pop down a large rabbit-hole under the hedge.
""" * 8
        with open(natural_path, "wb") as f:
            f.write(prose.encode("utf-8"))
    dataset_paths["Natural Prose"] = natural_path

    # 6. Source Code (Structured Python script)
    code_path = os.path.join(samples_dir, "source_code.py")
    if not os.path.exists(code_path):
        code = """
import os
import sys
import math

class PerformanceBenchmark:
    def __init__(self, name: str):
        self.name = name
        self.timestamps = []
        self.results = {}

    def log_metric(self, key: str, value: float):
        if key not in self.results:
            self.results[key] = []
        self.results[key].append(value)

    def compute_summary(self):
        output = {}
        for k, vals in self.results.items():
            mean = sum(vals) / len(vals)
            output[k] = {"mean": mean, "count": len(vals)}
        return output

def run_suite():
    bench = PerformanceBenchmark("DAA_Suite")
    for i in range(250):
        bench.log_metric("latency_ms", i * 1.5 + math.sqrt(i))
    return bench.compute_summary()
""" * 12
        with open(code_path, "wb") as f:
            f.write(code.encode("utf-8"))
    dataset_paths["Source Code"] = code_path

    # 7. High-Entropy Pseudorandom Binary (worst case)
    random_path = os.path.join(samples_dir, "random.bin")
    if not os.path.exists(random_path):
        rng = random.Random(1337)
        rand_bytes = bytes([rng.randint(0, 255) for _ in range(10240)])
        with open(random_path, "wb") as f:
            f.write(rand_bytes)
    dataset_paths["Random Binary"] = random_path

    return dataset_paths


def run_benchmark(output_image_path: str = "benchmark_comparison.png") -> List[Dict[str, Any]]:
    """
    Executes benchmark matrix: all algorithms across all test datasets.
    Prints formatted CLI tables and generates performance graphs.
    """
    samples_dir = os.path.join(PROJECT_ROOT, "samples")
    datasets = ensure_benchmark_datasets(samples_dir)

    algorithms = [
        HuffmanCompressor(),
        RLECompressor(),
        LZWCompressor(),
    ]

    all_results: List[Dict[str, Any]] = []

    print("\n" + "=" * 90)
    print("           DAA FILE COMPRESSION ALGORITHM BENCHMARK EXECUTION")
    print("=" * 90)

    header = (
        f"{'Dataset':<20} | {'Algorithm':<18} | {'Orig (B)':<9} | {'Comp (B)':<9} | "
        f"{'Ratio':<7} | {'Savings':<8} | {'Comp(ms)':<9} | {'Decomp(ms)':<10} | {'Verified':<8}"
    )
    print(header)
    print("-" * 115)

    with tempfile.TemporaryDirectory() as temp_dir:
        for label, file_path in datasets.items():
            orig_size = os.path.getsize(file_path)

            for algo in algorithms:
                comp_file = os.path.join(temp_dir, f"{os.path.basename(file_path)}.{algo.name}.daac")
                decomp_file = os.path.join(temp_dir, f"{os.path.basename(file_path)}.{algo.name}.decomp")

                try:
                    c_stats = algo.compress_file(file_path, comp_file)
                    d_stats = algo.decompress_file(comp_file, decomp_file, original_for_verify=file_path)

                    verified_str = "PASS" if d_stats.is_verified else "FAIL"
                    comp_ms = c_stats.compression_time * 1000.0
                    decomp_ms = d_stats.decompression_time * 1000.0

                    row = (
                        f"{label:<20} | {algo.name:<18} | {orig_size:<9,} | {c_stats.compressed_size:<9,} | "
                        f"{c_stats.compression_ratio:<6.2f}x | {c_stats.space_savings:>+6.1f}% | "
                        f"{comp_ms:<9.2f} | {decomp_ms:<10.2f} | {verified_str:<8}"
                    )
                    print(row)

                    all_results.append({
                        "file_name": label,
                        "algorithm": algo.name,
                        "original_size": orig_size,
                        "compressed_size": c_stats.compressed_size,
                        "compression_ratio": c_stats.compression_ratio,
                        "space_savings": c_stats.space_savings,
                        "comp_time": c_stats.compression_time,
                        "decomp_time": d_stats.decompression_time,
                        "verified": d_stats.is_verified,
                    })

                except Exception as ex:
                    print(f"{label:<20} | {algo.name:<18} | ERROR: {ex}")

            print("-" * 115)

    print("\nBenchmark tests completed across all datasets.")
    
    # Generate visualization graphs
    graph_status = plot_benchmark_results(all_results, output_image_path)
    print(f"\n[Graph Visualization] {graph_status}")

    return all_results


if __name__ == "__main__":
    out_img = os.path.join(PROJECT_ROOT, "benchmark_comparison.png")
    run_benchmark(out_img)
