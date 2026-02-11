from __future__ import annotations

import numpy as np

from .models import Camera, ExtraAsset
from .pipeline import AnchorStagePipeline


def _make_synthetic_image(h: int = 540, w: int = 960) -> np.ndarray:
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    xx = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    r = 0.15 + 0.55 * (1.0 - yy)
    g = 0.25 + 0.35 * xx
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
    scene = pipe.create_scene(image, scene_id="demo_scene_001")

    assets = [
        ExtraAsset("walker_a", _make_sprite((0.95, 0.55, 0.35)), 1.7, 0.0, "walk", 1.0),
        ExtraAsset("idle_a", _make_sprite((0.35, 0.75, 0.95)), 1.6, 0.0, "idle", 0.0),
    ]
    pipe.configure_extras(scene, assets, density=30, motion_mix={"walk": 0.7, "idle": 0.3}, seed=12)

    cam = Camera(
        position=np.array([0.22, 0.0, 0.0], dtype=np.float32),
        rotation_xyz_deg=np.array([0.0, 4.0, 0.0], dtype=np.float32),
        focal_length_mm=35.0,
        filmback_mm=36.0,
        width=1280,
        height=720,
    )
    frame = pipe.generate_frame(scene, cam, assets)
    void_ratio = float(frame.void_map.sum() / frame.void_map.size)
    print("AnchorStage MVP demo frame generated")
    print(f"Scene ID: {scene.scene_id}")
    print(f"Confidence score: {frame.confidence_score:.4f} (void ratio: {void_ratio:.4f})")
    print(f"Passes: beauty={frame.beauty.shape}, depth={frame.depth.shape}, extras_id={frame.extras_id_pass.shape}")


if __name__ == "__main__":
    main()

