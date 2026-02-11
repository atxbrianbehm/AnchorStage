# AnchorStage Implementation Roadmap v2.0
## SHARP-Enhanced MVP Development Plan

---

## Overview

This roadmap reframes the AnchorStage MVP implementation to incorporate:
- **SHARP-inspired monocular Gaussian Splat regression** (<5s reconstruction)
- **Metric-aware camera system** (absolute scale, reduced drift)
- **Region primitives** (forward-compatible for building replacement)
- **Enhanced witness refresh** (normal conditioning, region locking)

---

## Phase 1: Foundation (Weeks 1-2)

### 1.1 Metric Depth Estimation
**Goal**: Replace placeholder depth with metric-aware estimator

**Tasks**:
- [ ] Integrate ZoeDepth or MiDaS v3.1 for metric depth prediction
- [ ] Add EXIF parsing for camera intrinsics (focal length, sensor size)
- [ ] Implement depth-to-metric conversion using camera metadata
- [ ] Validate depth accuracy on test images (indoor/outdoor scenes)
- [ ] Target: <2s inference on RTX 3080

**Acceptance Criteria**:
- Depth maps have absolute scale (meters)
- EXIF-based initialization improves accuracy by >20%
- Inference time <2s for 1080p images

**Files to Modify**:
- `anchorstage/reconstruction/depth_estimator.py` (new)
- `anchorstage/core/scene.py` (add metric_scale field)

---

### 1.2 SHARP-Inspired Gaussian Regression
**Goal**: Direct RGB → Gaussian parameters regression

**Tasks**:
- [ ] Implement Gaussian parameter regression head
  - Input: RGB image + depth map
  - Output: positions (Nx3), colors (Nx3), opacities (N), scales (Nx3), rotations (Nx4)
- [ ] Back-project depth to 3D point cloud
- [ ] Regress splat parameters from point cloud + RGB
- [ ] Implement splat pruning (remove low-opacity, redundant splats)
- [ ] Target: ~1M splats in <2s

**Technical Approach**:
```python
# Pseudo-code
def regress_gaussians(rgb_image, depth_map, camera_intrinsics):
    # 1. Back-project to 3D
    points_3d = backproject_depth(depth_map, camera_intrinsics)
    
    # 2. Initialize splat parameters
    positions = points_3d
    colors = sample_rgb_at_points(rgb_image, points_3d)
    
    # 3. Regress scales and rotations (simple heuristic for MVP)
    scales = estimate_local_scale(points_3d, k=8)  # k-NN
    rotations = estimate_surface_orientation(depth_map)
    opacities = estimate_confidence(depth_map)
    
    # 4. Prune and return
    return prune_splats(positions, colors, opacities, scales, rotations)
```

**Acceptance Criteria**:
- Output ~1M Gaussians per image
- Regression time <2s
- Splats render without major artifacts

**Files to Create**:
- `anchorstage/reconstruction/gaussian_regressor.py`
- `anchorstage/reconstruction/splat_utils.py`

---

### 1.3 Region Segmentation
**Goal**: Auto-segment scene into replaceable regions

**Tasks**:
- [ ] Implement depth-based clustering (k-means or DBSCAN)
- [ ] Detect major planes (RANSAC on point cloud)
- [ ] Semantic heuristics (sky = top + blue, ground = bottom)
- [ ] Generate region masks and metadata
- [ ] Target: <1s segmentation

**Region Output Format**:
```python
@dataclass
class Region:
    id: str  # e.g., "facade_001"
    mask: np.ndarray  # (H, W) binary
    plane_params: Optional[np.ndarray]  # (4,) [a,b,c,d]
    semantic_label: str  # "building_facade", "sky", "ground"
    splat_indices: List[int]
    locked: bool = False
```

**Acceptance Criteria**:
- Segments 3-10 regions per scene
- Major planes (facades, ground) detected >80% accuracy
- Segmentation time <1s

**Files to Create**:
- `anchorstage/reconstruction/region_segmenter.py`
- `anchorstage/core/region.py`

---

### 1.4 Enhanced Scene Container
**Goal**: Update data model for regions and metric scale

**Tasks**:
- [ ] Add `regions: List[Region]` to Scene class
- [ ] Add `metric_scale: float` to GaussianSplats
- [ ] Add `normal_map: np.ndarray` to reconstruction outputs
- [ ] Update serialization (save/load with regions)
- [ ] Add region visualization helpers

**Acceptance Criteria**:
- Scene can save/load with regions
- Region masks export correctly
- Backward compatible with v1.0 scenes (regions optional)

**Files to Modify**:
- `anchorstage/core/scene.py`
- `anchorstage/core/gaussian_splats.py` (new)
- `anchorstage/io/scene_serializer.py`

---

## Phase 2: Camera + Rendering (Weeks 3-4)

### 2.1 Metric-Aware Camera Rig
**Goal**: Film-style camera with metric coordinates

**Tasks**:
- [ ] Implement Camera class with metric position/rotation
- [ ] Add focal length presets (24, 35, 50, 85, 135mm)
- [ ] Compute projection/view matrices from camera params
- [ ] Add camera movement modes (orbit, dolly, truck, pedestal)
- [ ] Validate metric consistency across moves

**Acceptance Criteria**:
- Camera positions in meters (not arbitrary units)
- Dolly moves maintain scale consistency
- Focal length changes produce correct FOV

**Files to Create**:
- `anchorstage/camera/camera_rig.py`
- `anchorstage/camera/movement_modes.py`

---

### 2.2 Gaussian Splat Renderer
**Goal**: Real-time proxy rendering with multi-pass output

**Tasks**:
- [ ] Implement GPU-accelerated splat rasterizer
  - Sort splats by depth
  - Project to screen space
  - Alpha-composite with depth testing
- [ ] Output color, depth, normal, confidence passes
- [ ] Add region mask rendering (per-region ID buffer)
- [ ] Optimize for 30+ FPS @ 720p

**Technical Notes**:
- Use existing libraries (gsplat, diff-gaussian-rasterization) or custom CUDA
- Implement LOD for distant splats
- Frustum culling for off-screen splats

**Acceptance Criteria**:
- Real-time rendering at 720p (30+ FPS)
- Multi-pass output (color, depth, normal, masks)
- No major artifacts (holes, z-fighting)

**Files to Create**:
- `anchorstage/rendering/splat_renderer.py`
- `anchorstage/rendering/rasterizer.cu` (optional CUDA)

---

### 2.3 Enhanced Witness Refresh Pipeline
**Goal**: Metric-aware warping with region locking

**Tasks**:
- [ ] Implement metric-aware image warping
  - Use proxy depth for 3D reprojection
  - Warp base witness to target pose
  - Identify disocclusions (void map)
- [ ] Add region-based locking
  - Mark locked regions in void map
  - Preserve high-confidence areas
- [ ] Implement normal-conditioned inpainting
  - Use proxy normals as conditioning
  - Respect locked regions
- [ ] Add soft blending at region boundaries

**Witness Refresh Flow**:
```
base_witness + proxy_depth → warp → disocclusion_mask
                                ↓
                    apply region locks (preserve facades)
                                ↓
                    inpaint voids (normal-conditioned)
                                ↓
                    witness_refreshed
```

**Acceptance Criteria**:
- Warping preserves metric scale
- Locked regions never modified
- Inpaint quality improved with normal conditioning
- <10% drift over 3-step sequence

**Files to Modify**:
- `anchorstage/witness/refresh_pipeline.py`
- `anchorstage/witness/warping.py` (new)
- `anchorstage/witness/inpainting.py`

---

### 2.4 Confidence Visualization
**Goal**: Real-time confidence metric with color coding

**Tasks**:
- [ ] Implement enhanced confidence formula:
  ```
  confidence = (1 - void_coverage) * depth_confidence * angle_confidence
  ```
- [ ] Add color-coded overlay (green/yellow/red)
- [ ] Display confidence meter in UI
- [ ] Add confidence threshold warnings

**Acceptance Criteria**:
- Confidence updates in real-time during camera moves
- Color coding clearly indicates safe/risky zones
- Formula matches PRD specification

**Files to Create**:
- `anchorstage/camera/confidence_metric.py`
- `anchorstage/ui/confidence_overlay.py`

---

## Phase 3: Generation + Export (Weeks 5-6)

### 3.1 Enhanced Generation Bridge
**Goal**: Multi-modal conditioning for better quality

**Tasks**:
- [ ] Update conditioning stack:
  - Primary: witness_refreshed
  - Depth: proxy_depth (metric)
  - Normal: proxy_normal (NEW)
  - Mask: void_map + region_locks
  - Metadata: camera params, style
- [ ] Implement region-aware generation
  - Locked regions preserved
  - Void regions inpainted
- [ ] Add generation quality validation
  - Check for artifacts
  - Verify locked regions unchanged

**Conditioning Format**:
```python
{
    "image": witness_refreshed,
    "depth": proxy_depth,
    "normal": proxy_normal,  # NEW
    "mask": void_map,
    "locked_regions": region_lock_mask,  # NEW
    "camera_metadata": {...},
    "style_prompt": "photorealistic, architectural"
}
```

**Acceptance Criteria**:
- Normal conditioning improves inpaint quality
- Locked regions 100% preserved
- Generation respects metric scale

**Files to Modify**:
- `anchorstage/generation/bridge.py`
- `anchorstage/generation/conditioning.py` (new)

---

### 3.2 Multi-Pass Export System
**Goal**: Compositing-native outputs with region metadata

**Tasks**:
- [ ] Implement pass export:
  - `beauty.exr` (linear color space)
  - `depth.exr` (metric depth)
  - `normal.exr` (world-space normals)
  - `void_map.png` (inpainted regions)
  - `region_masks/` (per-region PNG)
  - `proxy_render.png` (reference geometry)
  - `metadata.json` (camera, regions, confidence)
- [ ] Add EXR support (OpenEXR library)
- [ ] Implement batch export for sequences
- [ ] Add export presets (Nuke, After Effects, Blender)

**Metadata JSON Format**:
```json
{
  "camera": {
    "position": [x, y, z],
    "rotation": [yaw, pitch, roll],
    "focal_length": 50,
    "metric_scale": 1.0
  },
  "regions": [
    {
      "id": "facade_001",
      "semantic_label": "building_facade",
      "locked": false,
      "plane_params": [a, b, c, d]
    }
  ],
  "confidence": 0.85,
  "generation_params": {...}
}
```

**Acceptance Criteria**:
- All passes export correctly
- EXR files readable in Nuke/After Effects
- Region metadata preserved
- Batch export works for sequences

**Files to Create**:
- `anchorstage/export/pass_exporter.py`
- `anchorstage/export/formats.py`

---

### 3.3 Region Metadata Export
**Goal**: Enable future building replacement workflows

**Tasks**:
- [ ] Export region masks as separate files
- [ ] Include plane parameters in metadata
- [ ] Add region visualization (overlay on beauty pass)
- [ ] Document region data format for external tools

**Future Use Case**:
```
1. User exports scene with regions
2. External tool (UTDG) generates new building for region
3. User imports new building, replaces region
4. Re-render from all cameras
```

**Acceptance Criteria**:
- Region masks export correctly
- Plane parameters accurate (validated against ground truth)
- Documentation clear for external integration

**Files to Create**:
- `anchorstage/export/region_exporter.py`
- `docs/region_data_format.md`

---

## Phase 4: Polish + Demo (Weeks 7-8)

### 4.1 UI/UX Implementation
**Goal**: Intuitive camera controls and region visualization

**Tasks**:
- [ ] Camera control gizmos (orbit, dolly, truck)
- [ ] Focal length slider with presets
- [ ] Region overlay toggle
- [ ] Confidence meter display
- [ ] Real-time proxy preview
- [ ] Generation progress indicator

**Acceptance Criteria**:
- Camera controls feel responsive
- Region overlay clearly shows segmentation
- Confidence updates in real-time
- UI matches PRD mockups

**Files to Create**:
- `anchorstage/ui/camera_controls.py`
- `anchorstage/ui/region_overlay.py`

---

### 4.2 Performance Optimization
**Goal**: Meet <5s reconstruction, 30+ FPS rendering targets

**Tasks**:
- [ ] Profile reconstruction pipeline
  - Identify bottlenecks
  - Optimize depth estimation (TensorRT, FP16)
  - Parallelize stages where possible
- [ ] Profile rendering pipeline
  - Optimize splat sorting
  - Implement LOD system
  - Add frustum culling
- [ ] Memory optimization
  - Splat pruning
  - Lazy loading for large scenes
- [ ] Validate targets on reference hardware (RTX 3080)

**Performance Targets**:
| Operation | Target | Current | Status |
|-----------|--------|---------|--------|
| Reconstruction | <5s | TBD | ⏳ |
| Rendering @ 720p | 30+ FPS | TBD | ⏳ |
| Rendering @ 1080p | 15+ FPS | TBD | ⏳ |

**Acceptance Criteria**:
- 90th percentile reconstruction <5s
- Real-time rendering at 720p
- Memory usage <500 MB per scene

---

### 4.3 Updated Demo Materials
**Goal**: Showcase SHARP speed, metric scale, region extensibility

**Tasks**:
- [ ] Update demo script to emphasize:
  - <5s reconstruction (vs. competitors' minutes)
  - Metric-aware camera moves (no scale drift)
  - Region primitives (future building replacement)
- [ ] Create comparison slides:
  - SHARP vs. depth projection quality
  - AnchorStage vs. Martini/LTX/ArtCraft
- [ ] Add region visualization demo
- [ ] Prepare backup branches for live demo

**Key Demo Moments**:
1. **S1**: Upload image → <5s reconstruction (timer visible)
2. **S2**: Show Gaussian splats + region overlay
3. **S3**: Camera dolly with metric scale consistency
4. **S4**: Region locking during witness refresh
5. **S5**: Export with region metadata

**Acceptance Criteria**:
- Demo runs in <5 minutes
- All technical claims demonstrated
- Backup branches tested

**Files to Update**:
- `demo/anchorstage_anime_5min_script.md`
- `demo/anchorstage_tech_proof_checklist.md`

---

### 4.4 Documentation
**Goal**: Complete technical and user documentation

**Tasks**:
- [ ] API documentation (Scene, Camera, Region classes)
- [ ] User guide (camera controls, region workflow)
- [ ] Developer guide (SHARP implementation, extension points)
- [ ] Region data format specification
- [ ] Compositing workflow guide (Nuke, After Effects)

**Acceptance Criteria**:
- All public APIs documented
- User guide covers common workflows
- Developer guide enables extensions

**Files to Create**:
- `docs/api_reference.md`
- `docs/user_guide.md`
- `docs/developer_guide.md`
- `docs/region_data_format.md`
- `docs/compositing_workflows.md`

---

## Testing Strategy

### Unit Tests
- [ ] Gaussian regression output validation
- [ ] Region segmentation coverage
- [ ] Witness refresh preserves locked pixels
- [ ] Confidence metric bounds
- [ ] Camera projection matrices

### Integration Tests
- [ ] End-to-end: image → reconstruction → generation
- [ ] Multi-step sequence drift <10%
- [ ] Region export/import roundtrip
- [ ] Pass export validation (EXR readable)

### Performance Tests
- [ ] Reconstruction <5s (90th percentile)
- [ ] Rendering 30+ FPS @ 720p
- [ ] Memory usage <500 MB per scene

### User Acceptance Tests
- [ ] Can users generate 5+ believable novel views?
- [ ] Do camera moves feel "cinematic"?
- [ ] Are outputs usable in Nuke/After Effects?

---

## Risk Mitigation Plan

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Reconstruction >5s | Medium | High | Progressive refinement, TensorRT, FP16 |
| Splat artifacts | Medium | Medium | Confidence filtering, soft blending |
| Region segmentation fails | Low | Low | Fallback to single region |
| Memory overflow | Low | Medium | Splat pruning, LOD |

### Quality Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Hallucinations in large moves | High | High | Move limits, incremental refresh |
| Scale drift in sequences | Medium | High | Metric-aware warping, base witness anchor |
| Poor inpaint quality | Medium | Medium | Normal conditioning, locked regions |

---

## Success Metrics

### Technical Metrics
- ✅ Reconstruction <5s (90th percentile)
- ✅ Rendering 30+ FPS @ 720p
- ✅ Witness drift <10% over 3-step sequence
- ✅ Region segmentation >80% accuracy

### User Metrics
- ✅ 5+ believable novel views from single image
- ✅ Camera moves feel "cinematic" (user survey)
- ✅ Outputs usable in professional tools

### Business Metrics
- ✅ Demo validates "building replacement" narrative
- ✅ Competitive differentiation clear vs. Martini/LTX/ArtCraft
- ✅ Forward-compatible architecture for procedural editing

---

## Competitive Positioning Summary

### vs. Martini.ai
**Their Strength**: Witness refresh for continuity  
**Our Advantage**: Metric-aware splats (<5s reconstruction) + region primitives

### vs. LTX Studio
**Their Strength**: Timeline integration  
**Our Advantage**: Faster reconstruction, compositing-native outputs

### vs. ArtCraft AI
**Their Strength**: Craft-like controls  
**Our Advantage**: Forward-compatible data model for procedural editing

### Key Differentiator
**SHARP-inspired monocular splatting** enables:
- **10x faster reconstruction** (5s vs. 30s+)
- **Metric scale** for consistent camera moves
- **Region primitives** for future building replacement
- **25–34% better quality** (LPIPS) vs. depth-only methods

---

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1: Foundation | Weeks 1-2 | Metric depth, Gaussian regression, region segmentation |
| Phase 2: Camera + Rendering | Weeks 3-4 | Camera rig, splat renderer, witness refresh |
| Phase 3: Generation + Export | Weeks 5-6 | Enhanced conditioning, multi-pass export, region metadata |
| Phase 4: Polish + Demo | Weeks 7-8 | UI/UX, performance optimization, demo materials |

**Total**: 8 weeks to MVP

---

## Next Steps

1. **Immediate** (Week 1):
   - Set up development environment
   - Integrate ZoeDepth for metric depth
   - Implement basic Gaussian regression

2. **Short-term** (Weeks 2-4):
   - Complete reconstruction pipeline
   - Build camera rig + renderer
   - Validate <5s reconstruction target

3. **Medium-term** (Weeks 5-8):
   - Enhance generation bridge
   - Implement multi-pass export
   - Polish UI and prepare demo

4. **Long-term** (Post-MVP):
   - Video input support
   - Building replacement workflow
   - Trim sheet generation
