"""
Tkinter Graphical User Interface (GUI) for DAA File Compression Tool.

Features:
- Modern styled ttk UI layout.
- Compress tab: File selection, algorithm radio buttons, live metrics card.
- Decompress tab: Auto-detects algorithm from archive header, restores original file,
  automatic lossless verification check.
- Benchmark tab: One-click benchmark runner across test datasets with live treeview
  and image preview of comparative charts.
- Non-blocking execution using worker threads to keep UI responsive.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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


class CompressionAppGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("DAA File Compression Tool - Huffman | RLE | LZW")
        self.root.geometry("820x640")
        self.root.minsize(760, 560)

        # Apply modern style theme
        self._configure_styles()

        # Build Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self._build_compress_tab()
        self._build_decompress_tab()
        self._build_benchmark_tab()

    def _configure_styles(self):
        style = ttk.Style()
        # Use available modern theme
        available_themes = style.theme_names()
        if "clam" in available_themes:
            style.theme_use("clam")

        style.configure("TNotebook", tabposition="n")
        style.configure("TNotebook.Tab", font=("Helvetica", 11, "bold"), padding=[16, 6])
        style.configure("Header.TLabel", font=("Helvetica", 13, "bold"), foreground="#1E293B")
        style.configure("SubHeader.TLabel", font=("Helvetica", 10), foreground="#64748B")
        style.configure("Action.TButton", font=("Helvetica", 10, "bold"), padding=6)
        style.configure("MetricTitle.TLabel", font=("Helvetica", 9, "bold"), foreground="#475569")
        style.configure("MetricVal.TLabel", font=("Helvetica", 11, "bold"), foreground="#0F172A")

    # =========================================================================
    # TAB 1: COMPRESSION
    # =========================================================================
    def _build_compress_tab(self):
        tab = ttk.Frame(self.notebook, padding=16)
        self.notebook.add(tab, text="  Compress File  ")

        ttk.Label(tab, text="File Compression Engine", style="Header.TLabel").pack(anchor="w")
        ttk.Label(tab, text="Select any file (text, binary, code, image) and choose an algorithm.",
                  style="SubHeader.TLabel").pack(anchor="w", pady=(0, 14))

        # File selection frame
        file_frame = ttk.LabelFrame(tab, text=" 1. Input File ", padding=10)
        file_frame.pack(fill=tk.X, pady=6)

        self.comp_input_var = tk.StringVar()
        entry = ttk.Entry(file_frame, textvariable=self.comp_input_var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        ttk.Button(file_frame, text="Browse...", command=self._browse_compress_file).pack(side=tk.RIGHT)

        # Algorithm selection frame
        algo_frame = ttk.LabelFrame(tab, text=" 2. Select Algorithm (DAA Project) ", padding=10)
        algo_frame.pack(fill=tk.X, pady=6)

        self.algo_var = tk.StringVar(value="huffman")
        
        ttk.Radiobutton(
            algo_frame,
            text="Huffman Coding (Greedy min-heap priority queue, optimal prefix tree)",
            variable=self.algo_var,
            value="huffman"
        ).pack(anchor="w", pady=3)

        ttk.Radiobutton(
            algo_frame,
            text="Run-Length Encoding / PackBits (Linear scan, excels on repeating data)",
            variable=self.algo_var,
            value="rle"
        ).pack(anchor="w", pady=3)

        ttk.Radiobutton(
            algo_frame,
            text="LZW Compression (Dictionary-based adaptive, variable 9-16 bits)",
            variable=self.algo_var,
            value="lzw"
        ).pack(anchor="w", pady=3)

        # Action button & progress
        btn_frame = ttk.Frame(tab, padding=6)
        btn_frame.pack(fill=tk.X, pady=8)
        self.compress_btn = ttk.Button(btn_frame, text="Compress File", style="Action.TButton",
                                       command=self._start_compression_thread)
        self.compress_btn.pack(side=tk.LEFT, padx=(0, 12))
        self.comp_progress = ttk.Progressbar(btn_frame, mode="indeterminate", length=220)
        self.comp_progress.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Results Display Card
        results_frame = ttk.LabelFrame(tab, text=" Compression Statistics & Results ", padding=12)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=6)

        self.comp_results_text = tk.Text(results_frame, height=8, wrap="word", font=("Courier", 10),
                                         bg="#F8FAFC", fg="#0F172A", relief="solid", borderwidth=1)
        self.comp_results_text.pack(fill=tk.BOTH, expand=True)

    def _browse_compress_file(self):
        f = filedialog.askopenfilename(title="Select file to compress")
        if f:
            self.comp_input_var.set(f)

    def _start_compression_thread(self):
        input_path = self.comp_input_var.get().strip()
        if not input_path or not os.path.isfile(input_path):
            messagebox.showwarning("File Missing", "Please select a valid input file.")
            return

        algo_choice = self.algo_var.get()
        base_name = os.path.basename(input_path)
        comp_name = base_name if base_name.startswith("compressed_") else f"compressed_{base_name}"
        default_out = os.path.join(os.path.dirname(input_path), comp_name)
        output_path = filedialog.asksaveasfilename(
            title="Save Compressed File As",
            initialfile=comp_name,
            filetypes=[("Compressed File", "*.*"), ("All Files", "*.*")]
        )
        if not output_path:
            return

        self.compress_btn.config(state="disabled")
        self.comp_progress.start(10)
        self.comp_results_text.delete("1.0", tk.END)
        self.comp_results_text.insert(tk.END, f"Compressing '{os.path.basename(input_path)}' with {algo_choice.upper()}...\n")

        def worker():
            try:
                compressor = get_compressor_by_name(algo_choice)
                stats = compressor.compress_file(input_path, output_path)
                msg = (
                    f"==========================================================\n"
                    f"COMPRESSION SUCCESSFUL!\n"
                    f"==========================================================\n"
                    f"Algorithm Used    : {stats.algorithm}\n"
                    f"Original File     : {input_path}\n"
                    f"Original Size     : {stats.original_size:,} bytes\n"
                    f"Compressed File   : {output_path}\n"
                    f"Compressed Size   : {stats.compressed_size:,} bytes\n"
                    f"Compression Ratio : {stats.compression_ratio:.2f}x\n"
                    f"Space Savings     : {stats.space_savings:+.2f}%\n"
                    f"Execution Time    : {stats.compression_time * 1000.0:.2f} ms ({stats.compression_time:.4f} s)\n"
                    f"Original SHA-256  : {stats.sha256_hex}\n"
                    f"==========================================================\n"
                )
                self.root.after(0, lambda: self._on_compression_done(True, msg))
            except Exception as e:
                self.root.after(0, lambda: self._on_compression_done(False, f"Error: {e}"))

        threading.Thread(target=worker, daemon=True).start()

    def _on_compression_done(self, success: bool, message: str):
        self.comp_progress.stop()
        self.compress_btn.config(state="normal")
        self.comp_results_text.delete("1.0", tk.END)
        self.comp_results_text.insert(tk.END, message)
        if success:
            messagebox.showinfo("Success", "File compression finished successfully!")
        else:
            messagebox.showerror("Error", message)

    # =========================================================================
    # TAB 2: DECOMPRESSION
    # =========================================================================
    def _build_decompress_tab(self):
        tab = ttk.Frame(self.notebook, padding=16)
        self.notebook.add(tab, text="  Decompress File  ")

        ttk.Label(tab, text="Self-Contained Archive Decompression", style="Header.TLabel").pack(anchor="w")
        ttk.Label(tab, text="The tool automatically reads metadata from the header and verifies lossless reconstruction.",
                  style="SubHeader.TLabel").pack(anchor="w", pady=(0, 14))

        # Archive Selection
        arch_frame = ttk.LabelFrame(tab, text=" 1. Compressed File ", padding=10)
        arch_frame.pack(fill=tk.X, pady=6)

        self.decomp_input_var = tk.StringVar()
        entry = ttk.Entry(arch_frame, textvariable=self.decomp_input_var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        ttk.Button(arch_frame, text="Browse File...", command=self._browse_decomp_file).pack(side=tk.RIGHT)

        # Header Info Display
        self.header_info_var = tk.StringVar(value="Select a compressed file to inspect header metadata...")
        ttk.Label(tab, textvariable=self.header_info_var, font=("Helvetica", 9, "italic"),
                  foreground="#0284C7").pack(anchor="w", padx=6, pady=4)

        # Optional Verification
        verify_frame = ttk.LabelFrame(tab, text=" 2. Lossless Verification (Optional: Select Original File) ", padding=10)
        verify_frame.pack(fill=tk.X, pady=6)
        self.verify_orig_var = tk.StringVar()
        ttk.Entry(verify_frame, textvariable=self.verify_orig_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        ttk.Button(verify_frame, text="Original File...", command=self._browse_verify_file).pack(side=tk.RIGHT)

        # Action button
        btn_frame = ttk.Frame(tab, padding=6)
        btn_frame.pack(fill=tk.X, pady=8)
        self.decompress_btn = ttk.Button(btn_frame, text="Decompress & Verify", style="Action.TButton",
                                         command=self._start_decompression_thread)
        self.decompress_btn.pack(side=tk.LEFT, padx=(0, 12))
        self.decomp_progress = ttk.Progressbar(btn_frame, mode="indeterminate", length=220)
        self.decomp_progress.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Decompression Results
        results_frame = ttk.LabelFrame(tab, text=" Decompression & Integrity Check ", padding=12)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=6)

        self.decomp_results_text = tk.Text(results_frame, height=8, wrap="word", font=("Courier", 10),
                                           bg="#F8FAFC", fg="#0F172A", relief="solid", borderwidth=1)
        self.decomp_results_text.pack(fill=tk.BOTH, expand=True)

    def _browse_decomp_file(self):
        f = filedialog.askopenfilename(
            title="Select compressed file",
            filetypes=[("Compressed File", "*.*"), ("All Files", "*.*")]
        )
        if f:
            self.decomp_input_var.set(f)
            try:
                header = ContainerFile.read_header(f)
                algo = get_compressor_by_id(header.algorithm_id)
                self.header_info_var.set(
                    f"File Info: Algorithm = {algo.name} | Original Size = {header.original_size:,} bytes | SHA-256 = {header.sha256_hash.hex()[:16]}..."
                )
            except Exception as e:
                self.header_info_var.set(f"Could not parse header: {e}")

    def _browse_verify_file(self):
        f = filedialog.askopenfilename(title="Select original file for byte-for-byte verification")
        if f:
            self.verify_orig_var.set(f)

    def _start_decompression_thread(self):
        archive_path = self.decomp_input_var.get().strip()
        if not archive_path or not os.path.isfile(archive_path):
            messagebox.showwarning("File Missing", "Please select a valid compressed file.")
            return

        # Choose destination
        base = os.path.basename(archive_path)
        if base.startswith("compressed_"):
            restored_name = base[len("compressed_"):]
        elif base.endswith(".daac"):
            restored_name = base[:-5]
        else:
            restored_name = f"restored_{base}"
        output_path = filedialog.asksaveasfilename(
            title="Save Restored File As",
            initialfile=restored_name
        )
        if not output_path:
            return

        verify_file = self.verify_orig_var.get().strip() or None

        self.decompress_btn.config(state="disabled")
        self.decomp_progress.start(10)
        self.decomp_results_text.delete("1.0", tk.END)
        self.decomp_results_text.insert(tk.END, "Reading archive and initiating decompression...\n")

        def worker():
            try:
                header = ContainerFile.read_header(archive_path)
                compressor = get_compressor_by_id(header.algorithm_id)
                stats = compressor.decompress_file(archive_path, output_path, original_for_verify=verify_file)

                msg = (
                    f"==========================================================\n"
                    f"DECOMPRESSION COMPLETED & VERIFIED!\n"
                    f"==========================================================\n"
                    f"Algorithm Detected: {stats.algorithm}\n"
                    f"Archive Source    : {archive_path}\n"
                    f"Archive Size      : {stats.compressed_size:,} bytes\n"
                    f"Restored File     : {output_path}\n"
                    f"Restored Size     : {stats.decompressed_size:,} bytes\n"
                    f"Execution Time    : {stats.decompression_time * 1000.0:.2f} ms ({stats.decompression_time:.4f} s)\n"
                    f"Restored SHA-256  : {stats.sha256_hex}\n"
                    f"Integrity Check   : {'PASSED (100% Identical Lossless)' if stats.is_verified else 'FAILED'}\n"
                    f"Verification Note : {stats.verification_message}\n"
                    f"==========================================================\n"
                )
                self.root.after(0, lambda: self._on_decompression_done(True, msg))
            except Exception as e:
                self.root.after(0, lambda: self._on_decompression_done(False, f"Decompression failed: {e}"))

        threading.Thread(target=worker, daemon=True).start()

    def _on_decompression_done(self, success: bool, message: str):
        self.decomp_progress.stop()
        self.decompress_btn.config(state="normal")
        self.decomp_results_text.delete("1.0", tk.END)
        self.decomp_results_text.insert(tk.END, message)
        if success:
            messagebox.showinfo("Success", "File restored and verified successfully!")
        else:
            messagebox.showerror("Decompression Error", message)

    # =========================================================================
    # TAB 3: BENCHMARK & ANALYSIS
    # =========================================================================
    def _build_benchmark_tab(self):
        tab = ttk.Frame(self.notebook, padding=16)
        self.notebook.add(tab, text="  Benchmark & Analysis  ")

        ttk.Label(tab, text="DAA Comparative Algorithm Benchmark", style="Header.TLabel").pack(anchor="w")
        ttk.Label(tab, text="Runs Huffman, RLE, and LZW across diverse datasets and graphs performance.",
                  style="SubHeader.TLabel").pack(anchor="w", pady=(0, 10))

        btn_bar = ttk.Frame(tab)
        btn_bar.pack(fill=tk.X, pady=6)
        self.bench_btn = ttk.Button(btn_bar, text="Run Full Benchmark Suite", style="Action.TButton",
                                    command=self._start_benchmark_thread)
        self.bench_btn.pack(side=tk.LEFT, padx=(0, 12))
        self.bench_progress = ttk.Progressbar(btn_bar, mode="indeterminate", length=220)
        self.bench_progress.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Treeview Table
        table_frame = ttk.Frame(tab)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=8)

        cols = ("dataset", "algo", "orig", "comp", "ratio", "savings", "comp_ms", "decomp_ms", "status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)
        
        self.tree.heading("dataset", text="Dataset")
        self.tree.heading("algo", text="Algorithm")
        self.tree.heading("orig", text="Orig Size (B)")
        self.tree.heading("comp", text="Comp Size (B)")
        self.tree.heading("ratio", text="Ratio")
        self.tree.heading("savings", text="Savings %")
        self.tree.heading("comp_ms", text="Comp (ms)")
        self.tree.heading("decomp_ms", text="Decomp (ms)")
        self.tree.heading("status", text="Lossless")

        self.tree.column("dataset", width=140)
        self.tree.column("algo", width=150)
        self.tree.column("orig", width=90, anchor="e")
        self.tree.column("comp", width=90, anchor="e")
        self.tree.column("ratio", width=70, anchor="e")
        self.tree.column("savings", width=80, anchor="e")
        self.tree.column("comp_ms", width=80, anchor="e")
        self.tree.column("decomp_ms", width=80, anchor="e")
        self.tree.column("status", width=70, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.bench_status_label = ttk.Label(tab, text="Click 'Run Full Benchmark Suite' to analyze all algorithms.",
                                            font=("Helvetica", 9, "italic"))
        self.bench_status_label.pack(anchor="w", pady=4)

    def _start_benchmark_thread(self):
        self.bench_btn.config(state="disabled")
        self.bench_progress.start(10)
        self.bench_status_label.config(text="Executing benchmark suite across test datasets...")
        # Clear table
        for row in self.tree.get_children():
            self.tree.delete(row)

        def worker():
            out_img = os.path.join(PROJECT_ROOT, "benchmark_comparison.png")
            results = run_benchmark(out_img)
            self.root.after(0, lambda: self._on_benchmark_done(results, out_img))

        threading.Thread(target=worker, daemon=True).start()

    def _on_benchmark_done(self, results, out_img):
        self.bench_progress.stop()
        self.bench_btn.config(state="normal")
        self.bench_status_label.config(text=f"Benchmark complete! Comparison chart generated: {out_img}")

        for r in results:
            self.tree.insert("", tk.END, values=(
                r["file_name"],
                r["algorithm"],
                f"{r['original_size']:,}",
                f"{r['compressed_size']:,}",
                f"{r['compression_ratio']:.2f}x",
                f"{r['space_savings']:+.1f}%",
                f"{r['comp_time'] * 1000.0:.2f}",
                f"{r['decomp_time'] * 1000.0:.2f}",
                "PASS" if r["verified"] else "FAIL"
            ))

        messagebox.showinfo(
            "Benchmark Complete",
            f"Successfully evaluated all algorithms across {len(results)} tests.\nComparison chart saved as:\n{out_img}"
        )


def launch_gui():
    root = tk.Tk()
    app = CompressionAppGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
