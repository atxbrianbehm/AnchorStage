from __future__ import annotations

import numpy as np

from ..math3d import backproject_pixel, intrinsics_from_camera
from ..models import Camera, GaussianSplat, Scene


class ReconstructionService:
    def reconstruct(self, rgb_image: np.ndarray, scene_id: str = "scene_default") -> Scene:
        if rgb_image.ndim != 3 or rgb_image.shape[2] != 3:
            raise ValueError("Expected RGB image in HxWx3 format.")
        image = rgb_image.astype(np.float32)
        if image.max() > 1.0:
            image /= 255.0

        h, w, _ = image.shape
        base_camera = Camera(
            position=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            rotation_xyz_deg=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            width=w,
            height=h,
        )
        depth = self._estimate_depth(image)
        confidence = self._estimate_confidence(depth)
        splats = self._build_splats(image, depth, confidence, base_camera)

        return Scene(
            base_witness=image,
            gaussian_splats=splats,
            depth_map=depth,
            confidence_map=confidence,
            base_camera=base_camera,
            scene_id=scene_id,
        )

    def _estimate_depth(self, image: np.ndarray) -> np.ndarray:
        h, w, _ = image.shape
        yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
        luma = image.mean(axis=2)
        depth = 1.0 + (1.0 - yy) * 4.0 + (1.0 - luma) * 1.5
        return depth.astype(np.float32)

    def _estimate_confidence(self, depth: np.ndarray) -> np.ndarray:
        gx = np.zeros_like(depth)
        gy = np.zeros_like(depth)
        gx[:, 1:-1] = np.abs(depth[:, 2:] - depth[:, :-2]) * 0.5
        gy[1:-1, :] = np.abs(depth[2:, :] - depth[:-2, :]) * 0.5
        grad = np.sqrt(gx * gx + gy * gy)
        grad_norm = grad / (grad.max() + 1e-6)
        return np.clip(1.0 - grad_norm, 0.0, 1.0).astype(np.float32)

    def _build_splats(
        self, image: np.ndarray, depth: np.ndarray, confidence: np.ndarray, camera: Camera
    ) -> list[GaussianSplat]:
        h, w = depth.shape
        k = intrinsics_from_camera(w, h, camera.focal_length_mm, camera.filmback_mm)
        splats: list[GaussianSplat] = []

        # Downsample to keep preview rendering responsive.
        step = max(1, int(min(h, w) / 180))
        for v in range(0, h, step):
            for u in range(0, w, step):
                d = float(depth[v, u])
                p = backproject_pixel(float(u), float(v), d, k)
                local_var = 0.0
                if 1 < v < h - 2 and 1 < u < w - 2:
                    patch = depth[v - 1 : v + 2, u - 1 : u + 2]
                    local_var = float(np.var(patch))
                scale = 0.6 + min(1.4, local_var * 3.0)
                splats.append(
                    GaussianSplat(
                        position=p,
                        color=image[v, u].copy(),
                        scale=scale,
                        opacity=float(confidence[v, u]),
                    )
                )
        return splats

