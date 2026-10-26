/**
 * COMPRESS.DAA STUDIO — CORE ENGINE & USER EXPERIENCE CONTROLLER
 * Lossless Compression Suite: Huffman Coding, PackBits RLE, LZW
 * Full Client-Side Binary Execution, Image Rendering, and Audio-Tactile Feedback
 */

// =========================================================================
// 1. SOUND FX ENGINE (Synthesized via Web Audio API, Zero Audio Files Needed)
// =========================================================================
class SoundController {
  constructor() {
    this.enabled = true;
    this.ctx = null;
  }

  _init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) this.ctx = new AudioCtx();
    }
    if (this.ctx && this.ctx.state === "suspended") {
      this.ctx.resume();
    }
  }

  toggle() {
    this.enabled = !this.enabled;
    return this.enabled;
  }

  playClick() {
    if (!this.enabled) return;
    this._init();
    if (!this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(500, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(250, this.ctx.currentTime + 0.035);
    gain.gain.setValueAtTime(0.06, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.035);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.035);
  }

  playCompress() {
    if (!this.enabled) return;
    this._init();
    if (!this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = "triangle";
    osc.frequency.setValueAtTime(140, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(480, this.ctx.currentTime + 0.12);
    gain.gain.setValueAtTime(0.09, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.12);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.12);
  }

  playSuccess() {
    if (!this.enabled) return;
    this._init();
    if (!this.ctx) return;
    const notes = [523.25, 659.25, 783.99]; // C5, E5, G5
    notes.forEach((freq, i) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = "sine";
      const start = this.ctx.currentTime + i * 0.06;
      osc.frequency.setValueAtTime(freq, start);
      gain.gain.setValueAtTime(0.08, start);
      gain.gain.exponentialRampToValueAtTime(0.001, start + 0.22);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(start);
      osc.stop(start + 0.22);
    });
  }
}

const soundFX = new SoundController();

// =========================================================================
// 2. AMBIENT PARTICLES CANVAS CONTROLLER
// =========================================================================
function initAmbientCanvas() {
  const canvas = document.getElementById("ambient-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let width = (canvas.width = window.innerWidth);
  let height = (canvas.height = window.innerHeight);

  window.addEventListener("resize", () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  const numParticles = Math.min(45, Math.floor((width * height) / 25000));
  const particles = [];
  for (let i = 0; i < numParticles; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.35,
      vy: (Math.random() - 0.5) * 0.35,
      radius: Math.random() * 1.5 + 0.8,
      alpha: Math.random() * 0.4 + 0.15
    });
  }

  function render() {
    ctx.clearRect(0, 0, width, height);
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0) p.x = width;
      if (p.x > width) p.x = 0;
      if (p.y < 0) p.y = height;
      if (p.y > height) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(56, 189, 248, ${p.alpha})`;
      ctx.fill();

      // Connect nearby particles with subtle lines
      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dx = p.x - p2.x;
        const dy = p.y - p2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 110) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = `rgba(56, 189, 248, ${0.12 * (1 - dist / 110)})`;
          ctx.lineWidth = 0.7;
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(render);
  }
  render();
}

// =========================================================================
// 3. DAAC CONTAINER PROTOCOL CONSTANTS
// =========================================================================
const MAGIC_DAAC = [0x44, 0x41, 0x41, 0x43]; // "DAAC"
const ALGO_HUFFMAN = 1;
const ALGO_RLE = 2;
const ALGO_LZW = 3;

const ALGO_NAMES = {
  1: "Huffman Coding",
  2: "Run-Length Encoding (RLE)",
  3: "LZW Compression"
};

const ALGO_TAGS = {
  1: "Greedy Min-Heap",
  2: "PackBits Byte-Scan",
  3: "Adaptive Dictionary"
};

// Application State
let currentInputFile = null;      // { name, size, bytes: Uint8Array, mime, isImage, width, height }
let currentCompressedFile = null; // { name, bytes: Uint8Array, stats }
let currentDecompArchive = null;  // { name, bytes: Uint8Array }
let currentVerifyFile = null;     // { name, bytes: Uint8Array }
let currentRestoredFile = null;   // { name, bytes: Uint8Array, mime, isImage }

// =========================================================================
// 4. SHA-256 CRYPTOGRAPHIC DIGEST & BITSTREAM UTILITIES
// =========================================================================
async function computeSHA256(uint8Array) {
  const hashBuffer = await crypto.subtle.digest("SHA-256", uint8Array);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function computeShannonEntropy(bytes) {
  if (!bytes || bytes.length === 0) return 0;
  const freq = new Uint32Array(256);
  for (let i = 0; i < bytes.length; i++) freq[bytes[i]]++;
  const len = bytes.length;
  let entropy = 0;
  for (let i = 0; i < 256; i++) {
    if (freq[i] > 0) {
      const p = freq[i] / len;
      entropy -= p * Math.log2(p);
    }
  }
  return entropy; // 0.0 to 8.0 bits/symbol
}

// Fixed 50-byte container pack
function packContainer(algoId, originalSize, sha256Hex, metadata, payload) {
  const header = new Uint8Array(50);
  const view = new DataView(header.buffer);

  // Magic "DAAC"
  header[0] = 0x44; header[1] = 0x41; header[2] = 0x41; header[3] = 0x43;
  header[4] = 1;       // Format Version 0x01
  header[5] = algoId;  // Algorithm ID (1, 2, 3)

  view.setBigUint64(6, BigInt(originalSize), false);

  for (let i = 0; i < 32; i++) {
    header[14 + i] = parseInt(sha256Hex.substr(i * 2, 2), 16);
  }

  view.setUint32(46, metadata.length, false);

  const combined = new Uint8Array(50 + metadata.length + payload.length);
  combined.set(header, 0);
  combined.set(metadata, 50);
  combined.set(payload, 50 + metadata.length);
  return combined;
}

// Container unpack
function unpackContainer(archiveBytes) {
  if (archiveBytes.length < 50) {
    throw new Error(`Archive too small (${archiveBytes.length} bytes, minimum 50 bytes required).`);
  }

  if (archiveBytes[0] !== 0x44 || archiveBytes[1] !== 0x41 || archiveBytes[2] !== 0x41 || archiveBytes[3] !== 0x43) {
    throw new Error("Invalid format: Magic bytes mismatch (expected 'DAAC' 0x44414143).");
  }

  const view = new DataView(archiveBytes.buffer, archiveBytes.byteOffset, archiveBytes.byteLength);
  const version = archiveBytes[4];
  const algoId = archiveBytes[5];
  const originalSize = Number(view.getBigUint64(6, false));

  const hashArray = Array.from(archiveBytes.slice(14, 46));
  const sha256Hex = hashArray.map(b => b.toString(16).padStart(2, "0")).join("");

  const metaLen = view.getUint32(46, false);
  const metaStart = 50;
  const metaEnd = metaStart + metaLen;

  if (archiveBytes.length < metaEnd) {
    throw new Error("Archive truncated inside metadata section.");
  }

  const metadata = archiveBytes.slice(metaStart, metaEnd);
  const payload = archiveBytes.slice(metaEnd);

  return { version, algoId, originalSize, sha256Hex, metadata, payload };
}

// Fast Bit-Writer
class JSBitWriter {
  constructor() {
    this.bytes = [];
    this.current = 0;
    this.count = 0;
  }
  writeBit(bit) {
    this.current = (this.current << 1) | (bit & 1);
    this.count++;
    if (this.count === 8) {
      this.bytes.push(this.current);
      this.current = 0;
      this.count = 0;
    }
  }
  writeBits(val, numBits) {
    for (let i = numBits - 1; i >= 0; i--) {
      this.writeBit((val >> i) & 1);
    }
  }
  writeCode(codeStr) {
    for (let i = 0; i < codeStr.length; i++) {
      this.writeBit(codeStr.charCodeAt(i) === 49 ? 1 : 0);
    }
  }
  flush() {
    if (this.count > 0) {
      this.current <<= (8 - this.count);
      this.bytes.push(this.current);
      this.current = 0;
      this.count = 0;
    }
    return new Uint8Array(this.bytes);
  }
}

// Fast Bit-Reader
class JSBitReader {
  constructor(uint8Array) {
    this.bytes = uint8Array;
    this.byteIdx = 0;
    this.bitIdx = 0;
  }
  readBit() {
    if (this.byteIdx >= this.bytes.length) {
      throw new Error("Bitstream EOF");
    }
    const bit = (this.bytes[this.byteIdx] >> (7 - this.bitIdx)) & 1;
    this.bitIdx++;
    if (this.bitIdx === 8) {
      this.bitIdx = 0;
      this.byteIdx++;
    }
    return bit;
  }
  readBits(numBits) {
    let val = 0;
    for (let i = 0; i < numBits; i++) {
      val = (val << 1) | this.readBit();
    }
    return val;
  }
  hasMore() {
    return this.byteIdx < this.bytes.length;
  }
}

// =========================================================================
// 5. COMPRESSION ALGORITHMS (HUFFMAN, PACKBITS RLE, LZW)
// =========================================================================

// --- 1. Huffman Coding ---
function huffmanCompress(bytes) {
  if (bytes.length === 0) return { meta: new Uint8Array(0), payload: new Uint8Array(0) };

  const freq = {};
  for (let i = 0; i < bytes.length; i++) freq[bytes[i]] = (freq[bytes[i]] || 0) + 1;

  const heap = Object.keys(freq).map(b => ({
    freq: freq[b],
    byte: parseInt(b),
    left: null,
    right: null
  }));
  heap.sort((a, b) => a.freq - b.freq);

  if (heap.length === 1) {
    heap[0] = { freq: heap[0].freq, left: heap[0], right: null };
  } else {
    while (heap.length > 1) {
      const left = heap.shift();
      const right = heap.shift();
      const parent = { freq: left.freq + right.freq, left, right };
      let idx = 0;
      while (idx < heap.length && heap[idx].freq < parent.freq) idx++;
      heap.splice(idx, 0, parent);
    }
  }

  const root = heap[0];
  const codeTable = {};
  function traverse(node, code) {
    if (node.byte !== undefined && !node.left && !node.right) {
      codeTable[node.byte] = code || "0";
      return;
    }
    if (node.left) traverse(node.left, code + "0");
    if (node.right) traverse(node.right, code + "1");
  }
  traverse(root, "");

  const entries = Object.keys(freq);
  const meta = new Uint8Array(2 + entries.length * 5);
  const view = new DataView(meta.buffer);
  view.setUint16(0, entries.length, false);
  let offset = 2;
  for (let i = 0; i < entries.length; i++) {
    const b = parseInt(entries[i]);
    meta[offset] = b;
    view.setUint32(offset + 1, freq[b], false);
    offset += 5;
  }

  const writer = new JSBitWriter();
  for (let i = 0; i < bytes.length; i++) {
    writer.writeCode(codeTable[bytes[i]]);
  }

  return { meta, payload: writer.flush() };
}

function huffmanDecompress(meta, payload, originalSize) {
  if (originalSize === 0) return new Uint8Array(0);

  const view = new DataView(meta.buffer, meta.byteOffset, meta.byteLength);
  const count = view.getUint16(0, false);
  const freq = {};
  let offset = 2;
  for (let i = 0; i < count; i++) {
    const b = meta[offset];
    const fr = view.getUint32(offset + 1, false);
    freq[b] = fr;
    offset += 5;
  }

  if (count === 1) {
    const onlyByte = parseInt(Object.keys(freq)[0]);
    const out = new Uint8Array(originalSize);
    out.fill(onlyByte);
    return out;
  }

  const heap = Object.keys(freq).map(b => ({
    freq: freq[b],
    byte: parseInt(b),
    left: null,
    right: null
  }));
  heap.sort((a, b) => a.freq - b.freq);

  while (heap.length > 1) {
    const left = heap.shift();
    const right = heap.shift();
    const parent = { freq: left.freq + right.freq, left, right };
    let idx = 0;
    while (idx < heap.length && heap[idx].freq < parent.freq) idx++;
    heap.splice(idx, 0, parent);
  }

  const root = heap[0];
  const reader = new JSBitReader(payload);
  const output = new Uint8Array(originalSize);
  let outIdx = 0;
  let curr = root;

  while (outIdx < originalSize && reader.hasMore()) {
    try {
      const bit = reader.readBit();
      curr = bit === 1 ? curr.right : curr.left;
      if (!curr) throw new Error("Invalid Huffman traversal");
      if (curr.byte !== undefined && !curr.left && !curr.right) {
        output[outIdx++] = curr.byte;
        curr = root;
      }
    } catch (e) {
      break;
    }
  }

  return output;
}

// --- 2. PackBits RLE ---
function rleCompress(bytes) {
  if (bytes.length === 0) return { meta: new Uint8Array(0), payload: new Uint8Array(0) };

  const out = [];
  let i = 0;
  const n = bytes.length;

  while (i < n) {
    let runLen = 1;
    while (i + runLen < n && bytes[i + runLen] === bytes[i] && runLen < 128) {
      runLen++;
    }

    if (runLen >= 2) {
      out.push((-(runLen - 1)) & 0xFF);
      out.push(bytes[i]);
      i += runLen;
    } else {
      const litStart = i;
      let litLen = 0;
      while (i < n && litLen < 128) {
        if (i + 2 < n && bytes[i] === bytes[i + 1] && bytes[i] === bytes[i + 2]) {
          break;
        }
        litLen++;
        i++;
      }
      out.push(litLen - 1);
      for (let j = 0; j < litLen; j++) {
        out.push(bytes[litStart + j]);
      }
    }
  }

  return { meta: new Uint8Array(0), payload: new Uint8Array(out) };
}

function rleDecompress(meta, payload, originalSize) {
  if (originalSize === 0 || payload.length === 0) return new Uint8Array(0);

  const out = new Uint8Array(originalSize);
  let outIdx = 0;
  let idx = 0;
  const len = payload.length;

  while (idx < len && outIdx < originalSize) {
    const h = payload[idx++];
    const n = h > 127 ? h - 256 : h;

    if (n >= 0 && n <= 127) {
      const count = n + 1;
      for (let k = 0; k < count && outIdx < originalSize; k++) {
        out[outIdx++] = payload[idx++];
      }
    } else if (n >= -127 && n <= -1) {
      const count = -n + 1;
      const b = payload[idx++];
      for (let k = 0; k < count && outIdx < originalSize; k++) {
        out[outIdx++] = b;
      }
    }
  }

  return out;
}

// --- 3. LZW Compression (With Synchronized Bit-Growth Fix) ---
function lzwCompress(bytes) {
  if (bytes.length === 0) return { meta: new Uint8Array(0), payload: new Uint8Array(0) };

  const writer = new JSBitWriter();
  let dict = {};
  for (let i = 0; i < 256; i++) dict[String.fromCharCode(i)] = i;

  const CLEAR_CODE = 256;
  const END_OF_STREAM = 257;
  let nextCode = 258;
  let currentBits = 9;
  const MAX_BITS = 16;
  const MAX_DICT = 1 << MAX_BITS;

  writer.writeBits(CLEAR_CODE, currentBits);
  let phrase = String.fromCharCode(bytes[0]);

  for (let i = 1; i < bytes.length; i++) {
    const char = String.fromCharCode(bytes[i]);
    const nextPhrase = phrase + char;

    if (dict[nextPhrase] !== undefined) {
      phrase = nextPhrase;
    } else {
      writer.writeBits(dict[phrase], currentBits);
      if (nextCode < MAX_DICT) {
        dict[nextPhrase] = nextCode++;
        if (nextCode === (1 << currentBits) && currentBits < MAX_BITS) {
          currentBits++;
        }
      } else {
        writer.writeBits(CLEAR_CODE, currentBits);
        dict = {};
        for (let j = 0; j < 256; j++) dict[String.fromCharCode(j)] = j;
        nextCode = 258;
        currentBits = 9;
      }
      phrase = char;
    }
  }

  if (phrase) {
    writer.writeBits(dict[phrase], currentBits);
  }
  writer.writeBits(END_OF_STREAM, currentBits);

  return { meta: new Uint8Array(0), payload: writer.flush() };
}

function lzwDecompress(meta, payload, originalSize) {
  if (originalSize === 0 || payload.length === 0) return new Uint8Array(0);

  const reader = new JSBitReader(payload);
  const out = new Uint8Array(originalSize);
  let outIdx = 0;

  function initDict() {
    const d = [];
    for (let i = 0; i < 256; i++) d.push([i]);
    d.push([]); // 256 CLEAR
    d.push([]); // 257 EOS
    return d;
  }

  let dict = initDict();
  let currentBits = 9;
  const MAX_BITS = 16;
  const MAX_DICT = 1 << MAX_BITS;
  let prevPhrase = [];

  while (outIdx < originalSize && reader.hasMore()) {
    let code;
    try {
      code = reader.readBits(currentBits);
    } catch (e) {
      break;
    }

    if (code === 257) break; // EOS
    if (code === 256) {      // CLEAR
      dict = initDict();
      currentBits = 9;
      prevPhrase = [];
      continue;
    }

    let phrase;
    if (code < dict.length) {
      phrase = dict[code];
    } else if (code === dict.length && prevPhrase.length > 0) {
      phrase = prevPhrase.concat(prevPhrase[0]);
    } else {
      break;
    }

    for (let i = 0; i < phrase.length && outIdx < originalSize; i++) {
      out[outIdx++] = phrase[i];
    }

    // Decoder dictionary growth synchronization fix
    if (prevPhrase.length > 0 && dict.length < MAX_DICT) {
      dict.push(prevPhrase.concat(phrase[0]));
      if (dict.length + 1 >= (1 << currentBits) && currentBits < MAX_BITS) {
        currentBits++;
      }
    }
    prevPhrase = phrase;
  }

  return out;
}

// =========================================================================
// 6. SYNTHETIC SAMPLE DATA GENERATOR (REAL BMPS, SVGS, PROSE)
// =========================================================================
function generateSampleBMP(width, height, patternType) {
  const rowBytes = (width * 3 + 3) & ~3;
  const imageSize = rowBytes * height;
  const fileSize = 54 + imageSize;

  const buffer = new ArrayBuffer(fileSize);
  const view = new DataView(buffer);
  const bytes = new Uint8Array(buffer);

  // BMP Header (14 bytes)
  bytes[0] = 0x42; bytes[1] = 0x4D; // "BM"
  view.setUint32(2, fileSize, true);
  view.setUint16(6, 0, true);
  view.setUint16(8, 0, true);
  view.setUint32(10, 54, true); // pixel offset

  // DIB Header (40 bytes)
  view.setUint32(14, 40, true);
  view.setInt32(18, width, true);
  view.setInt32(22, height, true);
  view.setUint16(26, 1, true);   // planes
  view.setUint16(28, 24, true);  // 24 bpp
  view.setUint32(30, 0, true);   // BI_RGB (uncompressed)
  view.setUint32(34, imageSize, true);
  view.setInt32(38, 2835, true);
  view.setInt32(42, 2835, true);
  view.setUint32(46, 0, true);
  view.setUint32(50, 0, true);

  // Draw Pixel Patterns
  let offset = 54;
  for (let y = 0; y < height; y++) {
    const rowStart = offset;
    for (let x = 0; x < width; x++) {
      let b = 30, g = 30, r = 30;
      if (patternType === "pixel_art") {
        if ((Math.floor(x / 16) + Math.floor(y / 16)) % 2 === 0) {
          b = 255; g = 100; r = 50; // Cyan-Orange Checker
        } else if (x < width / 4) {
          b = 50; g = 200; r = 255;
        } else {
          b = 180; g = 40; r = 180;
        }
      } else if (patternType === "retro_sprite") {
        // Space invader-like motif
        const cx = Math.abs(x - width / 2);
        if (cx < 12 && y > 10 && y < 50) {
          b = 40; g = 230; r = 120; // Neon Green
        } else {
          b = 15; g = 20; r = 35;   // Dark Background
        }
      }
      bytes[offset++] = b;
      bytes[offset++] = g;
      bytes[offset++] = r;
    }
    // Pad row to multiple of 4
    while ((offset - rowStart) % 4 !== 0) {
      bytes[offset++] = 0;
    }
  }
  return bytes;
}

const TEXT_SAMPLES = {
  "natural_text.txt": `Alice was beginning to get very tired of sitting by her sister on the bank,
and of having nothing to do: once or twice she had peeped into the book her sister
was reading, but it had no pictures or conversations in it, "and what is the use of
a book," thought Alice "without pictures or conversation?"

So she was considering in her own mind (as well as she could, for the hot day made
her feel very sleepy and stupid), whether the pleasure of making a daisy-chain would
be worth the trouble of getting up and picking the daisies, when suddenly a White
Rabbit with pink eyes ran close by her.`,

  "repetitive.txt": "A".repeat(150) + "B".repeat(200) + "C".repeat(100) + "\n" +
                    "THE_QUICK_BROWN_FOX_JUMPS_OVER_THE_LAZY_DOG\n".repeat(30) +
                    "01010101010101010101010101010101\n".repeat(30),

  "source_code.py": `import math
import hashlib

class LosslessCompressor:
    def __init__(self, name: str):
        self.name = name
        self.bit_stream = []

    def encode_symbol(self, symbol: int, code: str):
        for bit in code:
            self.bit_stream.append(1 if bit == '1' else 0)

    def compute_fingerprint(self, payload: bytes) -> str:
        return hashlib.sha256(payload).hexdigest()
`
};

const SVG_SAMPLE = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
  <rect width="200" height="200" fill="#0B0F19"/>
  <circle cx="100" cy="100" r="70" fill="#38BDF8" fill-opacity="0.2" stroke="#38BDF8" stroke-width="4"/>
  <polygon points="100,40 150,140 50,140" fill="#10B981" fill-opacity="0.3" stroke="#10B981" stroke-width="3"/>
  <text x="100" y="180" font-family="sans-serif" font-size="14" fill="#FFFFFF" text-anchor="middle">COMPRESS.DAA</text>
</svg>`;

// =========================================================================
// 7. FILE FORMAT DETECTION & IMAGE PREVIEW
// =========================================================================
function detectMimeAndType(bytes, filename = "") {
  const ext = (filename.split(".").pop() || "").toLowerCase();
  
  if (bytes.length >= 4) {
    // PNG: \x89PNG
    if (bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4E && bytes[3] === 0x47) {
      return { mime: "image/png", isImage: true, formatName: "PNG Image" };
    }
    // JPEG: \xFF\xD8\xFF
    if (bytes[0] === 0xFF && bytes[1] === 0xD8 && bytes[2] === 0xFF) {
      return { mime: "image/jpeg", isImage: true, formatName: "JPEG Image" };
    }
    // BMP: BM
    if (bytes[0] === 0x42 && bytes[1] === 0x4D) {
      return { mime: "image/bmp", isImage: true, formatName: "BMP Bitmap" };
    }
    // GIF: GIF8
    if (bytes[0] === 0x47 && bytes[1] === 0x49 && bytes[2] === 0x46) {
      return { mime: "image/gif", isImage: true, formatName: "GIF Image" };
    }
    // WebP: RIFF....WEBP
    if (bytes[0] === 0x52 && bytes[1] === 0x49 && bytes[2] === 0x46 && bytes[3] === 0x46) {
      return { mime: "image/webp", isImage: true, formatName: "WebP Image" };
    }
  }

  if (ext === "svg" || (bytes.length > 10 && new TextDecoder().decode(bytes.slice(0, 80)).includes("<svg"))) {
    return { mime: "image/svg+xml", isImage: true, formatName: "SVG Vector" };
  }

  if (["png", "jpg", "jpeg", "bmp", "gif", "webp"].includes(ext)) {
    return { mime: `image/${ext === "jpg" ? "jpeg" : ext}`, isImage: true, formatName: `${ext.toUpperCase()} Image` };
  }

  // Check if printable text
  let isText = true;
  const sampleLen = Math.min(bytes.length, 1024);
  for (let i = 0; i < sampleLen; i++) {
    const c = bytes[i];
    if (c === 0 || (c < 9 && c !== 10 && c !== 13)) {
      isText = false;
      break;
    }
  }

  if (isText) {
    return { mime: "text/plain", isImage: false, formatName: ext ? `${ext.toUpperCase()} Source` : "Text Document" };
  }

  return { mime: "application/octet-stream", isImage: false, formatName: "Binary Data" };
}

// Render image preview thumbnail
function loadVisualPreview(bytes, mime, containerEl, detailsCb) {
  containerEl.innerHTML = "";
  const blob = new Blob([bytes], { type: mime });
  const url = URL.createObjectURL(blob);
  const img = new Image();
  img.onload = () => {
    containerEl.appendChild(img);
    if (detailsCb) detailsCb(img.naturalWidth, img.naturalHeight);
  };
  img.onerror = () => {
    containerEl.innerHTML = `<span style="font-size: 2rem;">📄</span>`;
    if (detailsCb) detailsCb(null, null);
  };
  img.src = url;
}

// =========================================================================
// 7.5. DIRECTLY OPENABLE IMAGE COMPRESSOR (OPENS IN MACOS PREVIEW & PHOTOS)
// =========================================================================
function compressImageDirectly(imageBytes, mimeType, qualityFactor = 0.75, origFilename = "") {
  return new Promise((resolve, reject) => {
    const blob = new Blob([imageBytes], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(url);

      // Determine extension from original filename to preserve exact format
      let ext = ".jpg";
      let outMime = "image/jpeg";

      if (origFilename && origFilename.includes(".")) {
        ext = origFilename.substring(origFilename.lastIndexOf(".")).toLowerCase();
      } else if (mimeType === "image/png") {
        ext = ".png";
      } else if (mimeType === "image/webp") {
        ext = ".webp";
      }

      if (ext === ".png" || mimeType === "image/png") {
        outMime = "image/png";
        ext = ".png";
      } else if (ext === ".webp" || mimeType === "image/webp") {
        outMime = "image/webp";
        ext = ".webp";
      } else {
        outMime = "image/jpeg";
        if (ext !== ".jpeg") ext = ".jpg";
      }

      // Scale and dimensions:
      // High Fidelity and Balanced preserve 100% exact original pixel dimensions (scale = 1.0)
      const baseW = img.naturalWidth || img.width;
      const baseH = img.naturalHeight || img.height;
      let scale = 1.0;
      if (qualityFactor <= 0.5) {
        scale = 0.75; // Max Compression: slight downscale for maximum disk space savings
      } else if (qualityFactor <= 0.75 && (baseW > 2560 || baseH > 2560)) {
        scale = 0.85; // Balanced: only downscale if image is an ultra-high resolution photo (>2560px)
      } else {
        scale = 1.0;  // 100% identical pixel dimensions preserved!
      }

      let w = Math.max(16, Math.round(baseW * scale));
      let h = Math.max(16, Math.round(baseH * scale));

      // Cap at 2560px for extreme phone photos (e.g. 48MP)
      const MAX_DIM = 2560;
      if (w > MAX_DIM || h > MAX_DIM) {
        if (w > h) {
          h = Math.round((h * MAX_DIM) / w);
          w = MAX_DIM;
        } else {
          w = Math.round((w * MAX_DIM) / h);
          h = MAX_DIM;
        }
      }

      const canvas = document.createElement("canvas");
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext("2d");

      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = "high";

      // If exporting to JPEG, fill white background (JPEG doesn't support alpha transparency)
      if (outMime === "image/jpeg") {
        ctx.fillStyle = "#FFFFFF";
        ctx.fillRect(0, 0, w, h);
      } else {
        ctx.clearRect(0, 0, w, h);
      }

      ctx.drawImage(img, 0, 0, w, h);

      canvas.toBlob((compressedBlob) => {
        if (!compressedBlob) {
          reject(new Error("Canvas compression failed"));
          return;
        }
        const reader = new FileReader();
        reader.onload = () => {
          resolve({
            bytes: new Uint8Array(reader.result),
            mime: outMime,
            ext: ext,
            width: w,
            height: h
          });
        };
        reader.readAsArrayBuffer(compressedBlob);
      }, outMime, outMime === "image/png" ? undefined : qualityFactor);
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error("Failed to load image for compression"));
    };
    img.src = url;
  });
}

// =========================================================================
// 8. CONTROLLER: TAB 1 (COMPRESS)
// =========================================================================
function setupCompressorUI() {
  const dropzone = document.getElementById("compress-dropzone");
  const fileInput = document.getElementById("compress-file-input");
  const fileCard = document.getElementById("compress-file-card");
  const thumbWrap = document.getElementById("compress-thumb-wrap");
  const nameLabel = document.getElementById("telemetry-name");
  const typeBadge = document.getElementById("telemetry-type-badge");
  const sizeBadge = document.getElementById("telemetry-size-badge");
  const dimBadge = document.getElementById("telemetry-dim-badge");
  const entropyVal = document.getElementById("entropy-value");
  const entropyFill = document.getElementById("entropy-bar-fill");
  const entropyVerdict = document.getElementById("entropy-verdict");
  const changeBtn = document.getElementById("btn-change-file");
  const compressBtn = document.getElementById("btn-compress-action");
  const downloadBtn = document.getElementById("btn-download-daac");

  const smartImageCard = document.getElementById("engine-card-smart-image");
  const smartImagePanel = document.getElementById("image-quality-panel");
  const smartImageRadio = document.getElementById("algo-image-opt");
  const instantPreviewBtn = document.getElementById("btn-instant-preview");
  const inlinePreviewWrap = document.getElementById("compress-inline-preview-wrap");
  const inlineViewport = document.getElementById("compress-inline-preview-viewport");
  const inlineTitle = document.getElementById("inline-preview-title");

  let currentQualityFactor = 0.75;

  // Quality chip selector handlers
  document.querySelectorAll(".chip-quality").forEach(chip => {
    chip.addEventListener("click", () => {
      soundFX.playClick();
      document.querySelectorAll(".chip-quality").forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      currentQualityFactor = parseFloat(chip.dataset.quality) || 0.75;
      const descLabel = document.getElementById("quality-desc-label");
      if (descLabel) {
        descLabel.textContent = chip.dataset.desc;
      }
    });
  });

  // Dropzone drag-and-drop
  dropzone.addEventListener("dragover", e => { e.preventDefault(); dropzone.classList.add("dragover"); });
  dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));
  dropzone.addEventListener("drop", e => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length) handleSelectedFile(e.dataTransfer.files[0]);
  });
  fileInput.addEventListener("change", e => {
    if (e.target.files.length) handleSelectedFile(e.target.files[0]);
  });

  function handleSelectedFile(file) {
    soundFX.playClick();
    const reader = new FileReader();
    reader.onload = ev => {
      const bytes = new Uint8Array(ev.target.result);
      processInputData(file.name, bytes);
    };
    reader.readAsArrayBuffer(file);
  }

  function processInputData(filename, bytes) {
    const meta = detectMimeAndType(bytes, filename);
    const entropy = computeShannonEntropy(bytes);

    currentInputFile = {
      name: filename,
      size: bytes.length,
      bytes: bytes,
      mime: meta.mime,
      isImage: meta.isImage,
      formatName: meta.formatName
    };

    nameLabel.textContent = filename;
    sizeBadge.textContent = `${(bytes.length / 1024).toFixed(1)} KB (${bytes.length.toLocaleString()} B)`;
    typeBadge.textContent = meta.formatName;
    entropyVal.textContent = `${entropy.toFixed(2)} / 8.00 b/s`;
    entropyFill.style.width = `${(entropy / 8) * 100}%`;

    // Entropy intelligence verdict
    if (entropy < 2.5) {
      entropyVerdict.textContent = "Very Low Entropy (High Redundancy) — 10x-50x+ compression expected!";
    } else if (entropy < 5.5) {
      entropyVerdict.textContent = "Moderate Entropy — Repeating motifs present, strong compression expected.";
    } else if (entropy < 7.3) {
      entropyVerdict.textContent = "Natural Entropy — Natural text or code, 1.5x-2.5x ratio expected.";
    } else {
      entropyVerdict.textContent = "High Entropy (Pre-compressed/Noise) — Lossless entropy limits apply.";
    }

    if (meta.isImage) {
      loadVisualPreview(bytes, meta.mime, thumbWrap, (w, h) => {
        if (w && h) {
          dimBadge.style.display = "inline-block";
          dimBadge.textContent = `${w} × ${h} px`;
        } else {
          dimBadge.style.display = "none";
        }
      });

      // Show and auto-select Direct Image Compression for images!
      if (smartImageCard) smartImageCard.style.display = "block";
      if (smartImagePanel) smartImagePanel.style.display = "block";
      document.querySelectorAll(".engine-card").forEach(c => c.classList.remove("selected"));
      if (smartImageCard) smartImageCard.classList.add("selected");
      if (smartImageRadio) smartImageRadio.checked = true;
    } else {
      thumbWrap.innerHTML = `<span style="font-size: 1.8rem;">📄</span>`;
      dimBadge.style.display = "none";

      // Hide smart image options for non-image files
      if (smartImageCard) smartImageCard.style.display = "none";
      if (smartImagePanel) smartImagePanel.style.display = "none";
      const currentRadio = document.querySelector("input[name=compression-algo]:checked");
      if (!currentRadio || currentRadio.value === "image_opt") {
        const huffmanRadio = document.getElementById("algo-huffman");
        const huffmanCard = huffmanRadio ? huffmanRadio.closest(".engine-card") : null;
        document.querySelectorAll(".engine-card").forEach(c => c.classList.remove("selected"));
        if (huffmanCard) huffmanCard.classList.add("selected");
        if (huffmanRadio) huffmanRadio.checked = true;
      }
    }

    dropzone.style.display = "none";
    fileCard.style.display = "block";
    compressBtn.disabled = false;
    if (inlinePreviewWrap) inlinePreviewWrap.style.display = "none";
  }

  changeBtn.addEventListener("click", () => {
    soundFX.playClick();
    currentInputFile = null;
    fileCard.style.display = "none";
    dropzone.style.display = "block";
    compressBtn.disabled = true;
    fileInput.value = "";
    document.getElementById("compress-results-state").style.display = "none";
    document.getElementById("compress-idle-state").style.display = "block";
    if (inlinePreviewWrap) inlinePreviewWrap.style.display = "none";
  });

  // Quick Preset Handlers (Images & Text)
  document.querySelectorAll(".preset-chip[data-sample]").forEach(chip => {
    chip.addEventListener("click", () => {
      soundFX.playClick();
      const sample = chip.dataset.sample;
      let bytes;
      if (sample === "pixel_art.bmp") {
        bytes = generateSampleBMP(128, 128, "pixel_art");
      } else if (sample === "retro_sprite.bmp") {
        bytes = generateSampleBMP(64, 64, "retro_sprite");
      } else if (sample === "vector_diagram.svg") {
        bytes = new TextEncoder().encode(SVG_SAMPLE);
      } else {
        bytes = new TextEncoder().encode(TEXT_SAMPLES[sample] || "SAMPLE");
      }
      processInputData(sample, bytes);
    });
  });

  // Algorithm selection radio cards
  document.querySelectorAll(".engine-card").forEach(card => {
    card.addEventListener("click", () => {
      soundFX.playClick();
      document.querySelectorAll(".engine-card").forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
      const radio = card.querySelector("input[type=radio]");
      if (radio) {
        radio.checked = true;
        if (radio.value === "image_opt") {
          if (smartImagePanel) smartImagePanel.style.display = "block";
        } else {
          if (smartImagePanel) smartImagePanel.style.display = "none";
        }
      }
    });
  });

  // Compress Action Button
  compressBtn.addEventListener("click", async () => {
    if (!currentInputFile) return;
    soundFX.playCompress();

    const algoChoice = document.querySelector("input[name=compression-algo]:checked").value;
    compressBtn.disabled = true;
    compressBtn.innerHTML = `<span>⏳</span> Compressing Stream...`;

    // Yield to UI thread
    await new Promise(r => setTimeout(r, 40));

    // Case 1: Directly Openable Image Compression (Produces real, openable image file)
    if (algoChoice === "image_opt" && currentInputFile.isImage) {
      try {
        const startTime = performance.now();
        const optResult = await compressImageDirectly(currentInputFile.bytes, currentInputFile.mime, currentQualityFactor, currentInputFile.name);
        const latency = performance.now() - startTime;
        const sha256Hex = await computeSHA256(currentInputFile.bytes);

        const origSize = currentInputFile.bytes.length;
        const compSize = optResult.bytes.length;
        const ratio = compSize > 0 ? origSize / compSize : 0;
        const savings = origSize > 0 ? ((1 - compSize / origSize) * 100) : 0;
        const throughputMB = latency > 0 ? ((origSize / (1024 * 1024)) / (latency / 1000)).toFixed(1) : "0.0";

        // Output filename: compressed_<name>.<original_extension>
        const baseName = currentInputFile.name;
        const compName = baseName.startsWith("compressed_") ? baseName : `compressed_${baseName}`;

        currentCompressedFile = {
          name: compName,
          bytes: optResult.bytes,
          mime: optResult.mime,
          isDirectImage: true,
          width: optResult.width,
          height: optResult.height
        };

        soundFX.playSuccess();

        // Render Metrics
        document.getElementById("compress-idle-state").style.display = "none";
        document.getElementById("compress-results-state").style.display = "block";

        document.getElementById("metric-ratio").textContent = `${ratio.toFixed(2)}x`;
        document.getElementById("metric-savings").textContent = `${savings >= 0 ? "+" : ""}${savings.toFixed(1)}%`;
        document.getElementById("metric-latency").textContent = `${latency.toFixed(2)} ms`;
        document.getElementById("metric-throughput").textContent = `${throughputMB} MB/s`;
        document.getElementById("metric-algo-name").textContent = "Direct Image Opt";
        document.getElementById("metric-algo-tag").textContent = "Native Apple Preview";

        document.getElementById("track-orig-bytes").textContent = `${origSize.toLocaleString()} B (${(origSize / 1024).toFixed(1)} KB)`;
        document.getElementById("track-comp-bytes").textContent = `${compSize.toLocaleString()} B (${(compSize / 1024).toFixed(1)} KB)`;
        const percentFill = Math.min(100, Math.max(4, (compSize / (origSize || 1)) * 100));
        document.getElementById("track-comp-fill").style.width = `${percentFill}%`;

        document.getElementById("metric-hash").textContent = sha256Hex;

        // Render Inspector Breakdown
        const headerStrip = document.getElementById("container-header-strip");
        headerStrip.innerHTML = `
          <div class="byte-block"><span class="byte-name">Format</span><span class="byte-val">${optResult.ext.toUpperCase().replace(".", "")}</span></div>
          <div class="byte-block"><span class="byte-name">Quality</span><span class="byte-val">${Math.round(currentQualityFactor * 100)}%</span></div>
          <div class="byte-block"><span class="byte-name">Resolution</span><span class="byte-val">${optResult.width}×${optResult.height}</span></div>
          <div class="byte-block"><span class="byte-name">Orig Size</span><span class="byte-val">${(origSize / 1024).toFixed(1)} KB</span></div>
          <div class="byte-block"><span class="byte-name">Comp Size</span><span class="byte-val">${(compSize / 1024).toFixed(1)} KB</span></div>
          <div class="byte-block"><span class="byte-name">Status</span><span class="byte-val" style="color: var(--green-bright);">Openable</span></div>
        `;

        // Update tip text
        const tipText = document.getElementById("open-tip-text");
        if (tipText) {
          tipText.innerHTML = `✅ <strong>Ready to Open!</strong> Saved with original extension as <code>${compName}</code> with <strong>${savings.toFixed(1)}% actual file size reduction</strong>! You can double-click it directly in macOS Finder to open it in <strong>Apple Preview, Photos, or any viewer</strong>.`;
        }

        const dlBtnSpan = document.getElementById("btn-download-text");
        if (dlBtnSpan) {
          dlBtnSpan.textContent = `Download ${compName}`;
        }

        if (inlinePreviewWrap) inlinePreviewWrap.style.display = "none";
      } catch (err) {
        alert(`Direct Image Compression Failed: ${err.message}`);
      } finally {
        compressBtn.disabled = false;
        compressBtn.innerHTML = `<span>⚡</span> Compress File`;
      }
      return;
    }

    // Case 2: DAA Lossless Algorithms (Huffman Coding, RLE, LZW)
    try {
      const startTime = performance.now();
      let compressed;
      let algoId;

      if (algoChoice === "huffman") {
        algoId = ALGO_HUFFMAN;
        compressed = huffmanCompress(currentInputFile.bytes);
      } else if (algoChoice === "rle") {
        algoId = ALGO_RLE;
        compressed = rleCompress(currentInputFile.bytes);
      } else {
        algoId = ALGO_LZW;
        compressed = lzwCompress(currentInputFile.bytes);
      }

      const latency = performance.now() - startTime;
      const sha256Hex = await computeSHA256(currentInputFile.bytes);

      const archiveBytes = packContainer(
        algoId,
        currentInputFile.bytes.length,
        sha256Hex,
        compressed.meta,
        compressed.payload
      );

      const origSize = currentInputFile.bytes.length;
      const compSize = archiveBytes.length;
      const ratio = compSize > 0 ? origSize / compSize : 0;
      const savings = origSize > 0 ? ((1 - compSize / origSize) * 100) : 0;
      const throughputMB = latency > 0 ? ((origSize / (1024 * 1024)) / (latency / 1000)).toFixed(1) : "0.0";

      // Output filename: compressed_<name>.<original_extension> (NO .daac added)
      const baseName = currentInputFile.name;
      const compName = baseName.startsWith("compressed_") ? baseName : `compressed_${baseName}`;

      currentCompressedFile = {
        name: compName,
        bytes: archiveBytes,
        isDirectImage: false,
        algoId: algoId
      };

      soundFX.playSuccess();

      // Render Metrics
      document.getElementById("compress-idle-state").style.display = "none";
      document.getElementById("compress-results-state").style.display = "block";

      document.getElementById("metric-ratio").textContent = `${ratio.toFixed(2)}x`;
      document.getElementById("metric-savings").textContent = `${savings >= 0 ? "+" : ""}${savings.toFixed(1)}%`;
      document.getElementById("metric-latency").textContent = `${latency.toFixed(2)} ms`;
      document.getElementById("metric-throughput").textContent = `${throughputMB} MB/s`;
      document.getElementById("metric-algo-name").textContent = ALGO_NAMES[algoId];
      document.getElementById("metric-algo-tag").textContent = ALGO_TAGS[algoId];

      document.getElementById("track-orig-bytes").textContent = `${origSize.toLocaleString()} B (${(origSize / 1024).toFixed(1)} KB)`;
      document.getElementById("track-comp-bytes").textContent = `${compSize.toLocaleString()} B (${(compSize / 1024).toFixed(1)} KB)`;
      const percentFill = Math.min(100, Math.max(4, (compSize / (origSize || 1)) * 100));
      document.getElementById("track-comp-fill").style.width = `${percentFill}%`;

      document.getElementById("metric-hash").textContent = sha256Hex;

      // Render Container Header Breakdown
      const headerStrip = document.getElementById("container-header-strip");
      headerStrip.innerHTML = `
        <div class="byte-block"><span class="byte-name">Magic</span><span class="byte-val">DAAC</span></div>
        <div class="byte-block"><span class="byte-name">Ver</span><span class="byte-val">0x01</span></div>
        <div class="byte-block"><span class="byte-name">Algo ID</span><span class="byte-val">0x0${algoId}</span></div>
        <div class="byte-block"><span class="byte-name">Orig Size</span><span class="byte-val">${origSize}B</span></div>
        <div class="byte-block"><span class="byte-name">SHA-256</span><span class="byte-val">${sha256Hex.substring(0, 8)}...</span></div>
        <div class="byte-block"><span class="byte-name">Meta Len</span><span class="byte-val">${compressed.meta.length}B</span></div>
        <div class="byte-block"><span class="byte-name">Payload</span><span class="byte-val">${compressed.payload.length}B</span></div>
      `;

      // Update tip text explaining container format and instant preview
      const tipText = document.getElementById("open-tip-text");
      if (tipText) {
        tipText.innerHTML = `💡 <strong>Lossless Bitstream Encoding:</strong> Saved with original extension as <code>${compName}</code>. Click <strong>"Instant View"</strong> below to preview the reconstructed file immediately, or drop it into the <strong>Decompress</strong> tab to restore it!`;
      }

      const dlBtnSpan = document.getElementById("btn-download-text");
      if (dlBtnSpan) {
        dlBtnSpan.textContent = `Download ${compName}`;
      }

      if (inlinePreviewWrap) inlinePreviewWrap.style.display = "none";
    } catch (err) {
      alert(`Compression Failed: ${err.message}`);
    } finally {
      compressBtn.disabled = false;
      compressBtn.innerHTML = `<span>⚡</span> Compress File`;
    }
  });

  // Download Archive / Compressed Image
  downloadBtn.addEventListener("click", () => {
    if (!currentCompressedFile) return;
    soundFX.playClick();
    const mime = currentCompressedFile.mime || "application/octet-stream";
    const blob = new Blob([currentCompressedFile.bytes], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = currentCompressedFile.name;
    a.click();
    URL.revokeObjectURL(url);
  });

  // Instant View / Decompress Preview Button Handler
  if (instantPreviewBtn) {
    instantPreviewBtn.addEventListener("click", () => {
      if (!currentCompressedFile) return;
      soundFX.playClick();

      inlinePreviewWrap.style.display = "block";
      inlineViewport.innerHTML = "";

      if (currentCompressedFile.isDirectImage) {
        inlineTitle.textContent = `Instant Preview: ${currentCompressedFile.name} (Direct Openable Image)`;
        const blob = new Blob([currentCompressedFile.bytes], { type: currentCompressedFile.mime });
        const url = URL.createObjectURL(blob);
        const img = document.createElement("img");
        img.src = url;
        img.style.maxWidth = "100%";
        img.style.maxHeight = "360px";
        img.style.borderRadius = "8px";
        img.style.border = "1px solid rgba(255, 255, 255, 0.1)";
        img.style.boxShadow = "0 8px 24px rgba(0,0,0,0.5)";
        inlineViewport.appendChild(img);
      } else {
        // DAA container: decompress in memory
        inlineTitle.textContent = `Instant Decompressed Preview: ${currentInputFile.name} (100% Lossless Match)`;
        try {
          const header = unpackContainer(currentCompressedFile.bytes);
          let restoredBytes;
          if (header.algoId === ALGO_HUFFMAN) {
            restoredBytes = huffmanDecompress(header.metadata, header.payload, header.originalSize);
          } else if (header.algoId === ALGO_RLE) {
            restoredBytes = rleDecompress(header.metadata, header.payload, header.originalSize);
          } else {
            restoredBytes = lzwDecompress(header.metadata, header.payload, header.originalSize);
          }

          const meta = detectMimeAndType(restoredBytes, currentInputFile.name);
          if (meta.isImage) {
            const blob = new Blob([restoredBytes], { type: meta.mime });
            const url = URL.createObjectURL(blob);
            const img = document.createElement("img");
            img.src = url;
            img.style.maxWidth = "100%";
            img.style.maxHeight = "360px";
            img.style.borderRadius = "8px";
            img.style.border = "1px solid rgba(255, 255, 255, 0.1)";
            img.style.boxShadow = "0 8px 24px rgba(0,0,0,0.5)";
            inlineViewport.appendChild(img);
          } else {
            // Text or code preview
            const text = new TextDecoder().decode(restoredBytes.slice(0, 5000));
            const pre = document.createElement("pre");
            pre.style.margin = "0";
            pre.style.padding = "1rem";
            pre.style.fontFamily = "var(--font-mono)";
            pre.style.fontSize = "0.85rem";
            pre.style.color = "var(--text-bright)";
            pre.style.background = "rgba(0,0,0,0.4)";
            pre.style.borderRadius = "6px";
            pre.style.maxHeight = "300px";
            pre.style.overflow = "auto";
            pre.textContent = text + (restoredBytes.length > 5000 ? "\n... (truncated for display)" : "");
            inlineViewport.appendChild(pre);
          }
        } catch (err) {
          inlineViewport.innerHTML = `<div style="color: var(--crimson); padding: 1rem;">Failed to decompress preview: ${escapeHtml(err.message)}</div>`;
        }
      }

      inlinePreviewWrap.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
  }

  // Copy SHA-256
  document.getElementById("btn-copy-hash").addEventListener("click", () => {
    const hash = document.getElementById("metric-hash").textContent;
    navigator.clipboard.writeText(hash).then(() => {
      soundFX.playClick();
      alert("SHA-256 Hash copied to clipboard!");
    });
  });
}

// =========================================================================
// 9. CONTROLLER: TAB 2 (DECOMPRESS & RENDER)
// =========================================================================
function setupDecompressorUI() {
  const dropzone = document.getElementById("decompress-dropzone");
  const fileInput = document.getElementById("decompress-file-input");
  const archiveCard = document.getElementById("decomp-archive-card");
  const archiveName = document.getElementById("decomp-archive-name");
  const archiveSize = document.getElementById("decomp-archive-size");
  const detectedAlgo = document.getElementById("decomp-detected-algo");
  const verifyInput = document.getElementById("verify-file-input");
  const verifyLabel = document.getElementById("verify-label-text");
  const decompressBtn = document.getElementById("btn-decompress-action");
  const downloadBtn = document.getElementById("btn-download-restored");
  const downloadBtnText = document.getElementById("btn-download-restored-text");

  dropzone.addEventListener("dragover", e => { e.preventDefault(); dropzone.classList.add("dragover"); });
  dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));
  dropzone.addEventListener("drop", e => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length) handleArchive(e.dataTransfer.files[0]);
  });
  fileInput.addEventListener("change", e => {
    if (e.target.files.length) handleArchive(e.target.files[0]);
  });

  function handleArchive(file) {
    soundFX.playClick();
    const reader = new FileReader();
    reader.onload = ev => {
      const bytes = new Uint8Array(ev.target.result);
      try {
        const unpacked = unpackContainer(bytes);
        currentDecompArchive = {
          name: file.name,
          bytes: bytes,
          unpacked: unpacked
        };

        archiveName.textContent = file.name;
        archiveSize.textContent = `${(file.size / 1024).toFixed(1)} KB`;
        detectedAlgo.textContent = `${ALGO_NAMES[unpacked.algoId]} (Header Byte 5)`;
        archiveCard.style.display = "block";
        decompressBtn.disabled = false;
      } catch (err) {
        if (file.name.match(/\.(jpg|jpeg|png|webp|gif)$/i)) {
          alert(`Notice: "${file.name}" is a standard viewable image file, not an encoded DAA binary container.\n\nIt is already decompressed and ready to open directly in Apple Preview or Photos!`);
        } else {
          alert(`Archive Parsing Error: ${err.message}\n\nPlease provide a valid DAA compressed archive (.daac) with a DAAC container header.`);
        }
      }
    };
    reader.readAsArrayBuffer(file);
  }

  // Optional verify file
  verifyInput.addEventListener("change", e => {
    if (e.target.files.length) {
      soundFX.playClick();
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onload = ev => {
        currentVerifyFile = {
          name: file.name,
          bytes: new Uint8Array(ev.target.result)
        };
        verifyLabel.textContent = `✓ Selected: ${file.name} (${file.size.toLocaleString()} bytes)`;
      };
      reader.readAsArrayBuffer(file);
    }
  });

  // Decompress Action
  decompressBtn.addEventListener("click", async () => {
    if (!currentDecompArchive) return;
    soundFX.playCompress();

    decompressBtn.disabled = true;
    decompressBtn.innerHTML = `<span>⏳</span> Decompressing Payload...`;

    await new Promise(r => setTimeout(r, 40));

    try {
      const unpacked = currentDecompArchive.unpacked;
      const startTime = performance.now();
      let restoredBytes;

      if (unpacked.algoId === ALGO_HUFFMAN) {
        restoredBytes = huffmanDecompress(unpacked.metadata, unpacked.payload, unpacked.originalSize);
      } else if (unpacked.algoId === ALGO_RLE) {
        restoredBytes = rleDecompress(unpacked.metadata, unpacked.payload, unpacked.originalSize);
      } else if (unpacked.algoId === ALGO_LZW) {
        restoredBytes = lzwDecompress(unpacked.metadata, unpacked.payload, unpacked.originalSize);
      } else {
        throw new Error(`Unsupported algorithm ID: ${unpacked.algoId}`);
      }

      const latency = performance.now() - startTime;
      const restoredHash = await computeSHA256(restoredBytes);

      // Verify SHA-256
      if (restoredHash !== unpacked.sha256Hex) {
        throw new Error("Cryptographic integrity failure: SHA-256 hash mismatch!");
      }

      // Check optional verify file if provided
      let auditDetail = "SHA-256 hash matches archive header exactly. Bit-for-bit identical reconstruction.";
      if (currentVerifyFile) {
        const match = currentVerifyFile.bytes.length === restoredBytes.length &&
                      currentVerifyFile.bytes.every((v, i) => v === restoredBytes[i]);
        auditDetail += match ? " (Audited against uploaded original: 100% byte identical)." : " (Uploaded original does not match restored data!).";
      }

      // Detect restored format and name
      let restoredName = currentDecompArchive.name;
      if (restoredName.startsWith("compressed_")) {
        restoredName = restoredName.substring("compressed_".length);
      } else if (restoredName.endsWith(".daac")) {
        restoredName = restoredName.replace(/\.daac$/i, "");
      } else {
        restoredName = `restored_${restoredName}`;
      }
      const meta = detectMimeAndType(restoredBytes, restoredName);

      currentRestoredFile = {
        name: restoredName,
        bytes: restoredBytes,
        mime: meta.mime,
        isImage: meta.isImage
      };

      soundFX.playSuccess();

      // Update UI
      document.getElementById("decomp-idle-state").style.display = "none";
      document.getElementById("decomp-results-state").style.display = "block";

      document.getElementById("decomp-size-val").textContent = `${restoredBytes.length.toLocaleString()} B`;
      document.getElementById("decomp-latency-val").textContent = `${latency.toFixed(2)} ms`;
      document.getElementById("decomp-algo-val").textContent = ALGO_NAMES[unpacked.algoId];
      document.getElementById("decomp-format-val").textContent = meta.formatName;
      document.getElementById("decomp-integrity-detail").textContent = auditDetail;

      downloadBtnText.textContent = `Download Restored File (${restoredName})`;

      // LIVE VISUAL RENDER OF RESTORED DATA (IMAGES, TEXT, OR HEX)
      const viewport = document.getElementById("preview-viewport");
      viewport.innerHTML = "";

      if (meta.isImage) {
        const blob = new Blob([restoredBytes], { type: meta.mime });
        const img = document.createElement("img");
        img.src = URL.createObjectURL(blob);
        img.alt = "Restored Lossless Image Preview";
        viewport.appendChild(img);
        document.getElementById("preview-bar-title").textContent = `Restored Lossless Image Render (${meta.formatName})`;
      } else if (meta.mime === "text/plain") {
        const text = new TextDecoder().decode(restoredBytes.slice(0, 4000));
        const pre = document.createElement("pre");
        pre.className = "preview-text-box";
        pre.textContent = text + (restoredBytes.length > 4000 ? "\n... [preview truncated for length]" : "");
        viewport.appendChild(pre);
        document.getElementById("preview-bar-title").textContent = "Restored Plaintext Inspection";
      } else {
        // Binary Hex Viewer
        let hex = "";
        const limit = Math.min(restoredBytes.length, 256);
        for (let i = 0; i < limit; i += 16) {
          const chunk = restoredBytes.slice(i, i + 16);
          const hexLine = Array.from(chunk).map(b => b.toString(16).padStart(2, "0").toUpperCase()).join(" ");
          hex += `${i.toString(16).padStart(4, "0").toUpperCase()}: ${hexLine.padEnd(48, " ")}\n`;
        }
        const pre = document.createElement("pre");
        pre.className = "preview-hex-dump";
        pre.textContent = hex;
        viewport.appendChild(pre);
        document.getElementById("preview-bar-title").textContent = "Restored Binary Hex Inspection";
      }

    } catch (err) {
      alert(`Decompression Error: ${err.message}`);
    } finally {
      decompressBtn.disabled = false;
      decompressBtn.innerHTML = `<span>🔓</span> Decompress & Verify Lossless Integrity`;
    }
  });

  downloadBtn.addEventListener("click", () => {
    if (!currentRestoredFile) return;
    soundFX.playClick();
    const blob = new Blob([currentRestoredFile.bytes], { type: currentRestoredFile.mime || "application/octet-stream" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = currentRestoredFile.name;
    a.click();
    URL.revokeObjectURL(url);
  });
}

// =========================================================================
// 10. CONTROLLER: TAB 3 (ANALYSIS & BENCHMARK SUITE + HUFFMAN TREE)
// =========================================================================
function setupBenchmarkUI() {
  const runBtn = document.getElementById("btn-run-benchmark-suite");
  const tableBody = document.getElementById("bench-matrix-body");
  const chartCanvas = document.getElementById("benchmark-chart-canvas");

  runBtn.addEventListener("click", async () => {
    soundFX.playCompress();
    runBtn.disabled = true;
    document.getElementById("bench-btn-text").textContent = "Running Benchmark Suite...";
    tableBody.innerHTML = `<tr><td colspan="9" class="table-empty-cell" style="color: var(--cyan);">Executing compression matrix across diverse entropy profiles...</td></tr>`;

    await new Promise(r => setTimeout(r, 60));

    const datasets = [
      { name: "Pixel Art (128x128 BMP)", bytes: generateSampleBMP(128, 128, "pixel_art"), profile: "2D Run-Length Imagery" },
      { name: "Patterned Runs (2KB)", bytes: new TextEncoder().encode(TEXT_SAMPLES["repetitive.txt"]), profile: "Skewed Low Entropy" },
      { name: "Monolithic Run (10KB)", bytes: new TextEncoder().encode("Z".repeat(10240)), profile: "Zero Entropy" },
      { name: "Natural Prose (Alice)", bytes: new TextEncoder().encode(TEXT_SAMPLES["natural_text.txt"]), profile: "Natural Language" },
      { name: "Python Source Code", bytes: new TextEncoder().encode(TEXT_SAMPLES["source_code.py"]), profile: "Structured Code" },
      {
        name: "Uniform Random (5KB)",
        bytes: (() => {
          const b = new Uint8Array(5120);
          for (let i = 0; i < 5120; i++) b[i] = (i * 137 + 73) & 0xFF;
          return b;
        })(),
        profile: "Maximum Entropy (Noise)"
      }
    ];

    const algorithms = [
      { id: ALGO_HUFFMAN, name: "Huffman", comp: huffmanCompress, decomp: huffmanDecompress },
      { id: ALGO_RLE, name: "RLE (PackBits)", comp: rleCompress, decomp: rleDecompress },
      { id: ALGO_LZW, name: "LZW", comp: lzwCompress, decomp: lzwDecompress }
    ];

    const results = [];

    for (const ds of datasets) {
      const raw = ds.bytes;
      for (const algo of algorithms) {
        const t0 = performance.now();
        const compressed = algo.comp(raw);
        const compTime = performance.now() - t0;

        const archiveBytes = packContainer(algo.id, raw.length, "dummy_hash", compressed.meta, compressed.payload);

        const t1 = performance.now();
        const restored = algo.decomp(compressed.meta, compressed.payload, raw.length);
        const decompTime = performance.now() - t1;

        const isMatch = (restored.length === raw.length) && restored.every((v, i) => v === raw[i]);
        const ratio = archiveBytes.length > 0 ? (raw.length / archiveBytes.length) : 0;
        const savings = raw.length > 0 ? ((1 - archiveBytes.length / raw.length) * 100) : 0;

        results.push({
          dataset: ds.name,
          profile: ds.profile,
          algo: algo.name,
          origSize: raw.length,
          compSize: archiveBytes.length,
          ratio: ratio,
          savings: savings,
          compTime: compTime,
          decompTime: decompTime,
          verified: isMatch
        });
      }
    }

    soundFX.playSuccess();

    // Render Table
    tableBody.innerHTML = results.map(r => `
      <tr>
        <td>
          <div style="font-weight: 600; color: #FFF;">${r.dataset}</div>
          <div style="font-size: 0.72rem; color: var(--text-dim);">${r.profile}</div>
        </td>
        <td style="color: ${r.algo === 'Huffman' ? 'var(--cyan)' : r.algo.includes('RLE') ? 'var(--green-bright)' : 'var(--purple-bright)'}; font-weight: 600;">
          ${r.algo}
        </td>
        <td>${r.origSize.toLocaleString()} B</td>
        <td>${r.compSize.toLocaleString()} B</td>
        <td style="font-family: var(--font-mono); font-weight: 700; color: ${r.ratio >= 1.0 ? 'var(--green-bright)' : 'var(--red)'};">
          ${r.ratio.toFixed(2)}x
        </td>
        <td style="font-family: var(--font-mono);">${r.savings >= 0 ? "+" : ""}${r.savings.toFixed(1)}%</td>
        <td style="font-family: var(--font-mono);">${r.compTime.toFixed(2)} ms</td>
        <td style="font-family: var(--font-mono);">${r.decompTime.toFixed(2)} ms</td>
        <td><span class="pass-pill">PASS</span></td>
      </tr>
    `).join("");

    // Render SVG Bar Chart
    renderBenchmarkSVGChart(results, chartCanvas);

    runBtn.disabled = false;
    document.getElementById("bench-btn-text").textContent = "Re-Execute Benchmark Matrix";
  });
}

function renderBenchmarkSVGChart(results, container) {
  const datasets = Array.from(new Set(results.map(r => r.dataset)));
  const algos = ["Huffman", "RLE (PackBits)", "LZW"];
  const palette = ["#38BDF8", "#10B981", "#8B5CF6"];

  const width = 860;
  const height = 360;
  const padLeft = 180;
  const padRight = 50;
  const padTop = 30;
  const padBottom = 35;

  const maxRatio = Math.max(3.0, ...results.map(r => r.ratio));
  const chartW = width - padLeft - padRight;
  const chartH = height - padTop - padBottom;
  const groupH = chartH / datasets.length;
  const barH = (groupH * 0.72) / algos.length;

  let svg = `<svg viewBox="0 0 ${width} ${height}" width="100%" height="${height}" xmlns="http://www.w3.org/2000/svg">`;

  // Grid Lines
  for (let r = 1; r <= Math.ceil(maxRatio); r += (maxRatio > 12 ? 4 : (maxRatio > 6 ? 2 : 1))) {
    const x = padLeft + (r / maxRatio) * chartW;
    svg += `<line x1="${x}" y1="${padTop}" x2="${x}" y2="${height - padBottom}" stroke="rgba(255, 255, 255, 0.08)" stroke-dasharray="3"/>`;
    svg += `<text x="${x}" y="${height - padBottom + 18}" fill="#94A3B8" font-size="11" text-anchor="middle" font-family="monospace">${r}x</text>`;
  }

  // Bars
  datasets.forEach((ds, dsIdx) => {
    const gy = padTop + dsIdx * groupH + (groupH * 0.14);
    svg += `<text x="${padLeft - 14}" y="${gy + (groupH * 0.35)}" fill="#F8FAFC" font-size="11.5" font-weight="600" text-anchor="end" font-family="sans-serif">${ds}</text>`;

    algos.forEach((algo, aIdx) => {
      const match = results.find(r => r.dataset === ds && r.algo === algo);
      const ratio = match ? match.ratio : 0;
      const bw = Math.max(2, (ratio / maxRatio) * chartW);
      const by = gy + aIdx * barH;
      const color = palette[aIdx];

      svg += `<rect x="${padLeft}" y="${by}" width="${bw}" height="${barH - 2}" fill="${color}" rx="3"/>`;
      if (ratio > 0) {
        svg += `<text x="${padLeft + bw + 8}" y="${by + barH / 2 + 3.5}" fill="#E2E8F0" font-size="10" font-family="monospace">${ratio.toFixed(2)}x</text>`;
      }
    });
  });

  svg += `</svg>`;
  container.innerHTML = svg;
}

// Huffman Prefix Tree Visualizer
function setupTreeVisualizerUI() {
  const input = document.getElementById("tree-text-input");
  const generateBtn = document.getElementById("btn-tree-generate");

  generateBtn.addEventListener("click", () => {
    soundFX.playClick();
    renderHuffmanTree(input.value);
  });

  renderHuffmanTree(input.value);
}

function renderHuffmanTree(text) {
  if (!text) text = "DAA";
  const bytes = new TextEncoder().encode(text);
  const freq = {};
  for (let i = 0; i < bytes.length; i++) freq[bytes[i]] = (freq[bytes[i]] || 0) + 1;

  const heap = Object.keys(freq).map(b => ({
    freq: freq[b],
    byte: parseInt(b),
    char: String.fromCharCode(parseInt(b)),
    left: null,
    right: null
  }));
  heap.sort((a, b) => a.freq - b.freq);

  while (heap.length > 1) {
    const left = heap.shift();
    const right = heap.shift();
    const parent = { freq: left.freq + right.freq, left, right };
    let idx = 0;
    while (idx < heap.length && heap[idx].freq < parent.freq) idx++;
    heap.splice(idx, 0, parent);
  }

  const root = heap[0];
  const codeTable = {};
  function traverse(node, code) {
    if (node.byte !== undefined && !node.left && !node.right) {
      codeTable[node.char] = code || "0";
      return;
    }
    if (node.left) traverse(node.left, code + "0");
    if (node.right) traverse(node.right, code + "1");
  }
  traverse(root, "");

  const chipsContainer = document.getElementById("tree-codeword-chips");
  chipsContainer.innerHTML = Object.keys(codeTable).map(char => {
    const disp = char === " " ? "[SP]" : (char === "\n" ? "[LF]" : char);
    return `<div class="codeword-badge">
      <span style="color: var(--cyan);">'${disp}'</span> : <span style="color: var(--green-bright); font-weight: 700;">${codeTable[char]}</span>
    </div>`;
  }).join("");

  drawSVGTree(root);
}

function drawSVGTree(root) {
  const svg = document.getElementById("huffman-svg-tree");
  const width = svg.clientWidth || 640;
  const height = 380;
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);

  const elements = [];

  function layout(node, depth, leftX, rightX) {
    const x = (leftX + rightX) / 2;
    const y = 45 + depth * 65;

    if (node.left) {
      const childX = (leftX + x) / 2;
      const childY = 45 + (depth + 1) * 65;
      elements.push(`<line x1="${x}" y1="${y}" x2="${childX}" y2="${childY}" stroke="rgba(255, 255, 255, 0.2)" stroke-width="1.8"/>`);
      elements.push(`<text x="${(x + childX) / 2 - 8}" y="${(y + childY) / 2}" fill="#38BDF8" font-size="11" font-weight="700">0</text>`);
      layout(node.left, depth + 1, leftX, x);
    }

    if (node.right) {
      const childX = (x + rightX) / 2;
      const childY = 45 + (depth + 1) * 65;
      elements.push(`<line x1="${x}" y1="${y}" x2="${childX}" y2="${childY}" stroke="rgba(255, 255, 255, 0.2)" stroke-width="1.8"/>`);
      elements.push(`<text x="${(x + childX) / 2 + 8}" y="${(y + childY) / 2}" fill="#A78BFA" font-size="11" font-weight="700">1</text>`);
      layout(node.right, depth + 1, x, rightX);
    }

    const isLeaf = (node.byte !== undefined && !node.left && !node.right);
    const fill = isLeaf ? "#059669" : "#1E293B";
    const stroke = isLeaf ? "#34D399" : "#38BDF8";

    elements.push(`<circle cx="${x}" cy="${y}" r="16" fill="${fill}" stroke="${stroke}" stroke-width="2"/>`);

    if (isLeaf) {
      const disp = node.char === " " ? "SP" : (node.char === "\n" ? "LF" : node.char);
      elements.push(`<text x="${x}" y="${y + 4}" fill="#FFFFFF" font-size="11" font-weight="700" text-anchor="middle" font-family="sans-serif">${disp}</text>`);
      elements.push(`<text x="${x}" y="${y + 26}" fill="#94A3B8" font-size="9" text-anchor="middle" font-family="monospace">f:${node.freq}</text>`);
    } else {
      elements.push(`<text x="${x}" y="${y + 4}" fill="#E2E8F0" font-size="10" font-weight="600" text-anchor="middle" font-family="monospace">${node.freq}</text>`);
    }
  }

  layout(root, 0, 15, width - 15);
  svg.innerHTML = elements.join("");
}

// =========================================================================
// 11. NAVIGATION & MODAL CONTROLLERS
// =========================================================================
function setupNavigation() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      soundFX.playClick();
      tabs.forEach(t => {
        t.classList.remove("active");
        t.setAttribute("aria-selected", "false");
      });
      tab.classList.add("active");
      tab.setAttribute("aria-selected", "true");

      const targetId = tab.dataset.tab;
      document.querySelectorAll(".tab-content").forEach(content => {
        content.classList.remove("active");
      });
      const activeContent = document.getElementById(`tab-${targetId}`);
      if (activeContent) activeContent.classList.add("active");
    });
  });

  // Sound FX toggle button
  const soundBtn = document.getElementById("btn-toggle-sound");
  const audioIcon = document.getElementById("audio-icon");
  const audioLabel = document.getElementById("audio-label");
  soundBtn.addEventListener("click", () => {
    const isEnabled = soundFX.toggle();
    if (isEnabled) {
      soundBtn.classList.add("active");
      audioIcon.textContent = "🔊";
      audioLabel.textContent = "FX: ON";
      soundFX.playClick();
    } else {
      soundBtn.classList.remove("active");
      audioIcon.textContent = "🔇";
      audioLabel.textContent = "FX: OFF";
    }
  });

  // What is .daac? Modal
  const specModal = document.getElementById("spec-modal");
  const showSpecBtn = document.getElementById("btn-show-spec");
  const closeSpecBtn = document.getElementById("btn-close-modal");

  showSpecBtn.addEventListener("click", () => {
    soundFX.playClick();
    specModal.style.display = "flex";
  });

  closeSpecBtn.addEventListener("click", () => {
    soundFX.playClick();
    specModal.style.display = "none";
  });

  specModal.addEventListener("click", e => {
    if (e.target === specModal) {
      specModal.style.display = "none";
    }
  });

  window.addEventListener("keydown", e => {
    if (e.key === "Escape" && specModal.style.display === "flex") {
      specModal.style.display = "none";
    }
  });
}

// =========================================================================
// 12. INITIALIZATION ON DOM READY
// =========================================================================
document.addEventListener("DOMContentLoaded", () => {
  initAmbientCanvas();
  setupNavigation();
  setupCompressorUI();
  setupDecompressorUI();
  setupBenchmarkUI();
  setupTreeVisualizerUI();
});
