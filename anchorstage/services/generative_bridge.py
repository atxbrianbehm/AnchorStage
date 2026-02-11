from __future__ import annotations

import numpy as np


class GenerativeBridgeService:
    def refresh(
        self,
        witness_reprojected: np.ndarray,
        void_map: np.ndarray,
        depth_map: np.ndarray,
        base_witness: np.ndarray,
        camera_metadata: dict,
    ) -> np.ndarray:
        del depth_map
        del camera_metadata
        out = witness_reprojected.copy()
        h, w, _ = out.shape
        base = self._resize_nearest(base_witness, h, w)

        # Masked fill only; non-void pixels remain locked.
        void = void_map.astype(bool)
        for y in range(h):
            for x in range(w):
                if not void[y, x]:
                    continue
                out[y, x] = self._neighbor_color(out, base, void, y, x)
        return np.clip(out, 0.0, 1.0).astype(np.float32)

    def _neighbor_color(
        self,
        current: np.ndarray,
        base: np.ndarray,
        void: np.ndarray,
        y: int,
        x: int,
    ) -> np.ndarray:
        h, w, _ = current.shape
        samples = []
        for r in range(1, 5):
            for dy, dx in ((-r, 0), (r, 0), (0, -r), (0, r)):
                yy = y + dy
                xx = x + dx
                if 0 <= yy < h and 0 <= xx < w and not void[yy, xx]:
                    samples.append(current[yy, xx])
            if samples:
                break
        if samples:
            return np.mean(np.array(samples, dtype=np.float32), axis=0) * 0.7 + base[y, x] * 0.3
        return base[y, x]

    def _resize_nearest(self, img: np.ndarray, h: int, w: int) -> np.ndarray:
        in_h, in_w, _ = img.shape
        ys = (np.linspace(0, in_h - 1, h)).astype(np.int32)
        xs = (np.linspace(0, in_w - 1, w)).astype(np.int32)
        return img[ys][:, xs]

