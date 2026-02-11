from __future__ import annotations

import tempfile

import numpy as np

from .models import Camera, ExtraAsset
from .pipeline import AnchorStagePipeline


def _make_synthetic_image(h: int = 540, w: int = 960) -> np.ndarray:
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    xx = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    ones = np.ones((h, w), dtype=np.float32)
    r = 0.15 + 0.55 * (1.0 - yy) * ones
    g = 0.25 + 0.35 * xx * ones
    b = 0.45 + 0.35 * (yy * (1.0 - xx))
    img = np.stack([r, g, b], axis=2)
    return np.clip(img, 0.0, 1.0)


def _make_sprite(color: tuple[float, float, float]) -> np.ndarray:
    h, w = 48, 32
    sprite = np.zeros((h, w, 4), dtype=np.float32)
    sprite[:, :, :3] = np.array(color, dtype=np.float32)[None, None, :]
    sprite[:, :, 3] = 0.85
    # Transparent corners to fake silhouette.
    sprite[:6, :6, 3] = 0.0
    sprite[:6, -6:, 3] = 0.0
    return sprite


def main() -> None:
    pipe = AnchorStagePipeline()
    image = _make_synthetic_image()

    # --- S2: SHARP-inspired reconstruction with timer ---
    print("=" * 60)
    print("AnchorStage v2.0 Demo — SHARP-Enhanced MVP")
    print("=" * 60)
    scene = pipe.create_scene(image, scene_id="demo_scene_001")
    print(f"\n[Reconstruction] Completed in {scene.reconstruction_time_s:.3f}s")
    print(f"  Gaussian splats: {len(scene.gaussian_splats):,}")
    print(f"  Metric scale: {scene.metric_scale}")
    print(f"  Normal map: {scene.normal_map.shape}")

    # --- Region segmentation ---
    print(f"\n[Regions] {len(scene.regions)} auto-detected:")
    for r in scene.regions:
        px_count = int(r.mask.sum())
        plane_str = f", plane={r.plane_params.tolist()}" if r.plane_params is not None else ""
        print(f"  - {r.id} ({r.semantic_label}): {px_count:,} px, locked={r.locked}{plane_str}")

    # --- Lock facade region for demo ---
    locked = pipe.lock_region(scene, "facade_001")
    if locked:
        print("\n[Region Lock] facade_001 locked for preservation")

    # --- S4: Configure extras (region-aware) ---
    assets = [
        ExtraAsset("walker_a", _make_sprite((0.95, 0.55, 0.35)), 1.7, 0.0, "walk", 1.0),
        ExtraAsset("idle_a", _make_sprite((0.35, 0.75, 0.95)), 1.6, 0.0, "idle", 0.0),
    ]
    pipe.configure_extras(scene, assets, density=30, motion_mix={"walk": 0.7, "idle": 0.3}, seed=12)

    # --- S3: Metric-aware camera with position display ---
    cam = Camera(
        position=np.array([0.22, 0.0, 0.0], dtype=np.float32),
        rotation_xyz_deg=np.array([0.0, 4.0, 0.0], dtype=np.float32),
        focal_length_mm=35.0,
        filmback_mm=36.0,
        width=1280,
        height=720,
    )
    print(f"\n[Camera] Metric position: {cam.position.tolist()}")
    print(f"  Focal length: {cam.focal_length_mm}mm")

    # --- S5: Generate frame with all v2.0 features ---
    frame = pipe.generate_frame(scene, cam, assets)
    void_ratio = float(frame.void_map.sum() / frame.void_map.size)

    print(f"\n[Frame Generated]")
    print(f"  Beauty: {frame.beauty.shape}")
    print(f"  Depth (metric): {frame.depth.shape}")
    print(f"  Normal map: {frame.normal_map.shape}")
    print(f"  Void map: {frame.void_map.shape} (void ratio: {void_ratio:.4f})")
    print(f"  Region masks: {len(frame.region_masks)} passes")

    # --- Enhanced confidence (3-factor) ---
    meta = frame.metadata
    conf = meta["confidence"]
    depth_c = conf["depth_confidence"]
    angle_c = conf["angle_confidence"]
    overall = conf["overall"]
    # Back-derive void_factor from the 3-factor product
    void_factor = overall / max(depth_c * angle_c, 1e-9)
    print(f"\n[Confidence] Enhanced 3-factor formula:")
    print(f"  void_factor × depth_conf × angle_conf")
    print(f"  = {void_factor:.3f} × {depth_c:.3f} × {angle_c:.3f}")
    print(f"  = {overall:.4f}")
    print(f"  (frame void ratio: {void_ratio:.4f})")

    # --- Metadata ---
    print(f"\n[Metadata]")
    print(f"  Scene: {meta['scene_id']}")
    print(f"  Splats: {meta['num_splats']:,}")
    print(f"  Regions: {meta['num_regions']}")
    print(f"  Reconstruction: {meta['reconstruction_time_s']:.3f}s")

    # --- Export demo ---
    with tempfile.TemporaryDirectory() as tmpdir:
        paths = pipe.export_frame(frame, tmpdir)
        print(f"\n[Export] {len(paths)} passes exported:")
        for name, path in paths.items():
            print(f"  - {name}")

    print("\n" + "=" * 60)
    print("Demo complete. All v2.0 proof points demonstrated.")
    print("=" * 60)


if __name__ == "__main__":
    main()

