"""
Command-Line Interface (CLI) for DAA File Compression Tool.

Supports:
1. Interactive Menu Mode: Guided step-by-step terminal UI.
2. Argument Flag Mode: Direct subcommands for scripting and automation.
"""

import os
import sys
import argparse
from typing import Optional

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from algorithms import (
    HuffmanCompressor,
    RLECompressor,
    LZWCompressor,
    get_compressor_by_id,
    get_compressor_by_name,
)
from utils.file_io import ContainerFile, verify_files_identical
from benchmark import run_benchmark


def print_banner():
    banner = """
========================================================================
       LOSSLESS FILE COMPRESSION TOOL (DAA PROJECT)
       Algorithms: Huffman Coding | Run-Length (RLE) | LZW
========================================================================
"""
    print(banner)


def display_compression_stats(stats, input_path: str, output_path: str):
    print("\n" + "=" * 50)
    print("           COMPRESSION SUMMARY")
    print("=" * 50)
    print(f"Algorithm Used    : {stats.algorithm}")
    print(f"Original File     : {input_path}")
    print(f"Original Size     : {stats.original_size:,} bytes")
    print(f"Compressed File   : {output_path}")
    print(f"Compressed Size   : {stats.compressed_size:,} bytes")
    print(f"Compression Ratio : {stats.compression_ratio:.2f}x (Orig / Comp)")
    print(f"Space Savings     : {stats.space_savings:+.2f}%")
    print(f"Time Taken        : {stats.compression_time * 1000.0:.2f} ms ({stats.compression_time:.4f} s)")
    print(f"Original SHA-256  : {stats.sha256_hex}")
    print("=" * 50)


def display_decompression_stats(stats, input_path: str, output_path: str):
    print("\n" + "=" * 50)
    print("          DECOMPRESSION SUMMARY")
    print("=" * 50)
    print(f"Algorithm Used    : {stats.algorithm}")
    print(f"Archive File      : {input_path}")
    print(f"Archive Size      : {stats.compressed_size:,} bytes")
    print(f"Restored File     : {output_path}")
    print(f"Restored Size     : {stats.decompressed_size:,} bytes")
    print(f"Time Taken        : {stats.decompression_time * 1000.0:.2f} ms ({stats.decompression_time:.4f} s)")
    print(f"Restored SHA-256  : {stats.sha256_hex}")
    print(f"Integrity Check   : {'PASSED (Lossless Verified)' if stats.is_verified else 'FAILED'}")
    print(f"Details           : {stats.verification_message}")
    print("=" * 50)


def interactive_compress():
    print("\n--- COMPRESS A FILE ---")
    file_path = input("Enter path to the file you want to compress: ").strip()
    # Strip quotes if user dragged and dropped
    file_path = file_path.strip("\"'")
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return

    print("\nSelect Algorithm:")
    print("  1. Huffman Coding (Greedy min-heap priority queue)")
    print("  2. Run-Length Encoding (RLE / PackBits)")
    print("  3. LZW Compression (Dictionary-based adaptive)")
    choice = input("Enter choice (1, 2, or 3): ").strip()

    algo_map = {
        "1": HuffmanCompressor(),
        "2": RLECompressor(),
        "3": LZWCompressor(),
    }

    if choice not in algo_map:
        print("Invalid choice! Defaulting to Huffman Coding.")
        algo = HuffmanCompressor()
    else:
        algo = algo_map[choice]

    default_output = file_path + ".daac"
    out_input = input(f"Enter output compressed file path [Default: {default_output}]: ").strip().strip("\"'")
    output_path = out_input if out_input else default_output

    print(f"\nCompressing '{file_path}' using {algo.name}...")
    try:
        stats = algo.compress_file(file_path, output_path)
        display_compression_stats(stats, file_path, output_path)
        print(f"\nSuccessfully created compressed archive: {output_path}")
    except Exception as ex:
        print(f"Compression failed: {ex}")


def interactive_decompress():
    print("\n--- DECOMPRESS A FILE ---")
    archive_path = input("Enter path to compressed archive (.daac): ").strip().strip("\"'")
    if not os.path.isfile(archive_path):
        print(f"Error: File '{archive_path}' does not exist.")
        return

    # Inspect archive header automatically to detect algorithm
    try:
        with open(archive_path, "rb") as f:
            header_sample = f.read(64)
        header, _, _ = ContainerFile.unpack(header_sample + b"\x00" * 64)
        algo = get_compressor_by_id(header.algorithm_id)
        print(f"Detected archive format: Encoded with {algo.name} (Original size: {header.original_size:,} bytes)")
    except Exception as ex:
        print(f"Error inspecting archive header: {ex}")
        return

    base_name = os.path.splitext(archive_path)[0]
    default_output = base_name + ".restored"
    out_input = input(f"Enter restored file path [Default: {default_output}]: ").strip().strip("\"'")
    output_path = out_input if out_input else default_output

    verify_orig = input("Enter original file path to verify lossless match (optional, press Enter to skip): ").strip().strip("\"'")
    verify_orig = verify_orig if verify_orig else None

    print(f"\nDecompressing using {algo.name}...")
    try:
        stats = algo.decompress_file(archive_path, output_path, original_for_verify=verify_orig)
        display_decompression_stats(stats, archive_path, output_path)
        print(f"\nSuccessfully restored file: {output_path}")
    except Exception as ex:
        print(f"Decompression failed: {ex}")


def interactive_benchmark():
    print("\nLaunching benchmark matrix across test datasets...")
    out_img = os.path.join(PROJECT_ROOT, "benchmark_comparison.png")
    run_benchmark(out_img)


def interactive_menu():
    while True:
        print_banner()
        print("MAIN MENU:")
        print("  1. Compress a file")
        print("  2. Decompress a file (.daac archive)")
        print("  3. Run comprehensive benchmark & generate comparison graphs")
        print("  4. Verify two files are identical (lossless checker)")
        print("  5. Exit")
        choice = input("\nSelect an option (1-5): ").strip()

        if choice == "1":
            interactive_compress()
        elif choice == "2":
            interactive_decompress()
        elif choice == "3":
            interactive_benchmark()
        elif choice == "4":
            print("\n--- LOSSLESS INTEGRITY VERIFIER ---")
            f1 = input("Original file path: ").strip().strip("\"'")
            f2 = input("Decompressed file path: ").strip().strip("\"'")
            identical, msg = verify_files_identical(f1, f2)
            print(f"\nResult: {'PASS (100% Identical)' if identical else 'FAIL'}")
            print(f"Details: {msg}")
        elif choice == "5":
            print("Exiting. Thank you!")
            break
        else:
            print("Invalid option, please enter 1, 2, 3, 4, or 5.")

        input("\nPress Enter to return to main menu...")


def run_cli_arguments():
    parser = argparse.ArgumentParser(
        description="Lossless File Compression Tool (DAA Project) - Huffman, RLE, LZW"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Compress subcommand
    comp_parser = subparsers.add_parser("compress", help="Compress a file")
    comp_parser.add_argument("-i", "--input", required=True, help="Path to input file to compress")
    comp_parser.add_argument("-o", "--output", help="Path to output compressed archive (.daac)")
    comp_parser.add_argument(
        "-a", "--algorithm", choices=["huffman", "rle", "lzw"], default="huffman",
        help="Compression algorithm to use (default: huffman)"
    )

    # Decompress subcommand
    decomp_parser = subparsers.add_parser("decompress", help="Decompress an archive file")
    decomp_parser.add_argument("-i", "--input", required=True, help="Path to compressed archive (.daac)")
    decomp_parser.add_argument("-o", "--output", required=True, help="Path for restored output file")
    decomp_parser.add_argument("-v", "--verify", help="Path to original file to verify byte-for-byte equality")

    # Benchmark subcommand
    bench_parser = subparsers.add_parser("benchmark", help="Run benchmark on test datasets")
    bench_parser.add_argument("-o", "--graph", default="benchmark_comparison.png", help="Output graph path")

    args = parser.parse_args()

    if args.command == "compress":
        compressor = get_compressor_by_name(args.algorithm)
        output_path = args.output or (args.input + ".daac")
        print(f"Compressing '{args.input}' using {compressor.name}...")
        stats = compressor.compress_file(args.input, output_path)
        display_compression_stats(stats, args.input, output_path)

    elif args.command == "decompress":
        with open(args.input, "rb") as f:
            sample_data = f.read(64)
        header, _, _ = ContainerFile.unpack(sample_data + b"\x00" * 64)
        compressor = get_compressor_by_id(header.algorithm_id)
        print(f"Decompressing '{args.input}' using {compressor.name}...")
        stats = compressor.decompress_file(args.input, args.output, original_for_verify=args.verify)
        display_decompression_stats(stats, args.input, args.output)

    elif args.command == "benchmark":
        run_benchmark(args.graph)

    else:
        # If no arguments provided, launch interactive menu
        interactive_menu()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_cli_arguments()
    else:
        interactive_menu()
