# AnchorStage Technical Architecture v2.0
## SHARP-Enhanced Monocular Reconstruction

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AnchorStage MVP v2.0                      │
│                  (WitnessCam Architecture)                   │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Reconstruction│    │  Camera Rig  │    │  Generation  │
│    Engine     │    │   + Witness  │    │    Bridge    │
│  (SHARP-based)│    │   Refresh    │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌──────────────┐
                    │    Scene     │
                    │  Container   │
                    │  (with regions)│
                    └──────────────┘
```

---

## 2. Reconstruction Engine (Enhanced)

### 2.1 Pipeline Architecture

```
Input Image (RGB)
      │
      ▼
┌─────────────────────────────────────┐
│  Stage 1: Metric Depth Estimation   │
│  - MiDaS v3.1 or ZoeDepth           │
│  - Output: metric depth map         │
│  - Target: <2s                      │
└─────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│  Stage 2: Gaussian Regression       │
│  - SHARP-inspired architecture      │
│  - Direct RGB → Gaussian params     │
│  - Output: ~1M splats               │
│  - Target: <2s                      │
└─────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│  Stage 3: Region Segmentation       │
│  - Depth clustering or SAM          │
│  - Output: region masks + planes    │
│  - Target: <1s                      │
└─────────────────────────────────────┘
      │
      ▼
Total: <5s on RTX 3080-class GPU
```

### 2.2 Gaussian Splat Representation

**Data Structure:**
```python
class GaussianSplats:
    positions: np.ndarray  # (N, 3) - metric XYZ coordinates
    colors: np.ndarray     # (N, 3) - RGB [0,1]
    opacities: np.ndarray  # (N,) - alpha [0,1]
    scales: np.ndarray     # (N, 3) - per-axis scale
    rotations: np.ndarray  # (N, 4) - quaternions
    
    # Metadata
    count: int = ~1_000_000
    metric_scale: float  # meters per unit
    confidence: np.ndarray  # (N,) - per-splat confidence
```

**Key Advantages over Depth Projection:**
- **Metric awareness**: Absolute scale, not relative
- **Multi-scale representation**: Splats adapt to surface complexity
- **Efficient rendering**: GPU-accelerated splatting
- **Quality**: 25–34% better LPIPS vs. depth-only methods

### 2.3 Region Segmentation

**Purpose**: Enable future building replacement without MVP complexity

**Implementation:**
```python
class Region:
    id: str
    mask: np.ndarray  # (H, W) binary mask
    plane_params: Optional[np.ndarray]  # (4,) [a,b,c,d] for ax+by+cz+d=0
    semantic_label: str  # "building_facade", "sky", "ground", etc.
    splat_indices: List[int]  # which splats belong to this region
    locked: bool = False  # preserve during generation
```

**Segmentation Strategy (MVP):**
1. **Depth clustering**: Group splats by depth ranges
2. **Plane fitting**: RANSAC on major surfaces
3. **Semantic hints**: Sky detection (top + blue), ground (bottom)
4. **Fallback**: Single "foreground" region if clustering fails

**Future Enhancement:**
- SAM (Segment Anything Model) for semantic segmentation
- User-drawn masks override auto-segmentation

---

## 3. Scene Container (Enhanced Data Model)

### 3.1 Core Structure

```python
@dataclass
class Scene:
    id: str
    
    # Witness states
    base_witness: Image  # Original upload
    base_witness_metadata: dict  # EXIF, camera params
    
    # Reconstruction outputs
    gaussian_splats: GaussianSplats
    depth_map: np.ndarray  # (H, W) metric depth
    normal_map: np.ndarray  # (H, W, 3) surface normals
    confidence_map: np.ndarray  # (H, W) reconstruction confidence
    
    # Region primitives (NEW in v2.0)
    regions: List[Region]
    
    # Camera states
    cameras: List[Camera]
    active_camera_id: str
    
    # Rendering cache
    proxy_renders: Dict[str, ProxyRender]  # camera_id -> render
    
    # Generation history
    witness_refreshes: List[WitnessRefresh]
    generated_frames: List[GeneratedFrame]
```

### 3.2 Region-Based Forward Compatibility

**MVP Usage:**
- Export region masks with frames
- Lock regions during witness refresh
- Visualize regions in UI (optional overlay)

**Future Usage:**
- Select region → replace with procedural building
- Extract region → generate trim sheet components
- Region as "slot" for UTDG/Promptscape output

**Example Workflow (Future):**
```
1. Capture scene → auto-segment facade region
2. Navigate camera → generate novel views
3. Select facade region → "Replace with Gothic cathedral"
4. System: generates new building, composites into region
5. Export: final frame + region metadata for further editing
```

---

## 4. Camera Rig + Witness Refresh

### 4.1 Camera Model

```python
@dataclass
class Camera:
    id: str
    
    # Transform
    position: np.ndarray  # (3,) metric XYZ
    rotation: np.ndarray  # (3,) yaw/pitch/roll or (4,) quaternion
    
    # Optics
    focal_length: float  # mm
    sensor_width: float  # mm (e.g., 36 for full-frame)
    aspect_ratio: float  # e.g., 16/9
    
    # Derived
    fov: float  # computed from focal_length + sensor
    projection_matrix: np.ndarray  # (4, 4)
    view_matrix: np.ndarray  # (4, 4)
```

**Film-Style Presets:**
- Wide: 24mm
- Standard: 35mm, 50mm
- Portrait: 85mm
- Telephoto: 135mm

### 4.2 Witness Refresh Pipeline (Metric-Aware)

```
Input: base_witness, target_camera, gaussian_splats, regions
      │
      ▼
┌─────────────────────────────────────┐
│  Step 1: Render Proxy from Target  │
│  - Splat rendering at target pose   │
│  - Output: proxy_color, proxy_depth │
└─────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│  Step 2: Warp Base Witness          │
│  - Use proxy_depth for metric warp  │
│  - Identify disocclusions           │
│  - Output: warped_witness, void_map │
└─────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│  Step 3: Lock Regions               │
│  - Mark locked regions in void_map  │
│  - Preserve high-confidence areas   │
└─────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│  Step 4: Inpaint Voids              │
│  - Condition on proxy_color/normals │
│  - Respect locked regions           │
│  - Output: witness_refreshed        │
└─────────────────────────────────────┘
```

**Key Enhancement (v2.0):**
- **Metric warping** reduces scale drift across multi-step sequences
- **Region-aware locking** preserves facades for future replacement
- **Normal conditioning** improves inpaint quality

---

## 5. Proxy Rendering System

### 5.1 Gaussian Splatting Renderer

**Algorithm:**
1. Sort splats by depth (painter's algorithm)
2. Project Gaussians to screen space
3. Alpha-composite front-to-back
4. Output color + depth + normals

**Performance:**
- Real-time at 720p (30+ FPS)
- 1080p at 15+ FPS
- GPU-accelerated (CUDA or Metal)

**Outputs per Frame:**
```python
@dataclass
class ProxyRender:
    color: np.ndarray  # (H, W, 3) RGB
    depth: np.ndarray  # (H, W) metric depth
    normal: np.ndarray  # (H, W, 3) surface normals
    confidence: np.ndarray  # (H, W) view confidence
    disocclusion_mask: np.ndarray  # (H, W) bool - holes from novel view
    region_masks: Dict[str, np.ndarray]  # region_id -> (H, W) bool
```

### 5.2 Confidence Metric (Enhanced)

**Formula:**
```
confidence = (1 - void_coverage) * depth_confidence * angle_confidence

where:
  void_coverage = void_pixels / total_pixels
  depth_confidence = 1 - (depth_uncertainty / max_depth)
  angle_confidence = cos(angle_from_base_view)  # penalize extreme angles
```

**Visualization:**
- Green: confidence > 0.8 (safe)
- Yellow: 0.5 < confidence < 0.8 (caution)
- Red: confidence < 0.5 (high risk)

---

## 6. Generation Bridge

### 6.1 Conditioning Stack

**Inputs to Generative Model:**
```python
{
    "image": witness_refreshed,  # Primary conditioning
    "depth": proxy_depth,  # Geometric guide
    "normal": proxy_normal,  # Surface orientation
    "mask": void_map,  # Inpaint regions only
    "locked_regions": region_lock_mask,  # Preserve facades
    "camera_metadata": {
        "focal_length": 50,
        "position": [x, y, z],
        "rotation": [yaw, pitch, roll]
    },
    "style_prompt": "photorealistic, architectural photography"
}
```

**Output:**
```python
@dataclass
class GeneratedFrame:
    beauty: np.ndarray  # (H, W, 3) final render
    depth: np.ndarray  # (H, W) generated depth
    passes: Dict[str, np.ndarray]  # additional passes
    metadata: dict
```

### 6.2 Pass Export System

**Compositing-Ready Outputs:**
- `beauty.exr` - Final render (linear color space)
- `depth.exr` - Metric depth
- `normal.exr` - World-space normals
- `void_map.png` - Inpainted regions
- `region_masks/` - Per-region masks
- `proxy_render.png` - Reference geometry
- `metadata.json` - Camera, regions, confidence

---

## 7. Performance Optimization Strategy

### 7.1 Reconstruction (<5s target)

| Stage | Current | Target | Optimization |
|-------|---------|--------|--------------|
| Depth estimation | 3-5s | <2s | TensorRT, FP16 |
| Gaussian regression | 2-3s | <2s | Batched inference |
| Region segmentation | 1-2s | <1s | GPU clustering |
| **Total** | 6-10s | **<5s** | Pipeline parallelization |

### 7.2 Rendering (Real-time target)

- **720p**: 30+ FPS (achieved)
- **1080p**: 15+ FPS (target)
- **4K**: 5+ FPS (future)

**Techniques:**
- Level-of-detail (LOD) for distant splats
- Frustum culling
- Occlusion culling (future)

### 7.3 Memory Management

**Typical Scene:**
- Gaussian splats: ~1M × 32 bytes = 32 MB
- Depth/normal maps: 1080p × 4 bytes × 2 = 16 MB
- Region masks: ~10 regions × 1080p × 1 byte = 2 MB
- **Total**: <100 MB per scene (manageable)

---

## 8. Implementation Phases

### Phase 1: Core Reconstruction (Week 1-2)
- [ ] Integrate metric depth estimator (ZoeDepth or MiDaS v3.1)
- [ ] Implement SHARP-inspired Gaussian regression
- [ ] Basic region segmentation (depth clustering)
- [ ] Validate <5s reconstruction target

### Phase 2: Camera + Witness (Week 3-4)
- [ ] Metric-aware camera rig
- [ ] Gaussian splat renderer (720p real-time)
- [ ] Witness refresh pipeline with region locking
- [ ] Confidence visualization

### Phase 3: Generation + Export (Week 5-6)
- [ ] Generation bridge with enhanced conditioning
- [ ] Multi-pass export system
- [ ] Region metadata export
- [ ] End-to-end validation

### Phase 4: Polish + Demo (Week 7-8)
- [ ] UI/UX for camera controls
- [ ] Region visualization overlay
- [ ] Performance profiling + optimization
- [ ] Demo script + rehearsal

---

## 9. Risk Mitigation

### 9.1 Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Reconstruction >5s | High | Progressive refinement, FP16, TensorRT |
| Splat artifacts | Medium | Confidence filtering, soft blending |
| Region segmentation fails | Low | Fallback to single region |
| Memory overflow | Low | Splat pruning, LOD |

### 9.2 Quality Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hallucinations in large moves | High | Move limits, incremental refresh |
| Scale drift in sequences | Medium | Metric-aware warping, base witness anchor |
| Poor inpaint quality | Medium | Normal conditioning, locked regions |

---

## 10. Competitive Differentiation

### 10.1 vs. Martini.ai
**Their Approach:** Witness refresh for continuity  
**Our Advantage:** Metric-aware splats + region primitives + <5s reconstruction

### 10.2 vs. LTX Studio
**Their Approach:** Timeline integration  
**Our Advantage:** Faster reconstruction, compositing-native outputs

### 10.3 vs. ArtCraft AI
**Their Approach:** Craft-like controls  
**Our Advantage:** Forward-compatible data model for procedural editing

---

## 11. Forward Compatibility Hooks

### 11.1 Building Replacement (Future)
```python
def replace_building(scene: Scene, region_id: str, new_building_prompt: str):
    """
    Future API for procedural building replacement
    """
    region = scene.get_region(region_id)
    
    # Generate new building (UTDG/Promptscape)
    new_building = generate_procedural_building(
        prompt=new_building_prompt,
        plane=region.plane_params,
        style=scene.base_witness_metadata.get("style")
    )
    
    # Composite into scene
    scene.replace_region_splats(region_id, new_building.splats)
    
    # Re-render from all cameras
    scene.invalidate_proxy_cache()
```

### 11.2 Trim Sheet Generation (Future)
```python
def extract_trim_sheet(scene: Scene, region_id: str):
    """
    Future API for component extraction
    """
    region = scene.get_region(region_id)
    
    # Extract facade texture + geometry
    facade = extract_facade_from_splats(region.splat_indices, scene.gaussian_splats)
    
    # Decompose to components
    components = decompose_to_trim_sheet(facade)
    
    return TrimSheet(components=components, metadata=region.metadata)
```

---

## 12. Testing Strategy

### 12.1 Unit Tests
- Gaussian regression output shape/range
- Region segmentation coverage
- Witness refresh preserves locked pixels
- Confidence metric bounds

### 12.2 Integration Tests
- End-to-end: image → reconstruction → camera move → generation
- Multi-step sequence drift <10%
- Region export/import roundtrip

### 12.3 Performance Tests
- Reconstruction <5s (90th percentile)
- Rendering 30+ FPS @ 720p
- Memory usage <500 MB per scene

---

## 13. Documentation Requirements

### 13.1 API Documentation
- Scene container schema
- Camera rig controls
- Region data format
- Export formats

### 13.2 User Documentation
- Camera movement best practices
- Region locking workflow
- Export for compositing (Nuke, After Effects)

### 13.3 Developer Documentation
- SHARP implementation notes
- Gaussian splat rendering pipeline
- Extension points for future features

---

## Appendix: SHARP Implementation Notes

### Reference Architecture
Based on "Sharp Monocular View Synthesis in Less Than a Second" (Apple, Dec 2025)

**Key Components:**
1. **Encoder**: ResNet-50 or EfficientNet backbone
2. **Regression Head**: Direct prediction of Gaussian parameters
3. **Loss Function**: Combination of:
   - Photometric loss (L1 + SSIM)
   - Depth consistency
   - Splat regularization (opacity, scale)

**Training Data:**
- Synthetic: Objaverse, ShapeNet
- Real: ScanNet, Matterport3D
- Metric scale supervision from depth sensors

**Inference Pipeline:**
```
RGB Image (H, W, 3)
      ↓
Encoder (ResNet-50)
      ↓
Feature Maps (H/32, W/32, 2048)
      ↓
Regression Head
      ↓
Gaussian Parameters (N, 15)
  [position(3), color(3), opacity(1), scale(3), rotation(4), confidence(1)]
```

**MVP Simplification:**
- Use pre-trained depth estimator instead of end-to-end training
- Lift depth to 3D, then regress splat parameters
- Target: 80% of SHARP quality at 100% of speed target
