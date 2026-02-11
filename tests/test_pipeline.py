import json
import os
import tempfile
import unittest

import numpy as np

from anchorstage.models import Camera, ExtraAsset, Region
from anchorstage.pipeline import AnchorStagePipeline


def make_img(h: int = 180, w: int = 320) -> np.ndarray:
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    xx = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    ones = np.ones((h, w), dtype=np.float32)
    r = 0.2 + xx * ones * 0.7
    g = 0.25 + yy * ones * 0.5
    b = 0.3 + (1.0 - xx) * ones * 0.4
    img = np.stack([r, g, b], axis=2)
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

    def test_enhanced_confidence_formula(self) -> None:
        pipe = AnchorStagePipeline()
        scene = pipe.create_scene(make_img())
        cam = Camera(
            position=np.array([0.25, 0.0, 0.0], dtype=np.float32),
            rotation_xyz_deg=np.array([0.0, 8.0, 0.0], dtype=np.float32),
            width=480,
            height=270,
        )
        frame = pipe.generate_frame(scene, cam, [])
        # Confidence should be between 0 and 1
        self.assertGreaterEqual(frame.confidence_score, 0.0)
        self.assertLessEqual(frame.confidence_score, 1.0)
        # Metadata should contain the 3-factor breakdown
        self.assertIn("confidence", frame.metadata)
        conf = frame.metadata["confidence"]
        self.assertIn("overall", conf)
        self.assertIn("depth_confidence", conf)
        self.assertIn("angle_confidence", conf)
        self.assertAlmostEqual(conf["overall"], frame.confidence_score, places=5)


class ReconstructionTests(unittest.TestCase):
    def test_reconstruction_produces_regions(self) -> None:
        pipe = AnchorStagePipeline()
        scene = pipe.create_scene(make_img(), scene_id="region_test")
        self.assertGreater(len(scene.regions), 0)
        for r in scene.regions:
            self.assertIsInstance(r, Region)
            self.assertEqual(r.mask.shape, scene.depth_map.shape)
            self.assertIn(r.semantic_label, ("sky", "ground", "building_facade", "unknown"))

    def test_reconstruction_produces_normal_map(self) -> None:
        pipe = AnchorStagePipeline()
        scene = pipe.create_scene(make_img())
        self.assertIsNotNone(scene.normal_map)
        h, w = scene.depth_map.shape
        self.assertEqual(scene.normal_map.shape, (h, w, 3))
        # Normals should be unit vectors (length ~1)
        lengths = np.linalg.norm(scene.normal_map, axis=2)
        self.assertTrue(np.allclose(lengths, 1.0, atol=0.01))

    def test_reconstruction_timing(self) -> None:
        pipe = AnchorStagePipeline()
        scene = pipe.create_scene(make_img())
        self.assertGreater(scene.reconstruction_time_s, 0.0)

    def test_metric_scale(self) -> None:
        pipe = AnchorStagePipeline()
        scene = pipe.create_scene(make_img())
        self.assertEqual(scene.metric_scale, 1.0)
        # Depth values should be in metric range (meters)
        self.assertGreater(float(scene.depth_map.min()), 0.0)
        self.assertLess(float(scene.depth_map.max()), 20.0)

    def test_splat_count(self) -> None:
        pipe = AnchorStagePipeline()
        h, w = 180, 320
        scene = pipe.create_scene(make_img(h, w))
        # v2.0: all pixels become splats
        self.assertEqual(len(scene.gaussian_splats), h * w)


class RegionLockingTests(unittest.TestCase):
    def test_lock_unlock_region(self) -> None:
        pipe = AnchorStagePipeline()
        scene = pipe.create_scene(make_img())
        self.assertGreater(len(scene.regions), 0)
        rid = scene.regions[0].id
        self.assertFalse(scene.regions[0].locked)
        self.assertTrue(pipe.lock_region(scene, rid))
        self.assertTrue(scene.regions[0].locked)
        self.assertTrue(pipe.unlock_region(scene, rid))
        self.assertFalse(scene.regions[0].locked)

    def test_lock_nonexistent_region(self) -> None:
        pipe = AnchorStagePipeline()
        scene = pipe.create_scene(make_img())
        self.assertFalse(pipe.lock_region(scene, "nonexistent_region"))

    def test_locked_region_preserved_in_generation(self) -> None:
        pipe = AnchorStagePipeline()
        scene = pipe.create_scene(make_img())
        # Lock all regions
        for r in scene.regions:
            pipe.lock_region(scene, r.id)
        cam = Camera(
            position=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            rotation_xyz_deg=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            width=320,
            height=180,
        )
        frame = pipe.generate_frame(scene, cam, [])
        # Locked region pixels should not be void
        lock_mask = pipe._build_region_lock_mask(scene, 180, 320)
        locked_pixels = lock_mask.astype(bool)
        if locked_pixels.any():
            self.assertTrue(np.all(frame.void_map[locked_pixels] == 0))


class FrameOutputTests(unittest.TestCase):
    def test_normal_map_in_frame(self) -> None:
        pipe = AnchorStagePipeline()
        scene = pipe.create_scene(make_img())
        cam = Camera(
            position=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            rotation_xyz_deg=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            width=320,
            height=180,
        )
        frame = pipe.generate_frame(scene, cam, [])
        self.assertIsNotNone(frame.normal_map)
        self.assertEqual(frame.normal_map.shape[2], 3)

    def test_region_masks_in_frame(self) -> None:
        pipe = AnchorStagePipeline()
        scene = pipe.create_scene(make_img())
        cam = Camera(
            position=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            rotation_xyz_deg=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            width=320,
            height=180,
        )
        frame = pipe.generate_frame(scene, cam, [])
        self.assertIsNotNone(frame.region_masks)
        self.assertEqual(len(frame.region_masks), len(scene.regions))

    def test_metadata_in_frame(self) -> None:
        pipe = AnchorStagePipeline()
        scene = pipe.create_scene(make_img(), scene_id="meta_test")
        cam = Camera(
            position=np.array([0.1, 0.2, 0.3], dtype=np.float32),
            rotation_xyz_deg=np.array([0.0, 5.0, 0.0], dtype=np.float32),
        )
        frame = pipe.generate_frame(scene, cam, [])
        meta = frame.metadata
        self.assertIsNotNone(meta)
        self.assertEqual(meta["scene_id"], "meta_test")
        self.assertIn("camera", meta)
        self.assertIn("regions", meta)
        self.assertIn("confidence", meta)
        self.assertGreater(meta["num_splats"], 0)
        self.assertGreater(meta["num_regions"], 0)
        self.assertGreater(meta["reconstruction_time_s"], 0.0)


class ExportTests(unittest.TestCase):
    def test_export_frame(self) -> None:
        pipe = AnchorStagePipeline()
        scene = pipe.create_scene(make_img())
        cam = Camera(
            position=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            rotation_xyz_deg=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            width=320,
            height=180,
        )
        frame = pipe.generate_frame(scene, cam, [])
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = pipe.export_frame(frame, tmpdir)
            self.assertIn("beauty", paths)
            self.assertIn("depth", paths)
            self.assertIn("void_map", paths)
            self.assertIn("proxy_render", paths)
            self.assertIn("metadata", paths)
            # Verify files exist
            for path in paths.values():
                self.assertTrue(os.path.exists(path))
            # Verify metadata JSON is valid
            with open(paths["metadata"]) as f:
                meta = json.load(f)
            self.assertIn("camera", meta)
            self.assertIn("regions", meta)

    def test_export_region_masks(self) -> None:
        pipe = AnchorStagePipeline()
        scene = pipe.create_scene(make_img())
        cam = Camera(
            position=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            rotation_xyz_deg=np.array([0.0, 0.0, 0.0], dtype=np.float32),
            width=320,
            height=180,
        )
        frame = pipe.generate_frame(scene, cam, [])
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = pipe.export_frame(frame, tmpdir)
            # Should have region mask entries
            region_keys = [k for k in paths if k.startswith("region_mask_")]
            self.assertGreater(len(region_keys), 0)


if __name__ == "__main__":
    unittest.main()

