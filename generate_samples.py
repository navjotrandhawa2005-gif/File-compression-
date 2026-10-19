"""
Sample files generator for compression benchmark testing.

Creates diverse datasets representing distinct entropy levels:
1. Empty file (0 bytes) - Extreme edge case
2. Single-byte file (1 byte) - Minimal tree/stream edge case
3. Monolithic single-character file (10 KB of identical 'A's) - RLE best case
4. Structured repetitive file (15 KB of patterned sequences) - RLE & LZW showcase
5. Natural English text (12 KB of Alice in Wonderland) - Huffman & LZW realistic case
6. High-Entropy Pseudorandom file (10 KB of uniform random bytes) - Incompressible worst case
7. Source code sample (8 KB of structured Python code) - Realistic code benchmark
"""

import os
import random


def generate_all_samples(samples_dir: str) -> None:
    os.makedirs(samples_dir, exist_ok=True)

    # 1. Empty file
    with open(os.path.join(samples_dir, "empty.txt"), "wb") as f:
        f.write(b"")

    # 2. Single-byte file
    with open(os.path.join(samples_dir, "single_char.txt"), "wb") as f:
        f.write(b"A")

    # 3. Monolithic repetitive file (10,000 'Z' characters)
    with open(os.path.join(samples_dir, "monolithic_same.txt"), "wb") as f:
        f.write(b"Z" * 10240)

    # 4. Structured repetitive data (blocks of runs and repeated phrases)
    repetitive_text = (
        ("AAAAA" * 20 + "BBBBBB" * 30 + "CCCCCCC" * 40 + "\n") * 10
        + ("THE_QUICK_BROWN_FOX_JUMPS_OVER_THE_LAZY_DOG\n" * 50)
        + ("0101010101010101010101010101010101010101\n" * 40)
    ).encode("utf-8")
    with open(os.path.join(samples_dir, "repetitive.txt"), "wb") as f:
        f.write(repetitive_text)

    # 5. Natural English text (Alice in Wonderland excerpt)
    natural_text = """Alice was beginning to get very tired of sitting by her sister on the bank,
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

In another moment down went Alice after it, never once considering in the world how in
the world she was to get out again. The rabbit-hole went straight on like a tunnel for
some way, and then dipped suddenly down, so suddenly that Alice had not a moment to
think about stopping herself before she found herself falling down a very deep well.

Either the well was very deep, or she fell very slowly, for she had plenty of time as
she went down to look about her and to wonder what was going to happen next. First, she
tried to look down and make out what she was coming to, but it was too dark to see
anything; then she looked at the sides of the well, and noticed that they were filled
with cupboards and book-shelves; here and there she saw maps and pictures hung upon pegs.
She took down a jar from one of the shelves as she passed; it was labelled "ORANGE
MARMALADE", but to her great disappointment it was empty: she did not like to drop the
jar for fear of killing somebody underneath, so managed to put it into one of the
cupboards as she fell past it.

"Well!" thought Alice to herself, "after such a fall as this, I shall think nothing of
tumbling down stairs! How brave they'll all think me at home! Why, I wouldn't say
anything about it, even if I fell off the top of the house!" (Which was very likely true.)
""" * 4  # Repeat to make realistic ~10KB file
    with open(os.path.join(samples_dir, "natural_text.txt"), "wb") as f:
        f.write(natural_text.encode("utf-8"))

    # 6. High-Entropy Pseudorandom file (uniform byte distribution 0-255)
    rng = random.Random(42)  # Deterministic seed for reproducible benchmarks
    random_bytes = bytes([rng.randint(0, 255) for _ in range(10240)])
    with open(os.path.join(samples_dir, "random.bin"), "wb") as f:
        f.write(random_bytes)

    # 7. Source code sample
    source_code = """
import sys
import os
import math

class DataAnalyzer:
    def __init__(self, dataset_name):
        self.dataset_name = dataset_name
        self.records = []
        self.summary_cache = {}

    def insert_record(self, record_id, metrics):
        self.records.append({"id": record_id, "metrics": metrics})

    def calculate_statistics(self):
        if not self.records:
            return None
        total = sum(r["metrics"] for r in self.records)
        mean = total / len(self.records)
        variance = sum((r["metrics"] - mean) ** 2 for r in self.records) / len(self.records)
        std_dev = math.sqrt(variance)
        return {"mean": mean, "variance": variance, "std_dev": std_dev}

def main():
    analyzer = DataAnalyzer("Benchmark_Run")
    for i in range(500):
        analyzer.insert_record(i, i * 2.5 + 1.2)
    stats = analyzer.calculate_statistics()
    print("Execution completed successfully:", stats)

if __name__ == "__main__":
    main()
""" * 8
    with open(os.path.join(samples_dir, "source_code.py"), "wb") as f:
        f.write(source_code.encode("utf-8"))


if __name__ == "__main__":
    target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
    generate_all_samples(target_dir)
    print(f"Sample test files created in: {target_dir}")
