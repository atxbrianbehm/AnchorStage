from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Intrinsics:
    fx: float
    fy: float
    cx: float
    cy: float


def intrinsics_from_camera(width: int, height: int, focal_length_mm: float, filmback_mm: float) -> Intrinsics:
    fx = (focal_length_mm / filmback_mm) * width
    fy = fx
    cx = width * 0.5
    cy = height * 0.5
    return Intrinsics(fx=fx, fy=fy, cx=cx, cy=cy)


def euler_xyz_to_matrix(rx_deg: float, ry_deg: float, rz_deg: float) -> np.ndarray:
    rx = math.radians(rx_deg)
    ry = math.radians(ry_deg)
    rz = math.radians(rz_deg)
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)

    rx_m = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]], dtype=np.float32)
    ry_m = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], dtype=np.float32)
    rz_m = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]], dtype=np.float32)
    return rz_m @ ry_m @ rx_m


def world_to_camera(points_world: np.ndarray, cam_pos: np.ndarray, cam_rot_euler_deg: np.ndarray) -> np.ndarray:
    r = euler_xyz_to_matrix(cam_rot_euler_deg[0], cam_rot_euler_deg[1], cam_rot_euler_deg[2])
    return (points_world - cam_pos[None, :]) @ r.T


def project_points(points_cam: np.ndarray, k: Intrinsics, width: int, height: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    z = points_cam[:, 2]
    valid = z > 1e-4
    u = np.zeros_like(z)
    v = np.zeros_like(z)
    u[valid] = (points_cam[valid, 0] * k.fx / z[valid]) + k.cx
    v[valid] = (points_cam[valid, 1] * k.fy / z[valid]) + k.cy
    in_bounds = valid & (u >= 0) & (u < width) & (v >= 0) & (v < height)
    return u, v, in_bounds


def backproject_pixel(u: float, v: float, d: float, k: Intrinsics) -> np.ndarray:
    x = (u - k.cx) * d / k.fx
    y = (v - k.cy) * d / k.fy
    z = d
    return np.array([x, y, z], dtype=np.float32)

