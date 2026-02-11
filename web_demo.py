"""AnchorStage v2.0 — Visual Web Demo (FastAPI backend)."""
from __future__ import annotations

import base64
import io
import math
import os
import struct
import tempfile
import time
from pathlib import Path

import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response
from PIL import Image
from pydantic import BaseModel

from anchorstage.math3d import intrinsics_from_camera
from anchorstage.models import Camera
from anchorstage.pipeline import AnchorStagePipeline

# ---------------------------------------------------------------------------
# App + pipeline init
# ---------------------------------------------------------------------------
app = FastAPI(title="AnchorStage v2.0 Demo")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

pipe = AnchorStagePipeline()
scene = None
captured_photos: list[dict] = []

# ---------------------------------------------------------------------------
# Apple SHARP integration (RunPod > HuggingFace Space > DPT fallback)
# ---------------------------------------------------------------------------
_sharp_client = None
_sharp_ply_path: str | None = None
_uploaded_image_path: str | None = None

SHARP_SPACE = "gagndeep/Apple-Sharp-Image-to-3D-View-Synthesis"
RUNPOD_API_KEY = os.environ.get("RUNPOD_API_KEY")
RUNPOD_ENDPOINT_ID = os.environ.get("RUNPOD_ENDPOINT_ID")
RUNPOD_POD_URL = os.environ.get("RUNPOD_POD_URL")  # e.g. https://POD_ID-8080.proxy.runpod.net

# DPT depth estimation (fallback for point cloud when SHARP unavailable)
_depth_pipeline = None
_midas_depth_cache: np.ndarray | None = None


def _get_depth_pipeline():
    global _depth_pipeline
    if _depth_pipeline is None:
        from transformers import pipeline as tf_pipeline
        _depth_pipeline = tf_pipeline(
            "depth-estimation",
            model="Intel/dpt-hybrid-midas",
            device=-1,
        )
    return _depth_pipeline


def _estimate_ml_depth(image_01: np.ndarray) -> np.ndarray:
    """Run DPT/MiDaS depth estimation. Returns depth map in meters."""
    from PIL import Image as PILImage
    h, w = image_01.shape[:2]
    img_u8 = (np.clip(image_01, 0, 1) * 255).astype(np.uint8)
    pil_img = PILImage.fromarray(img_u8)
    p = _get_depth_pipeline()
    result = p(pil_img)
    depth_pil = result["depth"]
    depth_arr = np.array(depth_pil, dtype=np.float32)
    if depth_arr.shape[:2] != (h, w):
        depth_pil = depth_pil.resize((w, h), PILImage.BILINEAR)
        depth_arr = np.array(depth_pil, dtype=np.float32)
    d_min, d_max = depth_arr.min(), depth_arr.max()
    disp_norm = (depth_arr - d_min) / (d_max - d_min + 1e-8)
    depth_metric = 2.5 + (1.0 - disp_norm) * 1.0
    return depth_metric.astype(np.float32)


def _run_sharp_pod(image_path: str) -> str:
    """Call SHARP via RunPod GPU Pod direct API. Returns path to saved PLY."""
    import requests
    print(f"[SHARP] Using RunPod Pod at {RUNPOD_POD_URL}")
    headers = {}
    if RUNPOD_API_KEY:
        headers["Authorization"] = f"Bearer {RUNPOD_API_KEY}"
    with open(image_path, "rb") as f:
        resp = requests.post(
            f"{RUNPOD_POD_URL}/predict_raw",
            files={"file": ("image.jpg", f, "image/jpeg")},
            headers=headers,
            timeout=180,
        )
    resp.raise_for_status()
    ply_bytes = resp.content
    ply_file = tempfile.NamedTemporaryFile(suffix=".ply", delete=False)
    ply_file.write(ply_bytes)
    ply_file.close()
    print(f"[SHARP] Pod done: {len(ply_bytes)/1024/1024:.1f} MB PLY")
    return ply_file.name


def _run_sharp_serverless(image_path: str) -> str:
    """Call SHARP via RunPod Serverless. Returns path to saved PLY file."""
    import base64 as b64mod
    import requests
    print(f"[SHARP] Using RunPod Serverless endpoint {RUNPOD_ENDPOINT_ID}")
    with open(image_path, "rb") as f:
        image_b64 = b64mod.b64encode(f.read()).decode("ascii")
    resp = requests.post(
        f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT_ID}/runsync",
        headers={"Authorization": f"Bearer {RUNPOD_API_KEY}"},
        json={"input": {"image_b64": image_b64}},
        timeout=180,
    )
    resp.raise_for_status()
    data = resp.json()
    print(f"[SHARP] RunPod response status: {data.get('status')}")
    print(f"[SHARP] RunPod response keys: {list(data.keys())}")
    if data.get("status") == "FAILED":
        raise RuntimeError(f"RunPod job failed: {data}")
    output = data.get("output", {})
    if isinstance(output, str):
        raise RuntimeError(f"SHARP returned string: {output[:500]}")
    if "error" in output:
        raise RuntimeError(f"SHARP error: {output['error']} {output.get('traceback','')[:500]}")
    if "ply_b64" not in output:
        raise RuntimeError(f"SHARP missing ply_b64. Output keys: {list(output.keys()) if isinstance(output, dict) else type(output)}")
    ply_bytes = b64mod.b64decode(output["ply_b64"])
    ply_file = tempfile.NamedTemporaryFile(suffix=".ply", delete=False)
    ply_file.write(ply_bytes)
    ply_file.close()
    print(f"[SHARP] Serverless done: {output.get('num_splats',0)} splats, "
          f"{output.get('elapsed_s',0)}s")
    return ply_file.name


def _get_sharp_client():
    global _sharp_client
    if _sharp_client is None:
        from gradio_client import Client
        hf_token = os.environ.get("HF_TOKEN")
        _sharp_client = Client(SHARP_SPACE, token=hf_token, httpx_kwargs={"timeout": 300})
    return _sharp_client


def _run_sharp_hf(image_path: str) -> str:
    """Call SHARP via HuggingFace Space. Returns path to downloaded PLY."""
    print("[SHARP] Using HuggingFace Space (may be slow)")
    client = _get_sharp_client()
    from gradio_client import handle_file
    result = client.predict(
        image_path=handle_file(image_path),
        trajectory_type="rotate_forward",
        output_long_side=512,
        num_frames=24,
        fps=30,
        render_video=False,
        api_name="/run_sharp",
    )
    ply_result = result[1]
    if isinstance(ply_result, dict):
        return ply_result.get("value", ply_result)
    return ply_result


def _run_sharp(image_path: str) -> str:
    """Run SHARP via best available backend: Pod > Serverless > HuggingFace."""
    if RUNPOD_POD_URL:
        return _run_sharp_pod(image_path)
    if RUNPOD_API_KEY and RUNPOD_ENDPOINT_ID:
        return _run_sharp_serverless(image_path)
    if os.environ.get("HF_SHARP_ENABLED") == "1":
        return _run_sharp_hf(image_path)
    raise RuntimeError("No SHARP backend configured. "
                       "Set RUNPOD_POD_URL, or RUNPOD_API_KEY + RUNPOD_ENDPOINT_ID.")


def _parse_sharp_ply(ply_path: str) -> tuple[np.ndarray, np.ndarray]:
    """Parse SHARP PLY and return (positions Nx3, colors Nx3) as float32.
    Colors are converted from SH DC coefficients to linear RGB [0,1]."""
    with open(ply_path, "rb") as f:
        header = b""
        n_verts = 0
        while True:
            line = f.readline()
            header += line
            if line.startswith(b"element vertex"):
                n_verts = int(line.split()[-1])
            if b"end_header" in line:
                break
        # 14 floats per vertex: x,y,z, f_dc_0/1/2, opacity, scale_0/1/2, rot_0/1/2/3
        floats_per_vert = 14
        raw = np.frombuffer(
            f.read(n_verts * floats_per_vert * 4), dtype=np.float32
        ).reshape(n_verts, floats_per_vert)

    xyz = raw[:, 0:3].copy()
    fdc = raw[:, 3:6]
    opacity_logit = raw[:, 6]

    # SH DC to RGB: color = 0.5 + C0 * f_dc
    C0 = 0.2820947917738781
    rgb = np.clip(0.5 + C0 * fdc, 0.0, 1.0).astype(np.float32)

    # Filter out near-transparent splats
    opacity = 1.0 / (1.0 + np.exp(-opacity_logit))
    mask = opacity > 0.05
    return xyz[mask], rgb[mask]


def _strip_sharp_ply(src_path: str, dst_path: str):
    """Create a clean 3DGS PLY with only vertex data (no extra elements)."""
    with open(src_path, "rb") as f:
        header = b""
        n_verts = 0
        while True:
            line = f.readline()
            header += line
            if line.startswith(b"element vertex"):
                n_verts = int(line.split()[-1])
            if b"end_header" in line:
                break
        floats_per_vert = 14
        vertex_data = f.read(n_verts * floats_per_vert * 4)

    # Write clean PLY with only vertex element
    clean_header = (
        "ply\n"
        "format binary_little_endian 1.0\n"
        f"element vertex {n_verts}\n"
        "property float x\n"
        "property float y\n"
        "property float z\n"
        "property float f_dc_0\n"
        "property float f_dc_1\n"
        "property float f_dc_2\n"
        "property float opacity\n"
        "property float scale_0\n"
        "property float scale_1\n"
        "property float scale_2\n"
        "property float rot_0\n"
        "property float rot_1\n"
        "property float rot_2\n"
        "property float rot_3\n"
        "end_header\n"
    ).encode("ascii")
    with open(dst_path, "wb") as f:
        f.write(clean_header)
        f.write(vertex_data)


_sharp_parsed_cache: tuple[np.ndarray, np.ndarray] | None = None
_sharp_clean_ply: str | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _np_to_jpg_b64(arr: np.ndarray, colormap: str | None = None, quality: int = 85) -> str:
    """Convert numpy array to base64-encoded JPEG for fast transfer."""
    if arr.ndim == 2:
        if colormap == "depth":
            valid = arr[arr > 0]
            lo = float(valid.min()) if valid.size else 0.0
            hi = float(valid.max()) if valid.size else 1.0
            norm = np.clip((arr - lo) / (hi - lo + 1e-9), 0, 1)
            r = (norm * 80).astype(np.uint8)
            g = (norm * 140 + 40).astype(np.uint8)
            b = (norm * 220 + 35).astype(np.uint8)
            rgb = np.stack([r, g, b], axis=2)
        elif colormap == "normal":
            rgb = ((arr * 0.5 + 0.5) * 255).clip(0, 255).astype(np.uint8)
            if rgb.ndim == 2:
                rgb = np.stack([rgb, rgb, rgb], axis=2)
        elif colormap == "void":
            v = (arr * 255).astype(np.uint8)
            rgb = np.stack([v, np.zeros_like(v), np.zeros_like(v)], axis=2)
        elif colormap == "region":
            colours = np.array([
                [40, 40, 40], [230, 80, 80], [80, 200, 80], [80, 120, 230],
                [230, 200, 50], [200, 80, 230], [80, 220, 220],
            ], dtype=np.uint8)
            idx = arr.astype(np.int32) % len(colours)
            rgb = colours[idx]
        else:
            v = (np.clip(arr, 0, 1) * 255).astype(np.uint8)
            rgb = np.stack([v, v, v], axis=2)
    elif arr.ndim == 3 and arr.shape[2] == 3:
        if colormap == "normal":
            rgb = ((arr * 0.5 + 0.5) * 255).clip(0, 255).astype(np.uint8)
        else:
            rgb = (np.clip(arr, 0, 1) * 255).astype(np.uint8)
    else:
        rgb = (np.clip(arr, 0, 1) * 255).astype(np.uint8)

    img = Image.fromarray(rgb)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    return base64.b64encode(buf.getvalue()).decode()


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class GenerateRequest(BaseModel):
    pos_x: float = 0.0
    pos_y: float = 0.0
    pos_z: float = 0.0
    rot_x: float = 0.0
    rot_y: float = 0.0
    rot_z: float = 0.0
    focal_mm: float = 35.0
    width: int = 640
    height: int = 360


class LockRequest(BaseModel):
    region_id: str
    locked: bool


class CaptureRequest(BaseModel):
    pos_x: float = 0.0
    pos_y: float = 0.0
    pos_z: float = 0.0
    rot_x: float = 0.0
    rot_y: float = 0.0
    rot_z: float = 0.0
    focal_mm: float = 35.0


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload a user image and reconstruct the scene from it."""
    global scene, captured_photos, _sharp_ply_path, _uploaded_image_path, _midas_depth_cache, _sharp_parsed_cache, _sharp_clean_ply
    captured_photos = []
    _sharp_ply_path = None
    _midas_depth_cache = None
    _sharp_parsed_cache = None
    _sharp_clean_ply = None

    contents = await file.read()
    pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
    # Resize to reasonable dimensions for reconstruction
    max_dim = 960
    w, h = pil_img.size
    if max(w, h) > max_dim:
        scale = max_dim / max(w, h)
        pil_img = pil_img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    # Save image to temp file for SHARP processing
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    pil_img.save(tmp, format="JPEG", quality=95)
    tmp.close()
    _uploaded_image_path = tmp.name

    img_arr = np.array(pil_img, dtype=np.float32) / 255.0

    t0 = time.perf_counter()
    scene = pipe.create_scene(img_arr, scene_id="uploaded_scene")
    elapsed = time.perf_counter() - t0

    base_b64 = _np_to_jpg_b64(img_arr, quality=90)
    return {
        "scene_id": scene.scene_id,
        "num_splats": len(scene.gaussian_splats),
        "reconstruction_time_s": round(elapsed, 3),
        "image_size": [img_arr.shape[1], img_arr.shape[0]],
        "regions": [
            {
                "id": r.id,
                "label": r.semantic_label,
                "locked": r.locked,
                "pixel_count": int(r.mask.sum()),
            }
            for r in scene.regions
        ],
        "base_witness": base_b64,
    }


@app.post("/api/init")
async def init_scene():
    """Initialize with a synthetic image (fallback)."""
    global scene, captured_photos, _sharp_ply_path, _uploaded_image_path, _midas_depth_cache, _sharp_parsed_cache, _sharp_clean_ply
    captured_photos = []
    _sharp_ply_path = None
    _midas_depth_cache = None
    _sharp_parsed_cache = None
    _sharp_clean_ply = None
    h, w = 540, 960
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    xx = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    ones = np.ones((h, w), dtype=np.float32)
    r = 0.15 + 0.55 * (1.0 - yy) * ones
    g = 0.25 + 0.35 * xx * ones
    b = 0.45 + 0.35 * (yy * (1.0 - xx))
    img = np.clip(np.stack([r, g, b], axis=2), 0.0, 1.0)

    t0 = time.perf_counter()
    scene = pipe.create_scene(img, scene_id="synthetic_demo")
    elapsed = time.perf_counter() - t0
    base_b64 = _np_to_jpg_b64(img, quality=90)
    return {
        "scene_id": scene.scene_id,
        "num_splats": len(scene.gaussian_splats),
        "reconstruction_time_s": round(elapsed, 3),
        "image_size": [w, h],
        "regions": [
            {
                "id": r.id,
                "label": r.semantic_label,
                "locked": r.locked,
                "pixel_count": int(r.mask.sum()),
            }
            for r in scene.regions
        ],
        "base_witness": base_b64,
    }


@app.post("/api/generate")
async def generate_frame(req: GenerateRequest):
    if scene is None:
        return {"error": "No scene loaded. Upload an image first."}

    cam = Camera(
        position=np.array([req.pos_x, req.pos_y, req.pos_z], dtype=np.float32),
        rotation_xyz_deg=np.array([req.rot_x, req.rot_y, req.rot_z], dtype=np.float32),
        focal_length_mm=req.focal_mm,
        width=req.width,
        height=req.height,
    )

    t0 = time.perf_counter()
    frame = pipe.generate_frame(scene, cam, [])
    gen_time = time.perf_counter() - t0

    beauty_b64 = _np_to_jpg_b64(frame.beauty)

    void_ratio = float(frame.void_map.sum() / frame.void_map.size)
    conf = frame.metadata["confidence"]

    return {
        "beauty": beauty_b64,
        "generation_time_s": round(gen_time, 3),
        "confidence": conf,
        "void_ratio": round(void_ratio, 4),
    }


@app.post("/api/capture")
async def capture_photo(req: CaptureRequest):
    """Capture a high-quality photo at current camera position."""
    if scene is None:
        return {"error": "No scene loaded."}

    cam = Camera(
        position=np.array([req.pos_x, req.pos_y, req.pos_z], dtype=np.float32),
        rotation_xyz_deg=np.array([req.rot_x, req.rot_y, req.rot_z], dtype=np.float32),
        focal_length_mm=req.focal_mm,
        width=1280,
        height=720,
    )

    frame = pipe.generate_frame(scene, cam, [])
    beauty_b64 = _np_to_jpg_b64(frame.beauty, quality=95)

    photo = {
        "b64": beauty_b64,
        "camera": {
            "pos": [req.pos_x, req.pos_y, req.pos_z],
            "rot": [req.rot_x, req.rot_y, req.rot_z],
            "focal_mm": req.focal_mm,
        },
        "index": len(captured_photos) + 1,
    }
    captured_photos.append(photo)

    return {
        "photo": beauty_b64,
        "index": photo["index"],
        "total": len(captured_photos),
    }


@app.post("/api/lock")
async def lock_region(req: LockRequest):
    if scene is None:
        return {"error": "No scene loaded."}
    if req.locked:
        ok = pipe.lock_region(scene, req.region_id)
    else:
        ok = pipe.unlock_region(scene, req.region_id)
    return {
        "region_id": req.region_id,
        "locked": req.locked,
        "success": ok,
        "regions": [
            {"id": r.id, "label": r.semantic_label, "locked": r.locked}
            for r in scene.regions
        ],
    }


@app.get("/api/photos")
async def get_photos():
    return {"photos": [{"b64": p["b64"], "index": p["index"], "camera": p["camera"]} for p in captured_photos]}


async def _ensure_sharp():
    """Run SHARP if not cached. Returns True on success."""
    import asyncio
    global _sharp_ply_path, _sharp_parsed_cache, _sharp_clean_ply
    if _uploaded_image_path is None:
        return False
    if _sharp_ply_path and Path(_sharp_ply_path).exists():
        return True
    try:
        loop = asyncio.get_event_loop()
        _sharp_ply_path = await loop.run_in_executor(
            None, _run_sharp, _uploaded_image_path
        )
        _sharp_parsed_cache = None  # invalidate parsed cache
        _sharp_clean_ply = None
        return True
    except Exception as e:
        print(f"SHARP failed: {e}")
        return False


@app.get("/api/pointcloud.bin")
async def get_pointcloud_bin():
    """Serve point cloud — uses SHARP 3D data if available, else DPT depth."""
    global _midas_depth_cache, _sharp_parsed_cache
    if scene is None:
        return Response(content=b"", status_code=404)

    # Try SHARP first (real 3D positions from Apple SHARP)
    sharp_ok = await _ensure_sharp()
    if sharp_ok and _sharp_ply_path:
        if _sharp_parsed_cache is None:
            _sharp_parsed_cache = _parse_sharp_ply(_sharp_ply_path)
        positions, colors = _sharp_parsed_cache

        # SHARP uses OpenCV: x-right, y-down, z-forward
        # Three.js uses: x-right, y-up, z-toward-camera
        pos = positions.copy()
        pos[:, 1] = -pos[:, 1]  # flip Y for Three.js y-up

        # Downsample for GPU performance
        n = pos.shape[0]
        max_points = 800_000
        if n > max_points:
            stride = max(2, n // max_points)
            pos = pos[::stride]
            colors = colors[::stride]
    else:
        # Fallback: DPT depth estimation
        image = scene.base_witness
        h, w = image.shape[:2]
        cam = scene.base_camera
        k = intrinsics_from_camera(w, h, cam.focal_length_mm, cam.filmback_mm)
        if _midas_depth_cache is None or _midas_depth_cache.shape != (h, w):
            _midas_depth_cache = _estimate_ml_depth(image)
        depth = _midas_depth_cache
        uu = np.arange(w, dtype=np.float32)
        vv = np.arange(h, dtype=np.float32)
        u_grid, v_grid = np.meshgrid(uu, vv)
        x3d = -(u_grid - k.cx) * depth / k.fx
        y3d = -(v_grid - k.cy) * depth / k.fy
        z3d = depth
        pos = np.stack([x3d, y3d, z3d], axis=2).reshape(-1, 3).astype(np.float32)
        colors = image.reshape(-1, 3).astype(np.float32)
        n = pos.shape[0]
        max_points = 500_000
        if n > max_points:
            stride = max(2, n // max_points)
            pos = pos[::stride]
            colors = colors[::stride]

    # Interleave: [x,y,z, r,g,b] per point, float32
    n_out = pos.shape[0]
    data = np.zeros((n_out, 6), dtype=np.float32)
    data[:, 0:3] = pos
    data[:, 3:6] = colors

    header = np.array([n_out], dtype=np.uint32)
    buf = header.tobytes() + data.tobytes()
    return Response(content=buf, media_type="application/octet-stream")


@app.get("/api/splats.ply")
async def get_splats_ply():
    """Serve cleaned SHARP 3DGS PLY (extra elements stripped)."""
    global _sharp_clean_ply
    sharp_ok = await _ensure_sharp()
    if not sharp_ok or not _sharp_ply_path:
        return Response(content=b"SHARP not available", status_code=503)

    # Create cleaned PLY on first request
    if _sharp_clean_ply is None or not Path(_sharp_clean_ply).exists():
        clean_path = _sharp_ply_path + ".clean.ply"
        _strip_sharp_ply(_sharp_ply_path, clean_path)
        _sharp_clean_ply = clean_path

    return FileResponse(
        _sharp_clean_ply,
        media_type="application/octet-stream",
        filename="splats.ply",
    )
