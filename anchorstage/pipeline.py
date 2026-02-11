from __future__ import annotations

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

    def generate_frame(self, scene: Scene, camera: Camera, assets: list[ExtraAsset]) -> FrameOutputs:
        # 1) Render splat proxy, 2) Compute void map
        proxy = self.proxy_renderer.render(scene, camera)

        # 3) Reproject base witness
        repro = self.reprojection.reproject(scene, camera, proxy.void_map)

        # 4) Composite extras into reprojected frame
        assets_by_id = {a.id: a for a in assets}
        extras_out = self.extras.render_extras(
            repro.witness_reprojected, camera, scene, assets_by_id, proxy.proxy_depth
        )

        # 5) Lock non-void pixels, 6) Generative fill, 7) Receive final frame
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
        )

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
        )

