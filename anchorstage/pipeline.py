from __future__ import annotations

import json
import os
from typing import Optional

import numpy as np

from .models import Camera, ExtraAsset, FrameOutputs, Scene
from .services import (
    ExtrasService,
    GenerativeBridgeService,
    ProxyRendererService,
    ReconstructionService,
    ReprojectionService,
)


class AnchorStagePipeline:
    def __init__(self) -> None:
        self.reconstruction = ReconstructionService()
        self.proxy_renderer = ProxyRendererService()
        self.reprojection = ReprojectionService()
        self.extras = ExtrasService()
        self.generative = GenerativeBridgeService()

    def create_scene(self, rgb_image: np.ndarray, scene_id: str = "scene_default") -> Scene:
        return self.reconstruction.reconstruct(rgb_image, scene_id=scene_id)

    def configure_extras(
        self,
        scene: Scene,
        assets: list[ExtraAsset],
        density: int,
        motion_mix: dict[str, float],
        seed: int = 7,
    ) -> list:
        return self.extras.place_extras(scene, assets, density=density, motion_mix=motion_mix, seed=seed)

    def lock_region(self, scene: Scene, region_id: str) -> bool:
        for region in scene.regions:
            if region.id == region_id:
                region.locked = True
                return True
        return False

    def unlock_region(self, scene: Scene, region_id: str) -> bool:
        for region in scene.regions:
            if region.id == region_id:
                region.locked = False
                return True
        return False

    def generate_frame(self, scene: Scene, camera: Camera, assets: list[ExtraAsset]) -> FrameOutputs:
        # 1) Render splat proxy with normals + region masks
        proxy = self.proxy_renderer.render(scene, camera)

        # 2) Build region lock mask from locked regions
        h, w = camera.height, camera.width
        region_lock_mask = self._build_region_lock_mask(scene, h, w)

        # 3) Reproject base witness with region locking
        repro = self.reprojection.reproject(
            scene, camera, proxy.void_map, region_lock_mask=region_lock_mask
        )

        # 4) Composite extras into reprojected frame
        assets_by_id = {a.id: a for a in assets}
        extras_out = self.extras.render_extras(
            repro.witness_reprojected, camera, scene, assets_by_id, proxy.proxy_depth
        )

        # 5) Lock non-void pixels + region locks, 6) Normal-conditioned fill, 7) Final frame
        refreshed = self.generative.refresh(
            witness_reprojected=extras_out.rgb_with_extras,
            void_map=repro.void_map,
            depth_map=repro.depth_map,
            base_witness=scene.base_witness,
            camera_metadata={
                "position": camera.position.tolist(),
                "rotation_xyz_deg": camera.rotation_xyz_deg.tolist(),
                "scene_id": scene.scene_id,
            },
            normal_map=proxy.proxy_normal,
            region_lock_mask=region_lock_mask,
        )

        # Collect region masks for export
        region_masks = [r.mask for r in scene.regions] if scene.regions else None

        # Build metadata dict
        metadata = self._build_metadata(scene, camera, proxy)

        return FrameOutputs(
            beauty=refreshed,
            depth=np.where(np.isfinite(proxy.proxy_depth), proxy.proxy_depth, 0.0).astype(np.float32),
            void_map=repro.void_map.astype(np.uint8),
            extras_id_pass=extras_out.extras_id_pass,
            extras_depth_pass=extras_out.extras_depth_pass,
            proxy_render=proxy.proxy_color,
            confidence_score=float(proxy.confidence_score),
            witness_reprojected=extras_out.rgb_with_extras,
            witness_refreshed=refreshed,
            normal_map=proxy.proxy_normal,
            region_masks=region_masks,
            metadata=metadata,
        )

    def export_frame(self, frame: FrameOutputs, output_dir: str) -> dict:
        os.makedirs(output_dir, exist_ok=True)
        paths: dict[str, str] = {}

        # Beauty pass
        beauty_path = os.path.join(output_dir, "beauty.npy")
        np.save(beauty_path, frame.beauty)
        paths["beauty"] = beauty_path

        # Depth pass (metric)
        depth_path = os.path.join(output_dir, "depth.npy")
        np.save(depth_path, frame.depth)
        paths["depth"] = depth_path

        # Normal map
        if frame.normal_map is not None:
            normal_path = os.path.join(output_dir, "normal.npy")
            np.save(normal_path, frame.normal_map)
            paths["normal"] = normal_path

        # Void map
        void_path = os.path.join(output_dir, "void_map.npy")
        np.save(void_path, frame.void_map)
        paths["void_map"] = void_path

        # Region masks
        if frame.region_masks:
            region_dir = os.path.join(output_dir, "region_masks")
            os.makedirs(region_dir, exist_ok=True)
            for i, mask in enumerate(frame.region_masks):
                mask_path = os.path.join(region_dir, f"region_{i:03d}.npy")
                np.save(mask_path, mask)
                paths[f"region_mask_{i}"] = mask_path

        # Proxy render
        proxy_path = os.path.join(output_dir, "proxy_render.npy")
        np.save(proxy_path, frame.proxy_render)
        paths["proxy_render"] = proxy_path

        # Metadata JSON
        if frame.metadata:
            meta_path = os.path.join(output_dir, "metadata.json")
            with open(meta_path, "w") as f:
                json.dump(frame.metadata, f, indent=2)
            paths["metadata"] = meta_path

        return paths

    def _build_region_lock_mask(self, scene: Scene, h: int, w: int) -> np.ndarray:
        lock_mask = np.zeros((h, w), dtype=np.uint8)
        if not scene.regions:
            return lock_mask
        src_h, src_w = scene.depth_map.shape
        y_indices = np.minimum(
            (np.arange(h, dtype=np.float32) * src_h / max(1, h)).astype(np.int32), src_h - 1
        )
        x_indices = np.minimum(
            (np.arange(w, dtype=np.float32) * src_w / max(1, w)).astype(np.int32), src_w - 1
        )
        for region in scene.regions:
            if not region.locked:
                continue
            rmask = region.mask.astype(bool)
            resized = rmask[np.ix_(y_indices, x_indices)]
            lock_mask[resized] = 1
        return lock_mask

    def _build_metadata(self, scene: Scene, camera: Camera, proxy) -> dict:
        regions_meta = []
        for r in scene.regions:
            entry = {
                "id": r.id,
                "semantic_label": r.semantic_label,
                "locked": r.locked,
            }
            if r.plane_params is not None:
                entry["plane_params"] = r.plane_params.tolist()
            regions_meta.append(entry)

        return {
            "camera": {
                "position": camera.position.tolist(),
                "rotation_xyz_deg": camera.rotation_xyz_deg.tolist(),
                "focal_length_mm": camera.focal_length_mm,
                "metric_scale": scene.metric_scale,
            },
            "regions": regions_meta,
            "confidence": {
                "overall": float(proxy.confidence_score),
                "depth_confidence": float(proxy.depth_confidence),
                "angle_confidence": float(proxy.angle_confidence),
            },
            "scene_id": scene.scene_id,
            "reconstruction_time_s": scene.reconstruction_time_s,
            "num_splats": len(scene.gaussian_splats),
            "num_regions": len(scene.regions),
        }

