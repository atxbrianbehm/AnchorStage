from __future__ import annotations

import time

import numpy as np
from scipy.ndimage import uniform_filter

from ..math3d import backproject_pixel, intrinsics_from_camera
from ..models import Camera, GaussianSplat, Region, Scene


class ReconstructionService:
    def reconstruct(self, rgb_image: np.ndarray, scene_id: str = "scene_default") -> Scene:
        if rgb_image.ndim != 3 or rgb_image.shape[2] != 3:
            raise ValueError("Expected RGB image in HxWx3 format.")
        t0 = time.perf_counter()
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
        depth = self._estimate_metric_depth(image)
        confidence = self._estimate_confidence(depth)
        normal_map = self._estimate_normals(depth, base_camera)
        splats = self._build_splats(image, depth, confidence, base_camera)
        regions = self._segment_regions(depth, image)

        elapsed = time.perf_counter() - t0
        return Scene(
            base_witness=image,
            gaussian_splats=splats,
            depth_map=depth,
            confidence_map=confidence,
            normal_map=normal_map,
            regions=regions,
            base_camera=base_camera,
            scene_id=scene_id,
            metric_scale=1.0,
            reconstruction_time_s=elapsed,
        )

    # ------------------------------------------------------------------
    # Metric depth estimation (SHARP-inspired, placeholder for ZoeDepth)
    # ------------------------------------------------------------------
    def _estimate_metric_depth(self, image: np.ndarray) -> np.ndarray:
        h, w, _ = image.shape
        yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
        luma = image.mean(axis=2)
        # Metric depth in meters: ground ~1m, sky/far ~6m
        depth = 1.0 + (1.0 - yy) * 4.0 + (1.0 - luma) * 1.5
        return depth.astype(np.float32)

    # ------------------------------------------------------------------
    # Confidence from depth gradients
    # ------------------------------------------------------------------
    def _estimate_confidence(self, depth: np.ndarray) -> np.ndarray:
        gx = np.zeros_like(depth)
        gy = np.zeros_like(depth)
        gx[:, 1:-1] = np.abs(depth[:, 2:] - depth[:, :-2]) * 0.5
        gy[1:-1, :] = np.abs(depth[2:, :] - depth[:-2, :]) * 0.5
        grad = np.sqrt(gx * gx + gy * gy)
        grad_norm = grad / (grad.max() + 1e-6)
        return np.clip(1.0 - grad_norm, 0.0, 1.0).astype(np.float32)

    # ------------------------------------------------------------------
    # Normal map from depth via finite differences
    # ------------------------------------------------------------------
    def _estimate_normals(self, depth: np.ndarray, camera: Camera) -> np.ndarray:
        h, w = depth.shape
        k = intrinsics_from_camera(w, h, camera.focal_length_mm, camera.filmback_mm)
        # Compute dz/du and dz/dv
        dz_du = np.zeros_like(depth)
        dz_dv = np.zeros_like(depth)
        dz_du[:, 1:-1] = (depth[:, 2:] - depth[:, :-2]) * 0.5
        dz_dv[1:-1, :] = (depth[2:, :] - depth[:-2, :]) * 0.5
        # Normal = (-dz/du / fx, -dz/dv / fy, 1), then normalize
        nx = -dz_du / (k.fx + 1e-6)
        ny = -dz_dv / (k.fy + 1e-6)
        nz = np.ones_like(depth)
        length = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-8
        normal = np.stack([nx / length, ny / length, nz / length], axis=2)
        return normal.astype(np.float32)

    # ------------------------------------------------------------------
    # Gaussian splat regression (direct, SHARP-inspired)
    # ------------------------------------------------------------------
    def _build_splats(
        self, image: np.ndarray, depth: np.ndarray, confidence: np.ndarray, camera: Camera
    ) -> list[GaussianSplat]:
        h, w = depth.shape
        k = intrinsics_from_camera(w, h, camera.focal_length_mm, camera.filmback_mm)

        # Vectorised back-projection for all pixels
        uu = np.arange(w, dtype=np.float32)
        vv = np.arange(h, dtype=np.float32)
        u_grid, v_grid = np.meshgrid(uu, vv)

        x3d = (u_grid - k.cx) * depth / k.fx
        y3d = (v_grid - k.cy) * depth / k.fy
        z3d = depth

        # Local scale from depth variance in 3x3 neighbourhood
        depth_mean = uniform_filter(depth, size=3)
        depth_sq_mean = uniform_filter(depth * depth, size=3)
        local_var = np.clip(depth_sq_mean - depth_mean * depth_mean, 0.0, None)
        scale_arr = 0.6 + np.minimum(1.4, local_var * 3.0)

        # Flatten all arrays
        positions = np.stack([x3d, y3d, z3d], axis=2).reshape(-1, 3).astype(np.float32)
        colors = image.reshape(-1, 3).astype(np.float32)
        opacities = confidence.reshape(-1).astype(np.float32)
        scales = scale_arr.reshape(-1).astype(np.float32)

        # Build splat objects
        n = positions.shape[0]
        splats: list[GaussianSplat] = []
        for i in range(n):
            splats.append(
                GaussianSplat(
                    position=positions[i],
                    color=colors[i],
                    scale=float(scales[i]),
                    opacity=float(opacities[i]),
                    metric_scale=1.0,
                )
            )
        return splats

    # ------------------------------------------------------------------
    # Region segmentation (depth clustering + semantic heuristics)
    # ------------------------------------------------------------------
    def _segment_regions(self, depth: np.ndarray, image: np.ndarray) -> list[Region]:
        h, w = depth.shape
        regions: list[Region] = []

        # Sky region: top portion, high depth, bluish
        sky_mask = np.zeros((h, w), dtype=bool)
        top_band = int(h * 0.35)
        sky_depth_thresh = np.percentile(depth[:top_band, :], 70)
        sky_mask[:top_band, :] = depth[:top_band, :] >= sky_depth_thresh
        # Boost with blue channel heuristic
        if image.shape[2] == 3:
            blue_ratio = image[:, :, 2] / (image.mean(axis=2) + 1e-6)
            sky_mask[:top_band, :] &= blue_ratio[:top_band, :] > 0.9
        if sky_mask.any():
            regions.append(Region(
                id="sky_001",
                mask=sky_mask.astype(np.uint8),
                semantic_label="sky",
                locked=False,
            ))

        # Ground region: bottom portion, shallow depth
        ground_mask = np.zeros((h, w), dtype=bool)
        bottom_start = int(h * 0.65)
        ground_depth_thresh = np.percentile(depth[bottom_start:, :], 40)
        ground_mask[bottom_start:, :] = depth[bottom_start:, :] <= ground_depth_thresh
        if ground_mask.any():
            # Estimate ground plane params [a,b,c,d] for y = ground_y
            ground_depths = depth[bottom_start:, :]
            median_d = float(np.median(ground_depths[ground_mask[bottom_start:, :]]))
            plane_params = np.array([0.0, 1.0, 0.0, -median_d * 0.02], dtype=np.float32)
            regions.append(Region(
                id="ground_001",
                mask=ground_mask.astype(np.uint8),
                plane_params=plane_params,
                semantic_label="ground",
                locked=False,
            ))

        # Facade region: mid-band, mid-depth, not sky or ground
        facade_mask = np.zeros((h, w), dtype=bool)
        assigned = np.zeros((h, w), dtype=bool)
        for r in regions:
            assigned |= r.mask.astype(bool)
        mid_depth = np.median(depth)
        facade_mask = (~assigned) & (depth < mid_depth * 1.3) & (depth > mid_depth * 0.5)
        if facade_mask.any():
            # RANSAC-lite: estimate dominant plane from facade pixels
            facade_depths = depth[facade_mask]
            med_fd = float(np.median(facade_depths))
            plane_params = np.array([0.0, 0.0, 1.0, -med_fd], dtype=np.float32)
            regions.append(Region(
                id="facade_001",
                mask=facade_mask.astype(np.uint8),
                plane_params=plane_params,
                semantic_label="building_facade",
                locked=False,
            ))

        return regions

