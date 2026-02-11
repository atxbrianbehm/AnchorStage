#!/bin/bash
# =============================================================================
# SHARP API Server Setup for RunPod GPU Pod
# Run this once after pod creation. Takes ~3-5 minutes.
# =============================================================================
set -e

echo "=== Installing SHARP on RunPod GPU Pod ==="

# Clone and install SHARP
cd /workspace
if [ ! -d "ml-sharp" ]; then
    git clone https://github.com/apple/ml-sharp.git
fi
cd ml-sharp
pip install -r requirements.txt 2>&1 | tail -5

# Download model checkpoint
CKPT_DIR="$HOME/.cache/torch/hub/checkpoints"
CKPT_FILE="$CKPT_DIR/sharp_2572gikvuh.pt"
mkdir -p "$CKPT_DIR"
if [ ! -f "$CKPT_FILE" ]; then
    echo "Downloading SHARP model checkpoint (~400MB)..."
    wget -q --show-progress -O "$CKPT_FILE" \
        https://ml-site.cdn-apple.com/models/sharp/sharp_2572gikvuh.pt
fi

# Verify
echo "=== Verifying installation ==="
sharp --help | head -3

# Install API server deps
pip install fastapi uvicorn python-multipart 2>&1 | tail -3

# Create the API server
cat > /workspace/sharp_api.py << 'PYEOF'
"""Minimal SHARP API server for RunPod GPU Pod."""
import base64
import glob
import os
import subprocess
import tempfile
import time

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

app = FastAPI(title="SHARP API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
async def health():
    return {"status": "ok", "model": "SHARP"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Accept image upload, return PLY as base64 JSON."""
    contents = await file.read()

    with tempfile.TemporaryDirectory() as work_dir:
        input_dir = os.path.join(work_dir, "input")
        output_dir = os.path.join(work_dir, "output")
        os.makedirs(input_dir)
        os.makedirs(output_dir)

        img_path = os.path.join(input_dir, "image.jpg")
        with open(img_path, "wb") as f:
            f.write(contents)

        t0 = time.time()
        result = subprocess.run(
            ["sharp", "predict", "-i", input_dir, "-o", output_dir],
            capture_output=True, text=True, timeout=120,
        )
        elapsed = time.time() - t0

        if result.returncode != 0:
            return JSONResponse(
                {"error": f"sharp predict failed", "stderr": result.stderr[-2000:]},
                status_code=500,
            )

        plys = glob.glob(os.path.join(output_dir, "**", "*.ply"), recursive=True)
        if not plys:
            return JSONResponse({"error": "No PLY output"}, status_code=500)

        with open(plys[0], "rb") as f:
            ply_bytes = f.read()

    # Count splats
    num_splats = 0
    header_text = ply_bytes[:2000].decode("ascii", errors="replace")
    for line in header_text.split("\n"):
        if line.startswith("element vertex"):
            num_splats = int(line.split()[-1])
            break

    return {
        "ply_b64": base64.b64encode(ply_bytes).decode("ascii"),
        "num_splats": num_splats,
        "elapsed_s": round(elapsed, 2),
        "ply_size_mb": round(len(ply_bytes) / 1024 / 1024, 1),
    }


@app.post("/predict_raw")
async def predict_raw(file: UploadFile = File(...)):
    """Accept image upload, return raw PLY bytes (faster, no base64 overhead)."""
    contents = await file.read()

    with tempfile.TemporaryDirectory() as work_dir:
        input_dir = os.path.join(work_dir, "input")
        output_dir = os.path.join(work_dir, "output")
        os.makedirs(input_dir)
        os.makedirs(output_dir)

        img_path = os.path.join(input_dir, "image.jpg")
        with open(img_path, "wb") as f:
            f.write(contents)

        subprocess.run(
            ["sharp", "predict", "-i", input_dir, "-o", output_dir],
            capture_output=True, text=True, timeout=120, check=True,
        )

        plys = glob.glob(os.path.join(output_dir, "**", "*.ply"), recursive=True)
        if not plys:
            return Response(content=b"No PLY output", status_code=500)

        with open(plys[0], "rb") as f:
            ply_bytes = f.read()

    return Response(content=ply_bytes, media_type="application/octet-stream")

PYEOF

echo ""
echo "=== Setup complete! ==="
echo ""
echo "To start the SHARP API server, run:"
echo "  python -m uvicorn sharp_api:app --host 0.0.0.0 --port 8080"
echo ""
echo "Then set these env vars on your local machine:"
echo '  $env:RUNPOD_POD_URL = "https://YOUR_POD_ID-8080.proxy.runpod.net"'
echo ""
