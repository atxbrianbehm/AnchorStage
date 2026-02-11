from __future__ import annotations

from typing import Optional

import numpy as np


class GenerativeBridgeService:
    def refresh(
        self,
        witness_reprojected: np.ndarray,
        void_map: np.ndarray,
        depth_map: np.ndarray,
        base_witness: np.ndarray,
        camera_metadata: dict,
        normal_map: Optional[np.ndarray] = None,
        region_lock_mask: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        out = witness_reprojected.copy()
        h, w, _ = out.shape
        base = self._resize_nearest(base_witness, h, w)

        void = void_map.astype(bool)

        # Region lock: locked pixels are never modified
        fillable = void.copy()
        if region_lock_mask is not None:
            fillable &= ~region_lock_mask.astype(bool)

        if not fillable.any():
            return np.clip(out, 0.0, 1.0).astype(np.float32)

        # Vectorised inpainting: iterative dilation from known pixels
        # Each iteration fills void pixels that border known pixels
        known = ~void
        filled = out.copy()
        for _ in range(8):  # 8 iterations covers radius ~8
            if not fillable.any():
                break
            # Average of known neighbours using shifts
            accum = np.zeros((h, w, 3), dtype=np.float32)
            count = np.zeros((h, w), dtype=np.float32)
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                shifted_known = np.roll(np.roll(known, -dy, axis=0), -dx, axis=1)
                shifted_color = np.roll(np.roll(filled, -dy, axis=0), -dx, axis=1)
                mask = shifted_known & fillable
                accum[mask] += shifted_color[mask]
                count[mask] += 1.0
            can_fill = (count > 0) & fillable
            if not can_fill.any():
                break
            for c in range(3):
                filled[:, :, c][can_fill] = accum[:, :, c][can_fill] / count[can_fill]
            # Blend with base witness
            filled[can_fill] = filled[can_fill] * 0.7 + base[can_fill] * 0.3
            known[can_fill] = True
            fillable[can_fill] = False

        # Remaining unfilled pixels get base witness
        still_void = fillable & ~known
        filled[still_void] = base[still_void]

        return np.clip(filled, 0.0, 1.0).astype(np.float32)

    def _resize_nearest(self, img: np.ndarray, h: int, w: int) -> np.ndarray:
        in_h, in_w = img.shape[:2]
        ys = (np.linspace(0, in_h - 1, h)).astype(np.int32)
        xs = (np.linspace(0, in_w - 1, w)).astype(np.int32)
        return img[ys][:, xs]

    def _resize_nearest_2d(self, img: np.ndarray, h: int, w: int) -> np.ndarray:
        in_h, in_w = img.shape[:2]
        ys = (np.linspace(0, in_h - 1, h)).astype(np.int32)
        xs = (np.linspace(0, in_w - 1, w)).astype(np.int32)
        return img[ys][:, xs]

