from __future__ import annotations

from typing import Optional

import numpy as np

from ..math3d import backproject_pixel, intrinsics_from_camera, project_points, world_to_camera
from ..models import Camera, ReprojectionOutput, Scene


class ReprojectionService:
    def reproject(
        self,
        scene: Scene,
        camera: Camera,
        proxy_void_map: np.ndarray,
        region_lock_mask: Optional[np.ndarray] = None,
    ) -> ReprojectionOutput:
        if scene.base_camera is None:
            raise ValueError("Scene is missing base_camera.")

        base = scene.base_witness
        depth = scene.depth_map
        h, w = camera.height, camera.width
        out = np.zeros((h, w, 3), dtype=np.float32)
        out_depth = np.full((h, w), np.inf, dtype=np.float32)
        known = np.zeros((h, w), dtype=np.uint8)

        k_base = intrinsics_from_camera(
            scene.base_camera.width,
            scene.base_camera.height,
            scene.base_camera.focal_length_mm,
            scene.base_camera.filmback_mm,
        )
        k_target = intrinsics_from_camera(w, h, camera.focal_length_mm, camera.filmback_mm)

        if region_lock_mask is None:
            region_lock_mask = self._build_region_lock_mask(scene, h, w)

        src_h, src_w = depth.shape

        # Vectorised reprojection: backproject all source pixels at once
        yy, xx = np.mgrid[0:src_h, 0:src_w]
        xs = xx.ravel().astype(np.float32)
        ys = yy.ravel().astype(np.float32)
        ds = depth.ravel().astype(np.float32)

        # Backproject: pixel (x,y,d) -> world via base camera intrinsics
        fx_b, fy_b = k_base.fx, k_base.fy
        cx_b, cy_b = k_base.cx, k_base.cy
        world_x = (xs - cx_b) * ds / fx_b
        world_y = (ys - cy_b) * ds / fy_b
        world_z = ds
        pts_world = np.stack([world_x, world_y, world_z], axis=1)

        # Transform to target camera
        pts_cam = world_to_camera(pts_world, camera.position, camera.rotation_xyz_deg)
        uv_u, uv_v, valid = project_points(pts_cam, k_target, w, h)

        vidx = np.where(valid)[0]
        if vidx.size > 0:
            tu = uv_u[vidx].astype(np.int32)
            tv = uv_v[vidx].astype(np.int32)
            tz = pts_cam[vidx, 2]
            # Source pixel coords
            sy = ys[vidx].astype(np.int32)
            sx = xs[vidx].astype(np.int32)

            # Sort front-to-back, then use unique to keep closest
            order = np.argsort(tz)
            tu, tv, tz = tu[order], tv[order], tz[order]
            sy, sx = sy[order], sx[order]

            flat = tv * w + tu
            _, first = np.unique(flat, return_index=True)
            tu, tv, tz = tu[first], tv[first], tz[first]
            sy, sx = sy[first], sx[first]

            out_depth[tv, tu] = tz
            out[tv, tu] = base[sy, sx]
            known[tv, tu] = 1

        # Locked regions: force known pixels to stay locked (never voided)
        locked = region_lock_mask.astype(bool)
        known[locked] = 1

        void_from_reproject = (known == 0).astype(np.uint8)
        merged_void = np.maximum(void_from_reproject, proxy_void_map.astype(np.uint8))
        merged_void[locked] = 0
        return ReprojectionOutput(
            witness_reprojected=out,
            known_mask=1 - merged_void,
            void_map=merged_void,
            depth_map=np.where(np.isfinite(out_depth), out_depth, 0.0).astype(np.float32),
        )

    def _build_region_lock_mask(self, scene: Scene, h: int, w: int) -> np.ndarray:
        lock_mask = np.zeros((h, w), dtype=np.uint8)
        if not scene.regions:
            return lock_mask
        src_h, src_w = scene.depth_map.shape
        y_idx = np.minimum((np.arange(h) * src_h / max(1, h)).astype(np.int32), src_h - 1)
        x_idx = np.minimum((np.arange(w) * src_w / max(1, w)).astype(np.int32), src_w - 1)
        for region in scene.regions:
            if not region.locked:
                continue
            rmask = region.mask.astype(bool)
            resized = rmask[np.ix_(y_idx, x_idx)]
            lock_mask[resized] = 1
        return lock_mask

