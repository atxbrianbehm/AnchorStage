from __future__ import annotations

import hashlib
import random

import numpy as np

from ..math3d import intrinsics_from_camera, project_points, world_to_camera
from ..models import Camera, ExtraAsset, ExtraPlacement, ExtrasRenderOutput, Scene


class ExtrasService:
    def place_extras(
        self,
        scene: Scene,
        assets: list[ExtraAsset],
        density: int,
        motion_mix: dict[str, float],
        seed: int = 7,
    ) -> list[ExtraPlacement]:
        if density <= 0 or not assets:
            scene.extras = []
            return scene.extras

        rng = random.Random(seed)
        placed: list[ExtraPlacement] = []
        min_dist = 0.25
        ground_y = self._estimate_ground_plane(scene.depth_map)

        attempts = 0
        while len(placed) < density and attempts < density * 30:
            attempts += 1
            x = rng.uniform(-4.0, 4.0)
            z = rng.uniform(1.5, 9.0)
            p = np.array([x, ground_y, z], dtype=np.float32)
            if any(np.linalg.norm(p - e.world_position) < min_dist for e in placed):
                continue
            motion = self._sample_motion(motion_mix, rng)
            candidates = [a for a in assets if a.motion_type == motion] or assets
            a = rng.choice(candidates)
            placed.append(
                ExtraPlacement(
                    asset_id=a.id,
                    world_position=p,
                    yaw_deg=rng.uniform(-20, 20),
                    loop_offset=rng.random(),
                )
            )

        scene.extras = placed
        return placed

    def render_extras(
        self,
        rgb: np.ndarray,
        camera: Camera,
        scene: Scene,
        assets_by_id: dict[str, ExtraAsset],
        proxy_depth: np.ndarray,
    ) -> ExtrasRenderOutput:
        h, w, _ = rgb.shape
        out = rgb.copy()
        id_pass = np.zeros((h, w), dtype=np.uint16)
        depth_pass = np.zeros((h, w), dtype=np.float32)
        k = intrinsics_from_camera(w, h, camera.focal_length_mm, camera.filmback_mm)

        for placement in scene.extras:
            asset = assets_by_id.get(placement.asset_id)
            if asset is None:
                continue
            p_cam = world_to_camera(
                placement.world_position[None, :],
                camera.position,
                camera.rotation_xyz_deg,
            )[0]
            uu, vv, valid = project_points(p_cam[None, :], k, w, h)
            if not bool(valid[0]):
                continue

            u = int(uu[0])
            v = int(vv[0])
            z = float(p_cam[2])
            if z <= 0.0:
                continue

            screen_scale = camera.focal_length_mm / z
            render_h = max(12, int(asset.height_meters * 26.0 * screen_scale))
            render_w = max(8, int(render_h * (asset.sprite_loop_rgba.shape[1] / max(1, asset.sprite_loop_rgba.shape[0]))))

            x0 = u - render_w // 2
            y0 = v - render_h
            self._blit_billboard(
                out,
                id_pass,
                depth_pass,
                x0,
                y0,
                render_w,
                render_h,
                asset.sprite_loop_rgba,
                z,
                proxy_depth,
                self._stable_id(asset.id),
            )

        return ExtrasRenderOutput(rgb_with_extras=out, extras_id_pass=id_pass, extras_depth_pass=depth_pass)

    def _estimate_ground_plane(self, depth_map: np.ndarray) -> float:
        h = depth_map.shape[0]
        bottom = depth_map[int(h * 0.8) :, :]
        return float(np.median(bottom) * 0.02)

    def _sample_motion(self, motion_mix: dict[str, float], rng: random.Random) -> str:
        total = sum(max(0.0, v) for v in motion_mix.values())
        if total <= 0:
            return "walk"
        t = rng.random() * total
        run = 0.0
        for k, v in motion_mix.items():
            run += max(0.0, v)
            if t <= run:
                return k
        return next(iter(motion_mix.keys()))

    def _stable_id(self, text: str) -> int:
        digest = hashlib.sha1(text.encode("utf-8")).digest()
        return int.from_bytes(digest[:2], "big")

    def _blit_billboard(
        self,
        out: np.ndarray,
        id_pass: np.ndarray,
        depth_pass: np.ndarray,
        x0: int,
        y0: int,
        rw: int,
        rh: int,
        sprite: np.ndarray,
        z: float,
        proxy_depth: np.ndarray,
        extra_id: int,
    ) -> None:
        h, w, _ = out.shape
        sh, sw, _ = sprite.shape
        for yy in range(rh):
            y = y0 + yy
            if y < 0 or y >= h:
                continue
            sy = int((yy / max(1, rh - 1)) * (sh - 1))
            for xx in range(rw):
                x = x0 + xx
                if x < 0 or x >= w:
                    continue
                if np.isfinite(proxy_depth[y, x]) and z > float(proxy_depth[y, x]):
                    continue
                sx = int((xx / max(1, rw - 1)) * (sw - 1))
                rgba = sprite[sy, sx]
                a = float(rgba[3])
                if a <= 0.01:
                    continue
                out[y, x] = (1.0 - a) * out[y, x] + a * rgba[:3]
                id_pass[y, x] = extra_id
                depth_pass[y, x] = z

