from __future__ import annotations

import numpy as np

from ..math3d import intrinsics_from_camera, project_points, world_to_camera
from ..models import Camera, ProxyRender, Scene


class ProxyRendererService:
    def render(self, scene: Scene, camera: Camera, opacity_threshold: float = 0.08) -> ProxyRender:
        h, w = camera.height, camera.width
        proxy_color = np.zeros((h, w, 3), dtype=np.float32)
        proxy_depth = np.full((h, w), np.inf, dtype=np.float32)
        alpha_accum = np.zeros((h, w), dtype=np.float32)

        points_world = np.array([s.position for s in scene.gaussian_splats], dtype=np.float32)
        colors = np.array([s.color for s in scene.gaussian_splats], dtype=np.float32)
        opacities = np.array([s.opacity for s in scene.gaussian_splats], dtype=np.float32)

        k = intrinsics_from_camera(w, h, camera.focal_length_mm, camera.filmback_mm)
        points_cam = world_to_camera(points_world, camera.position, camera.rotation_xyz_deg)
        u, v, valid = project_points(points_cam, k, w, h)

        idx = np.where(valid)[0]
        for i in idx:
            x = int(u[i])
            y = int(v[i])
            z = float(points_cam[i, 2])
            alpha = float(np.clip(opacities[i], 0.0, 1.0))
            if z < proxy_depth[y, x]:
                proxy_depth[y, x] = z
                proxy_color[y, x] = colors[i] * alpha
                alpha_accum[y, x] = alpha

        void_map = (alpha_accum < opacity_threshold).astype(np.uint8)
        void_ratio = float(void_map.sum() / (h * w))
        confidence = 1.0 - void_ratio
        return ProxyRender(
            proxy_color=proxy_color,
            proxy_depth=proxy_depth,
            void_map=void_map,
            confidence_score=confidence,
            contribution_alpha=alpha_accum,
        )

