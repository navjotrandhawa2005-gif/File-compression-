"""
FastAPI backend for DAA File Compression Tool
Exposes Python compressors through REST API
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Optional
import tempfile
import os
from pathlib import Path
import hashlib

from algorithms.huffman import HuffmanCompressor
from algorithms.rle import RLECompressor
from algorithms.lzw import LZWCompressor
from utils.file_io import ContainerFile, ALGO_HUFFMAN, ALGO_RLE, ALGO_LZW, compute_sha256

app = FastAPI(
    title="DAA Compression API",
    description="Lossless Compression API using Huffman, RLE (PackBits), and LZW",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

compressors = {
    'huffman': HuffmanCompressor(),
    'rle': RLECompressor(),
    'lzw': LZWCompressor()
}

algo_map = {
    'huffman': ALGO_HUFFMAN,
    'rle': ALGO_RLE,
    'lzw': ALGO_LZW
}

@app.get("/")
def root():
    return {"message": "DAA Compression API", "algorithms": ["auto", "huffman", "lzw", "rle"]}

@app.post("/compress")
async def compress_file(
    file: UploadFile = File(...),
    algorithm: str = Form("auto")
):
    valid_algos = ["auto", "huffman", "lzw", "rle"]
    if algorithm not in valid_algos:
        raise HTTPException(status_code=400, detail="Invalid algorithm. Choose auto, huffman, lzw, or rle.")
    
    try:
        contents = await file.read()
        data = bytes(contents)
        sha = compute_sha256(data)
        
        if algorithm == "auto":
            candidates = []
            for a_key in ["lzw", "huffman", "rle"]:
                try:
                    c = compressors[a_key]
                    m, p = c.compress(data)
                    pk = ContainerFile.pack(algo_map[a_key], len(data), sha, m, p)
                    candidates.append((len(pk), a_key, pk))
                except Exception:
                    pass
            if candidates:
                candidates.sort(key=lambda x: x[0])
                best_size, chosen_algo, packed = candidates[0]
            else:
                chosen_algo = "huffman"
                m, p = compressors["huffman"].compress(data)
                packed = ContainerFile.pack(algo_map["huffman"], len(data), sha, m, p)
        else:
            chosen_algo = algorithm
            compressor = compressors[algorithm]
            metadata, compressed_payload = compressor.compress(data)
            packed = ContainerFile.pack(algo_map[algorithm], len(data), sha, metadata, compressed_payload)
        
        orig_name = file.filename or "file.bin"
        ext = Path(orig_name).suffix
        comp_name = orig_name if orig_name.startswith("compressed_") else f"compressed_{orig_name}"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext or '.bin') as tmp:
            tmp.write(packed)
            tmp_path = tmp.name
        
        headers = {
            "X-Chosen-Algorithm": chosen_algo,
            "X-Original-Size": str(len(data)),
            "X-Compressed-Size": str(len(packed)),
            "Access-Control-Expose-Headers": "X-Chosen-Algorithm, X-Original-Size, X-Compressed-Size, Content-Disposition"
        }
        
        return FileResponse(
            tmp_path,
            media_type='application/octet-stream',
            filename=comp_name,
            headers=headers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/decompress")
async def decompress_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        data = bytes(contents)
        
        if len(data) >= 4 and data[:4] == b"DAAC":
            header, metadata, compressed_payload = ContainerFile.unpack(data)
            algo_id = header.algorithm_id
            if algo_id == ALGO_HUFFMAN:
                comp = compressors['huffman']
            elif algo_id == ALGO_RLE:
                comp = compressors['rle']
            elif algo_id == ALGO_LZW:
                comp = compressors['lzw']
            else:
                raise HTTPException(status_code=400, detail="Unknown algorithm")
            
            result = comp.decompress(metadata, compressed_payload, header.original_size)
        else:
            # Direct binary (e.g. directly compressed image)
            result = data
        
        # Restore original extension and filename without 'compressed_'
        orig_name = file.filename or "file.bin"
        if orig_name.startswith("compressed_"):
            restored_name = orig_name[len("compressed_"):]
        elif orig_name.endswith(".daac"):
            restored_name = orig_name[:-5]
        elif orig_name.startswith("restored_"):
            restored_name = orig_name
        else:
            restored_name = f"restored_{orig_name}"

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(result)
            tmp_path = tmp.name
        
        return FileResponse(
            tmp_path,
            media_type='application/octet-stream',
            filename=restored_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/inspect")
async def inspect_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        data = bytes(contents)
        
        header, metadata, compressed_payload = ContainerFile.unpack(data)
        
        algo_names = {1: "Huffman Coding", 2: "Run-Length Encoding (PackBits)", 3: "LZW Compression"}
        
        return {
            "magic": "DAAC",
            "version": header.version,
            "algorithm_id": header.algorithm_id,
            "algorithm_name": algo_names.get(header.algorithm_id, "Unknown"),
            "original_size": header.original_size,
            "metadata_length": len(metadata),
            "sha256": header.sha256_hash.hex(),
            "header_hex": data[:50].hex(),
            "payload_size": len(compressed_payload),
            "total_size": len(data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/benchmark")
async def run_benchmark():
    try:
        from benchmark import BenchmarkSuite
        suite = BenchmarkSuite()
        results = suite.run_full_benchmark()
        summary = suite.generate_summary()
        return {
            "results": results,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
