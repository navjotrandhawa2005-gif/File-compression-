"""
Graph and visualization generator for compression benchmarking results.

Generates:
1. Compression Ratio comparison bar chart.
2. Compression & Decompression Time comparison charts.
3. Space Savings (%) comparison chart.
4. Comprehensive multi-panel performance dashboard.

Supports Matplotlib with graceful ASCII/SVG fallback if Matplotlib is missing.
"""

import os
from typing import List, Dict, Any


def plot_benchmark_results(results: List[Dict[str, Any]], output_path: str = "benchmark_comparison.png") -> str:
    """
    Plots benchmark comparisons across algorithms and file types.
    
    Args:
        results: List of result dictionaries containing:
                 'file_name', 'algorithm', 'original_size', 'compressed_size',
                 'compression_ratio', 'space_savings', 'comp_time', 'decomp_time'
        output_path: Path to save the resulting image (e.g., .png)

    Returns:
        Status message with the path to the saved graph.
    """
    try:
        import matplotlib
        # Use Agg backend for non-interactive / headless script execution
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        # Fallback to generating an SVG chart directly
        return _generate_svg_fallback(results, output_path.replace(".png", ".svg"))

    # Extract unique files and algorithms
    files = list(dict.fromkeys(r["file_name"] for r in results))
    algorithms = list(dict.fromkeys(r["algorithm"] for r in results))

    if not files or not algorithms:
        return "No benchmark data available to plot."

    # Setup 2x2 multi-panel figure
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("DAA File Compression Algorithm Benchmark Analysis", fontsize=16, fontweight="bold", y=0.98)

    palette = ["#2563EB", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"]
    algo_colors = {algo: palette[i % len(palette)] for i, algo in enumerate(algorithms)}

    x = np.arange(len(files))
    bar_width = 0.8 / len(algorithms)

    # 1. Compression Ratio
    ax1 = axes[0, 0]
    for i, algo in enumerate(algorithms):
        ratios = [
            next((r["compression_ratio"] for r in results if r["file_name"] == f and r["algorithm"] == algo), 0)
            for f in files
        ]
        offsets = x - 0.4 + (i + 0.5) * bar_width
        bars = ax1.bar(offsets, ratios, bar_width, label=algo, color=algo_colors[algo], alpha=0.9)
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax1.annotate(f"{height:.2f}x",
                             xy=(bar.get_x() + bar.get_width() / 2, height),
                             xytext=(0, 3), textcoords="offset points",
                             ha="center", va="bottom", fontsize=8, rotation=0)

    ax1.set_title("Compression Ratio (Original / Compressed) [Higher is Better]", fontweight="semibold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(files, rotation=15, ha="right", fontsize=9)
    ax1.axhline(1.0, color="gray", linestyle="--", linewidth=1, alpha=0.7, label="Baseline (1.0x)")
    ax1.set_ylabel("Ratio")
    ax1.grid(axis="y", linestyle=":", alpha=0.6)
    ax1.legend(loc="upper right", fontsize=8)

    # 2. Space Savings (%)
    ax2 = axes[0, 1]
    for i, algo in enumerate(algorithms):
        savings = [
            next((r["space_savings"] for r in results if r["file_name"] == f and r["algorithm"] == algo), 0)
            for f in files
        ]
        offsets = x - 0.4 + (i + 0.5) * bar_width
        bars = ax2.bar(offsets, savings, bar_width, label=algo, color=algo_colors[algo], alpha=0.9)
        for bar in bars:
            height = bar.get_height()
            ax2.annotate(f"{height:+.1f}%",
                         xy=(bar.get_x() + bar.get_width() / 2, max(0, height)),
                         xytext=(0, 3 if height >= 0 else -10), textcoords="offset points",
                         ha="center", va="bottom" if height >= 0 else "top", fontsize=8)

    ax2.set_title("Space Savings % ((1 - Comp/Orig) * 100) [Higher is Better]", fontweight="semibold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(files, rotation=15, ha="right", fontsize=9)
    ax2.axhline(0, color="black", linestyle="-", linewidth=0.8)
    ax2.set_ylabel("Savings (%)")
    ax2.grid(axis="y", linestyle=":", alpha=0.6)
    ax2.legend(loc="upper right", fontsize=8)

    # 3. Compression Time (ms)
    ax3 = axes[1, 0]
    for i, algo in enumerate(algorithms):
        comp_times = [
            next((r["comp_time"] * 1000 for r in results if r["file_name"] == f and r["algorithm"] == algo), 0)
            for f in files
        ]
        offsets = x - 0.4 + (i + 0.5) * bar_width
        ax3.bar(offsets, comp_times, bar_width, label=algo, color=algo_colors[algo], alpha=0.9)

    ax3.set_title("Compression Time (ms) [Lower is Faster]", fontweight="semibold")
    ax3.set_xticks(x)
    ax3.set_xticklabels(files, rotation=15, ha="right", fontsize=9)
    ax3.set_ylabel("Time (milliseconds)")
    ax3.grid(axis="y", linestyle=":", alpha=0.6)
    ax3.legend(loc="upper right", fontsize=8)

    # 4. Decompression Time (ms)
    ax4 = axes[1, 1]
    for i, algo in enumerate(algorithms):
        decomp_times = [
            next((r["decomp_time"] * 1000 for r in results if r["file_name"] == f and r["algorithm"] == algo), 0)
            for f in files
        ]
        offsets = x - 0.4 + (i + 0.5) * bar_width
        ax4.bar(offsets, decomp_times, bar_width, label=algo, color=algo_colors[algo], alpha=0.9)

    ax4.set_title("Decompression Time (ms) [Lower is Faster]", fontweight="semibold")
    ax4.set_xticks(x)
    ax4.set_xticklabels(files, rotation=15, ha="right", fontsize=9)
    ax4.set_ylabel("Time (milliseconds)")
    ax4.grid(axis="y", linestyle=":", alpha=0.6)
    ax4.legend(loc="upper right", fontsize=8)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()

    return f"Graph successfully generated and saved to: {output_path}"


def _generate_svg_fallback(results: List[Dict[str, Any]], svg_path: str) -> str:
    """
    Pure-Python standalone SVG graph generator in case matplotlib is absent.
    Ensures the user ALWAYS gets a visual vector chart regardless of dependencies!
    """
    files = list(dict.fromkeys(r["file_name"] for r in results))
    algorithms = list(dict.fromkeys(r["algorithm"] for r in results))
    palette = ["#2563EB", "#10B981", "#F59E0B", "#EF4444"]

    width = 900
    height = 500
    svg = [
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" style="background:#0F172A;font-family:sans-serif;">',
        '<text x="450" y="35" text-anchor="middle" fill="#F8FAFC" font-size="18" font-weight="bold">DAA File Compression Algorithm Benchmark (Compression Ratio)</text>',
    ]

    # Legend
    for idx, algo in enumerate(algorithms):
        color = palette[idx % len(palette)]
        lx = 200 + idx * 180
        svg.append(f'<rect x="{lx}" y="55" width="14" height="14" fill="{color}" rx="3"/>')
        svg.append(f'<text x="{lx + 20}" y="67" fill="#E2E8F0" font-size="12">{algo}</text>')

    # Chart Area
    origin_x = 100
    origin_y = 400
    plot_width = 720
    plot_height = 300

    max_ratio = max(max(r.get("compression_ratio", 1.0) for r in results), 2.0)
    
    # Baseline line (1.0x)
    baseline_y = origin_y - (1.0 / max_ratio) * plot_height
    svg.append(f'<line x1="{origin_x}" y1="{baseline_y}" x2="{origin_x + plot_width}" y2="{baseline_y}" stroke="#64748B" stroke-dasharray="4" stroke-width="1.5"/>')
    svg.append(f'<text x="{origin_x - 10}" y="{baseline_y + 4}" fill="#94A3B8" font-size="10" text-anchor="end">1.0x</text>')

    group_width = plot_width / max(1, len(files))
    bar_width = (group_width * 0.7) / max(1, len(algorithms))

    for f_idx, f_name in enumerate(files):
        gx = origin_x + f_idx * group_width + (group_width * 0.15)
        for a_idx, algo in enumerate(algorithms):
            match = next((r for r in results if r["file_name"] == f_name and r["algorithm"] == algo), None)
            ratio = match["compression_ratio"] if match else 0
            bh = (ratio / max_ratio) * plot_height
            bx = gx + a_idx * bar_width
            by = origin_y - bh
            color = palette[a_idx % len(palette)]
            svg.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_width-2:.1f}" height="{bh:.1f}" fill="{color}" rx="2"/>')
            if ratio > 0:
                svg.append(f'<text x="{bx + bar_width/2:.1f}" y="{by - 4:.1f}" fill="#F8FAFC" font-size="9" text-anchor="middle">{ratio:.2f}x</text>')

        # File label
        svg.append(f'<text x="{gx + (group_width * 0.35):.1f}" y="{origin_y + 25}" fill="#CBD5E1" font-size="11" text-anchor="middle">{f_name}</text>')

    svg.append('</svg>')
    
    os.makedirs(os.path.dirname(os.path.abspath(svg_path)), exist_ok=True)
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))

    return f"SVG Benchmark graph generated and saved to: {svg_path}"
