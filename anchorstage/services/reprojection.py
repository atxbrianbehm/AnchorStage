from __future__ import annotations

import numpy as np

from ..math3d import backproject_pixel, intrinsics_from_camera, project_points, world_to_camera
from ..models import Camera, ReprojectionOutput, Scene


class ReprojectionService:
    def reproject(self, scene: Scene, camera: Camera, proxy_void_map: np.ndarray) -> ReprojectionOutput:
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

        src_h, src_w = depth.shape
        for y in range(src_h):
            for x in range(src_w):
                d = float(depth[y, x])
                p_world = backproject_pixel(float(x), float(y), d, k_base)
                p_cam = world_to_camera(
                    p_world[None, :],
                    camera.position,
                    camera.rotation_xyz_deg,
                )[0]
                uu, vv, valid = project_points(p_cam[None, :], k_target, w, h)
                if not bool(valid[0]):
                    continue
                u = int(uu[0])
                v = int(vv[0])
                z = float(p_cam[2])
                if z < out_depth[v, u]:
                    out_depth[v, u] = z
                    out[v, u] = base[y, x]
                    known[v, u] = 1

        void_from_reproject = (known == 0).astype(np.uint8)
        merged_void = np.maximum(void_from_reproject, proxy_void_map.astype(np.uint8))
        return ReprojectionOutput(
            witness_reprojected=out,
            known_mask=1 - merged_void,
            void_map=merged_void,
            depth_map=np.where(np.isfinite(out_depth), out_depth, 0.0).astype(np.float32),
        )

