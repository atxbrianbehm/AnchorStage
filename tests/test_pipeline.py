import unittest

import numpy as np

from anchorstage.models import Camera, ExtraAsset
from anchorstage.pipeline import AnchorStagePipeline


def make_img(h: int = 180, w: int = 320) -> np.ndarray:
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    xx = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    img = np.stack([0.2 + xx * 0.7, 0.25 + yy * 0.5, 0.3 + (1.0 - xx) * 0.4], axis=2)
    return np.clip(img, 0.0, 1.0)


def sprite(color: tuple[float, float, float]) -> np.ndarray:
    s = np.zeros((24, 16, 4), dtype=np.float32)
    s[:, :, :3] = np.array(color, dtype=np.float32)[None, None, :]
    s[:, :, 3] = 0.9
    return s


class PipelineTests(unittest.TestCase):
    def test_end_to_end_outputs(self) -> None:
        pipe = AnchorStagePipeline()
        scene = pipe.create_scene(make_img(), scene_id="t_scene")
        assets = [
            ExtraAsset("a", sprite((1.0, 0.2, 0.2)), 1.7, 0.0, "walk", 1.0),
            ExtraAsset("b", sprite((0.2, 1.0, 0.2)), 1.6, 0.0, "idle", 0.0),
        ]
        pipe.configure_extras(scene, assets, density=8, motion_mix={"walk": 0.5, "idle": 0.5}, seed=3)
        cam = Camera(
            position=np.array([0.1, 0.0, 0.0], dtype=np.float32),
            rotation_xyz_deg=np.array([0.0, 2.0, 0.0], dtype=np.float32),
            width=640,
            height=360,
        )

        frame = pipe.generate_frame(scene, cam, assets)
        self.assertEqual(frame.beauty.shape, (360, 640, 3))
        self.assertEqual(frame.depth.shape, (360, 640))
        self.assertEqual(frame.void_map.shape, (360, 640))
        self.assertEqual(frame.extras_id_pass.shape, (360, 640))
        self.assertGreaterEqual(frame.confidence_score, 0.0)
        self.assertLessEqual(frame.confidence_score, 1.0)

    def test_locked_pixels_preserved(self) -> None:
        pipe = AnchorStagePipeline()
        scene = pipe.create_scene(make_img())
        cam = Camera(
            position=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            rotation_xyz_deg=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            width=320,
            height=180,
        )
        assets: list[ExtraAsset] = []
        frame = pipe.generate_frame(scene, cam, assets)
        non_void = frame.void_map == 0
        delta = np.abs(frame.witness_refreshed - frame.witness_reprojected).sum(axis=2)
        self.assertTrue(np.all(delta[non_void] < 1e-6))

    def test_confidence_matches_void_ratio(self) -> None:
        pipe = AnchorStagePipeline()
        scene = pipe.create_scene(make_img())
        cam = Camera(
            position=np.array([0.25, 0.0, 0.0], dtype=np.float32),
            rotation_xyz_deg=np.array([0.0, 8.0, 0.0], dtype=np.float32),
            width=480,
            height=270,
        )
        frame = pipe.generate_frame(scene, cam, [])
        void_ratio = float(frame.void_map.sum() / frame.void_map.size)
        expected = 1.0 - void_ratio
        self.assertAlmostEqual(frame.confidence_score, expected, places=5)


if __name__ == "__main__":
    unittest.main()

