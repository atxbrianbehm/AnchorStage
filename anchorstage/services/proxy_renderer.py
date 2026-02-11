from __future__ import annotations

import math

import numpy as np

from ..math3d import intrinsics_from_camera, project_points, world_to_camera
from ..models import Camera, ProxyRender, Scene


class ProxyRendererService:
    def render(self, scene: Scene, camera: Camera, opacity_threshold: float = 0.08, stride: int = 1) -> ProxyRender:
        h, w = camera.height, camera.width
        proxy_color = np.zeros((h, w, 3), dtype=np.float32)
        proxy_depth = np.full((h, w), np.inf, dtype=np.float32)
        proxy_normal = np.zeros((h, w, 3), dtype=np.float32)
        proxy_normal[:, :, 2] = 1.0  # default forward-facing
        alpha_accum = np.zeros((h, w), dtype=np.float32)

        splats = scene.gaussian_splats
        if stride > 1:
            splats = splats[::stride]

        points_world = np.array([s.position for s in splats], dtype=np.float32)
        colors = np.array([s.color for s in splats], dtype=np.float32)
        opacities = np.clip(np.array([s.opacity for s in splats], dtype=np.float32), 0.0, 1.0)

        k = intrinsics_from_camera(w, h, camera.focal_length_mm, camera.filmback_mm)
        points_cam = world_to_camera(points_world, camera.position, camera.rotation_xyz_deg)
        uv_u, uv_v, valid = project_points(points_cam, k, w, h)

        # Vectorised z-buffer splatting: sort by depth (back-to-front not needed,
        # we want closest-wins so sort front-to-back and use first-write semantics)
        vidx = np.where(valid)[0]
        if vidx.size > 0:
            zvals = points_cam[vidx, 2]
            order = np.argsort(zvals)  # front to back
            vidx = vidx[order]

            xi = uv_u[vidx].astype(np.int32)
            yi = uv_v[vidx].astype(np.int32)
            zi = zvals[order]
            ci = colors[vidx]
            ai = opacities[vidx]

            # Use flat indices for vectorised scatter (first write wins for sorted data)
            flat = yi * w + xi
            # np.unique with return_index gives first occurrence (smallest z)
            _, first_idx = np.unique(flat, return_index=True)
            sel = vidx[first_idx]
            fx = xi[first_idx]
            fy = yi[first_idx]
            fz = zi[first_idx]
            fa = ai[first_idx]

            proxy_depth[fy, fx] = fz
            proxy_color[fy, fx] = colors[sel] * fa[:, None]
            alpha_accum[fy, fx] = fa

            # Normal map lookup (vectorised)
            normal_src = scene.normal_map
            if normal_src is not None:
                src_h, src_w = scene.depth_map.shape
                # Map splat global indices back to source pixels
                if stride > 1:
                    global_idx = sel * stride
                else:
                    global_idx = sel
                sy = np.minimum(global_idx // src_w, src_h - 1).astype(np.int32)
                sx = np.minimum(global_idx % src_w, src_w - 1).astype(np.int32)
                proxy_normal[fy, fx] = normal_src[sy, sx]

        # Render region masks (vectorised)
        region_mask = self._render_region_mask(scene, camera, h, w)

        void_map = (alpha_accum < opacity_threshold).astype(np.uint8)

        # Enhanced 3-factor confidence:
        # confidence = (1 - void_coverage) * depth_confidence * angle_confidence
        void_ratio = float(void_map.sum() / (h * w))
        void_factor = 1.0 - void_ratio
        depth_conf = self._compute_depth_confidence(proxy_depth, void_map)
        angle_conf = self._compute_angle_confidence(camera, scene)
        confidence = void_factor * depth_conf * angle_conf

        return ProxyRender(
            proxy_color=proxy_color,
            proxy_depth=proxy_depth,
            void_map=void_map,
            confidence_score=float(confidence),
            contribution_alpha=alpha_accum,
            proxy_normal=proxy_normal,
            region_mask=region_mask,
            depth_confidence=float(depth_conf),
            angle_confidence=float(angle_conf),
        )

    def _render_region_mask(self, scene: Scene, camera: Camera, h: int, w: int) -> np.ndarray:
        region_buf = np.zeros((h, w), dtype=np.uint16)
        if not scene.regions:
            return region_buf
        src_h, src_w = scene.depth_map.shape
        # Vectorised nearest-neighbour resize
        y_idx = np.minimum((np.arange(h) * src_h / max(1, h)).astype(np.int32), src_h - 1)
        x_idx = np.minimum((np.arange(w) * src_w / max(1, w)).astype(np.int32), src_w - 1)
        for idx, region in enumerate(scene.regions, start=1):
            rmask = region.mask.astype(bool)
            resized = rmask[np.ix_(y_idx, x_idx)]
            region_buf[resized] = idx
        return region_buf

    def _compute_depth_confidence(self, proxy_depth: np.ndarray, void_map: np.ndarray) -> float:
        finite = np.isfinite(proxy_depth)
        valid = (void_map == 0) & finite
        if not valid.any():
            return 0.0
        valid_depths = proxy_depth[valid]
        mean_depth = float(np.mean(valid_depths))
        # Compute gradients only between pairs of valid pixels
        grad_samples = []
        with np.errstate(invalid="ignore"):
            # Horizontal pairs
            h_both = valid[:, :-1] & valid[:, 1:]
            if h_both.any():
                h_diff = np.abs(proxy_depth[:, 1:] - proxy_depth[:, :-1])
                grad_samples.append(h_diff[h_both])
            # Vertical pairs
            v_both = valid[:-1, :] & valid[1:, :]
            if v_both.any():
                v_diff = np.abs(proxy_depth[1:, :] - proxy_depth[:-1, :])
                grad_samples.append(v_diff[v_both])
        if not grad_samples:
            return 0.5
        all_grads = np.concatenate(grad_samples)
        relative_roughness = float(np.mean(all_grads)) / (mean_depth + 1e-6)
        return float(np.clip(1.0 - relative_roughness * 2.0, 0.05, 1.0))

    def _compute_angle_confidence(self, camera: Camera, scene: Scene) -> float:
        if scene.base_camera is None:
            return 1.0
        # Angular deviation from base camera reduces confidence
        delta_rot = camera.rotation_xyz_deg - scene.base_camera.rotation_xyz_deg
        angle_deg = float(np.sqrt(np.sum(delta_rot ** 2)))
        # Confidence drops linearly: 0° → 1.0, 45° → 0.5, 90° → 0.0
        return float(np.clip(1.0 - angle_deg / 90.0, 0.0, 1.0))

