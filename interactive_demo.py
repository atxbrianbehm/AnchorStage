"""Interactive AnchorStage v2.0 demo - run with: python -i interactive_demo.py"""
import numpy as np
from anchorstage.models import Camera, ExtraAsset
from anchorstage.pipeline import AnchorStagePipeline

# Setup
pipe = AnchorStagePipeline()
h, w = 540, 960
yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
xx = np.linspace(0, 1, w, dtype=np.float32)[None, :]
ones = np.ones((h, w), dtype=np.float32)
img = np.clip(
    np.stack([0.15 + 0.55 * (1 - yy) * ones, 0.25 + 0.35 * xx * ones, 0.45 + 0.35 * (yy * (1 - xx))], axis=2),
    0, 1,
)

scene = pipe.create_scene(img, scene_id="interactive_demo")
print(f"\nScene ready: {len(scene.gaussian_splats):,} splats, {len(scene.regions)} regions")
print(f"Regions: {[r.id for r in scene.regions]}")
print()
print("=" * 50)
print("Interactive AnchorStage v2.0 - Try these:")
print("=" * 50)
print()
print("  # Lock a region")
print('  pipe.lock_region(scene, "facade_001")')
print()
print("  # Move camera and generate a frame")
print("  cam = Camera(position=np.array([0.1, 0, 0], dtype=np.float32),")
print("               rotation_xyz_deg=np.array([0, 2, 0], dtype=np.float32))")
print("  frame = pipe.generate_frame(scene, cam, [])")
print()
print("  # Check confidence breakdown")
print('  print(frame.metadata["confidence"])')
print()
print("  # Export all passes to disk")
print('  pipe.export_frame(frame, "./demo_output")')
print()
print("  # List regions")
print("  for r in scene.regions: print(f'{r.id}: locked={r.locked}')")
print()
