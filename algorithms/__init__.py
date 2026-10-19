"""
Compression Algorithms package.
"""
from algorithms.base import BaseCompressor, CompressionStats, DecompressionStats
from algorithms.huffman import HuffmanCompressor
from algorithms.rle import RLECompressor
from algorithms.lzw import LZWCompressor

ALGORITHM_REGISTRY = {
    1: HuffmanCompressor,
    2: RLECompressor,
    3: LZWCompressor,
}

ALGORITHM_CHOICES = {
    "huffman": HuffmanCompressor,
    "rle": RLECompressor,
    "lzw": LZWCompressor,
}

def get_compressor_by_id(algo_id: int) -> BaseCompressor:
    """Instantiate compressor by its numeric algorithm ID."""
    if algo_id not in ALGORITHM_REGISTRY:
        raise ValueError(f"Unknown algorithm ID: {algo_id}. Valid: {list(ALGORITHM_REGISTRY.keys())}")
    return ALGORITHM_REGISTRY[algo_id]()

def get_compressor_by_name(name: str) -> BaseCompressor:
    """Instantiate compressor by string name ('huffman', 'rle', 'lzw')."""
    key = name.strip().lower()
    if key not in ALGORITHM_CHOICES:
        raise ValueError(f"Unknown algorithm name '{name}'. Choose from: {list(ALGORITHM_CHOICES.keys())}")
    return ALGORITHM_CHOICES[key]()

__all__ = [
    "BaseCompressor",
    "CompressionStats",
    "DecompressionStats",
    "HuffmanCompressor",
    "RLECompressor",
    "LZWCompressor",
    "ALGORITHM_REGISTRY",
    "ALGORITHM_CHOICES",
    "get_compressor_by_id",
    "get_compressor_by_name",
]
