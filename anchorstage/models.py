from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Camera:
    position: np.ndarray
    rotation_xyz_deg: np.ndarray
    focal_length_mm: float = 35.0
    filmback_mm: float = 36.0
    aspect_ratio: float = 16 / 9
    width: int = 1280
    height: int = 720


@dataclass
class GaussianSplat:
    position: np.ndarray
    color: np.ndarray
    scale: float
    opacity: float


@dataclass
class ExtraAsset:
    id: str
    sprite_loop_rgba: np.ndarray
    height_meters: float
    facing_bias: float
    motion_type: str
    walk_speed: float


@dataclass
class ExtraPlacement:
    asset_id: str
    world_position: np.ndarray
    yaw_deg: float
    loop_offset: float


@dataclass
class Scene:
    base_witness: np.ndarray
    gaussian_splats: list[GaussianSplat]
    depth_map: np.ndarray
    confidence_map: np.ndarray
    regions: list[dict] = field(default_factory=list)
    cameras: list[Camera] = field(default_factory=list)
    extras: list[ExtraPlacement] = field(default_factory=list)
    base_camera: Camera | None = None
    scene_id: str = "scene_default"


@dataclass
class ProxyRender:
    proxy_color: np.ndarray
    proxy_depth: np.ndarray
    void_map: np.ndarray
    confidence_score: float
    contribution_alpha: np.ndarray


@dataclass
class ReprojectionOutput:
    witness_reprojected: np.ndarray
    known_mask: np.ndarray
    void_map: np.ndarray
    depth_map: np.ndarray


@dataclass
class ExtrasRenderOutput:
    rgb_with_extras: np.ndarray
    extras_id_pass: np.ndarray
    extras_depth_pass: np.ndarray


@dataclass
class FrameOutputs:
    beauty: np.ndarray
    depth: np.ndarray
    void_map: np.ndarray
    extras_id_pass: np.ndarray
    extras_depth_pass: np.ndarray
    proxy_render: np.ndarray
    confidence_score: float
    witness_reprojected: np.ndarray
    witness_refreshed: np.ndarray

