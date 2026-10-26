"""
FastAPI backend for DAA File Compression Tool
Exposes Python compressors through REST API
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
import tempfile
import os
import json
from pathlib import Path

from algorithms.huffman import HuffmanCompressor
from algorithms.rle import RLECompressor
from algorithms.lzw import LZWCompressor
from utils.file_io import ContainerFile, ALGO_HUFFMAN, ALGO_RLE, ALGO_LZW
from benchmark import BenchmarkSuite

app = FastAPI(
    title="DAA Compression API",
    description="Lossless Compression API using Huffman, RLE (PackBits), and LZW",
    version="1.0.0"
)

# Enable CORS for frontend
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
    return {"message": "DAA Compression API", "algorithms": ["huffman", "rle", "lzw"]}

@app.post("/compress")
async def compress_file(
    file: UploadFile = File(...),
    algorithm: str = Form(...)
):
    if algorithm not in compressors:
        raise HTTPException(status_code=400, detail="Invalid algorithm. Use huffman, rle, or lzw")
    
    try:
        # Read file
        contents = await file.read()
        data = bytes(contents)
        
        # Compress
        compressor = compressors[algorithm]
        metadata, compressed_payload = compressor.compress(data)
        
        # Create container
        container = ContainerFile(algorithm=algo_map[algorithm])
        container.build(compressed_payload, metadata, original_size=len(data))
        packed = container.pack()
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.daac') as tmp:
            tmp.write(packed)
            tmp_path = tmp.name
        
        return FileResponse(
            tmp_path,
            media_type='application/octet-stream',
            filename=f"{Path(file.filename).stem}.daac"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/decompress")
async def decompress_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        data = bytes(contents)
        
        # Parse container
        container = ContainerFile()
        container.unpack(data)
        
        # Get algorithm
        algo_id = container.header.algorithm_id
        if algo_id == ALGO_HUFFMAN:
            comp = compressors['huffman']
        elif algo_id == ALGO_RLE:
            comp = compressors['rle']
        elif algo_id == ALGO_LZW:
            comp = compressors['lzw']
        else:
            raise HTTPException(status_code=400, detail="Unknown algorithm")
        
        # Decompress
        result = comp.decompress(container.metadata, container.payload, container.header.original_size)
        
        # Verify checksum if present
        verification = {"verified": False, "message": "No checksum"}
        if len(container.header.sha256) == 32:
            import hashlib
            calc_hash = hashlib.sha256(result).digest()
            if calc_hash == bytes(container.header.sha256):
                verification = {"verified": True, "message": "SHA-256 verification passed"}
            else:
                verification = {"verified": False, "message": "SHA-256 verification failed"}
        
        # Save result
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(result)
            tmp_path = tmp.name
        
        return FileResponse(
            tmp_path,
            media_type='application/octet-stream',
            filename=f"restored_{Path(file.filename).stem}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/inspect")
async def inspect_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        data = bytes(contents)
        
        container = ContainerFile()
        container.unpack(data)
        
        algo_names = {1: "Huffman Coding", 2: "Run-Length Encoding (PackBits)", 3: "LZW Compression"}
        
        import hashlib
        header_bytes = data[:50]
        meta_bytes = data[50:50 + container.header.metadata_length] if container.header.metadata_length > 0 else b""
        
        return {
            "magic": container.header.magic.hex(),
            "version": container.header.version,
            "algorithm_id": container.header.algorithm_id,
            "algorithm_name": algo_names.get(container.header.algorithm_id, "Unknown"),
            "original_size": container.header.original_size,
            "metadata_length": container.header.metadata_length,
            "sha256": bytes(container.header.sha256).hex(),
            "header_hex": header_bytes.hex(),
            "metadata_hex": meta_bytes.hex() if meta_bytes else "",
            "payload_size": len(container.payload),
            "total_size": len(data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/benchmark")
async def run_benchmark():
    try:
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
