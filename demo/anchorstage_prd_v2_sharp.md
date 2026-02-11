# Wild Construct Camera Tool (MVP) - Enhanced PRD v2.0

## 1. Working Name
**Wild Construct – Camera Rig (MVP)**  
Internal codename: **WitnessCam**

---

## 2. Objective
Deliver a camera system that enables users to:
- Navigate inside a **Gaussian Splat-based proxy scene** derived from a single image (later video)
- Generate photorealistic new perspectives with **metric scale and parallax**
- Produce a **"refreshed witness image"** from any camera pose, anchored to the original for continuity
- Output **compositing-ready passes** for professional workflows

This tool must feel:
- **Cinematic** (lens presets, film grammar controls)
- **Controllable** (anchored generation, not unbounded hallucination)
- **Extensible** (hooks for future scene editing like region-based swaps)

---

## 3. Success Criteria
The MVP is successful if:
- Users can shift the camera **5–30° off-axis** and generate a plausible, metric-scaled new view without severe artifacts
- Incremental moves (e.g., dolly) maintain consistency via witness refresh, with **<10% drift** in key regions
- System outputs: proxy render, refreshed witness, final frame, **depth/normal/mask passes**
- Camera poses are **savable/reusable** across sessions
- Proxy reconstruction from a single image completes in **<5 seconds** on standard GPU hardware

---

## 4. Non-Goals (MVP Scope Limits)
- No dynamic elements (e.g., moving objects in video)
- No full-scene relighting or physics simulation
- No multi-view NeRF/3DGS training loops
- No procedural building generation/swaps (but **data model supports future hooks**)
- No collaborative multi-user editing

---

## 5. System Overview
The Camera Tool comprises **4 layers**:
1. **Scene Reconstruction** (monocular image → Gaussian Splat proxy)
2. **Camera Rig Model**
3. **Witness Refresh Pipeline**
4. **Generation Bridge**

---

## 6. Core Concepts

### 6.1 Witness Philosophy
Three image states:
- **Base Witness**: Original uploaded image
- **Proxy Witness**: Real-time render of Gaussian Splat scene from current pose
- **Refreshed Witness**: Warped + inpainted image blending base and proxy, with disocclusion handling

Final frame generates from **refreshed witness**, ensuring anchored continuity.

### 6.2 Gaussian Splat Proxy
Use **fast monocular splatting** (inspired by Apple's SHARP: regresses ~1M Gaussians from single image in <1 second, with metric scale). This provides efficient, renderable 3D representation for parallax and novel views.

**Key advantages over depth projection:**
- **Metric scale awareness** (absolute depth, not relative)
- **25–34% better LPIPS** vs. prior monocular methods
- **Real-time rendering** at 720p+
- **Reduced perspective drift** in novel views

---

## 7. Feature Requirements

### 7.1 Scene Reconstruction
**Inputs**: Single photo (optional: EXIF metadata for initial scale)

**Process**:
1. Estimate monocular depth/normals/confidence (via lightweight network)
2. **Regress Gaussian parameters** (position, color, opacity, scale, rotation) directly, yielding ~1M splats
3. **Cluster into lightweight "regions"** (e.g., auto-segmented buildings/sky) for future editing hooks

**Outputs**: Splattable scene proxy with **metric coordinates**

**Technical Implementation**:
- Use SHARP-inspired architecture: direct Gaussian regression from single RGB image
- Output format: positions (Nx3), colors (Nx3), opacities (N), scales (Nx3), rotations (Nx4 quaternions)
- Region segmentation: SAM-based or simple depth clustering for MVP
- Target: **<5s reconstruction** on RTX 3080-class GPU

### 7.2 Camera Rig Model
Film-like camera with:
- **Position** (x, y, z; metric units)
- **Rotation** (yaw, pitch, roll)
- **Focal length** (mm; presets: 24, 35, 50, 85, 135)
- **Sensor/filmback** (e.g., full-frame, crop)
- **Aspect ratio** (e.g., 16:9, 2.39:1)
- **Near/far clipping**

**Controls**:
- Orbit, dolly, truck, pedestal
- Push/pull focus (visual preview)
- Optional spline for small moves (MVP+)

### 7.3 Proxy Render Output
For any pose:
- `proxy_color.png` (real-time splat render)
- `proxy_depth.exr` (metric depth)
- `proxy_normal.exr` (surface normals)
- `disocclusion_mask.png` (holes from novel views)
- `region_masks.png` (per-segmented area, **future building swap hook**)

### 7.4 Witness Refresh Pipeline
**Inputs**: Base witness, proxy outputs

**Process**:
1. Warp base toward target pose using proxy depth
2. Inpaint disoccluded regions conditioned on proxy color/normals
3. Blend edges softly; preserve **"locked" regions** (e.g., user-brushed or auto-detected planes)

**Output**: `witness_refreshed.png`

**Key Innovation**: Metric-aware warping reduces scale ambiguities, improving multi-step consistency.

### 7.5 Generation Bridge
Feeds refreshed witness to gen model (e.g., via API router).

**Conditioning**:
- Refreshed witness
- Depth/normal maps
- Camera metadata
- Optional style/prompt

**Output**: `frame_generated.png` (plus passes)

---

## 8. Camera Movement Modes

### 8.1 Static Reframe
Small shifts (5–15° yaw, focal tweaks) for recomposition.

### 8.2 Push/Dolly
Forward Z-move; incremental witness refreshes maintain scale.

### 8.3 Parallax Pan
Lateral shift to reveal depth; metric splats ensure correct parallax.

### 8.4 Locked Frame
Preserve horizons/verticals or specific regions (e.g., building facades for future replacement).

---

## 9. UI/UX Flow

**Step 1**: Upload Image → Auto-reconstruct proxy (shows progress, **<5s target**)

**Step 2**: Camera Mode → Real-time viewer with gizmos, lens sliders

**Step 3**: Generate → Render proxy → Refresh witness → Generate frame; side-by-side preview

**Step 4**: Export/Timeline → Add pose to keyframe; basic sequence render; **include region data**

---

## 10. Data Model

### Camera Object
```json
{
  "id": "cam_001",
  "position": [x, y, z],
  "rotation": [yaw, pitch, roll],
  "focal_length": 50,
  "filmback": "full_frame",
  "aspect_ratio": "16:9",
  "spline": null
}
```

### Scene Object
```json
{
  "id": "scene_001",
  "base_witness": "path/to/original.png",
  "gaussian_splats": {
    "positions": "Nx3 array",
    "colors": "Nx3 array",
    "opacities": "N array",
    "scales": "Nx3 array",
    "rotations": "Nx4 array"
  },
  "regions": [
    {
      "id": "region_001",
      "mask": "path/to/mask.png",
      "plane_params": [a, b, c, d],
      "semantic_label": "building_facade"
    }
  ],
  "cameras": ["cam_001", "cam_002"]
}
```

**Forward-Compatibility Note**: `regions[]` array enables future building replacement without MVP bloat.

---

## 11. Output Requirements

### Still
- Beauty render
- Depth map (metric EXR)
- Normal map
- Disocclusion/region masks
- Proxy render

### Sequence
- Frame/depth sequences
- Camera JSON
- **Region data** (for future procedural editing)

---

## 12. Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| Reconstruction | **<5s** | SHARP-inspired regression |
| Preview | Real-time @ 720p | Gaussian splat rendering |
| Still generation | <30s | Single frame |
| Short move (3s) | <3min | Incremental witness refresh |

---

## 13. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Hallucinations in large moves | Move limits, incremental steps, witness anchoring |
| Scale ambiguities | **SHARP's metric regression** |
| Artifacting in splats | Soft blending, confidence-based filtering |
| Slow reconstruction | GPU optimization, progressive refinement |

---

## 14. Roadmap Hooks

### Phase 2: Video Input
- Accumulate splats from keyframes
- Temporal consistency via witness refresh

### Phase 3: Scene Editing
- Use **regions** for facade extraction/swaps
- Integrate UTDG for procedural buildings
- **Trim Sheets**: Generate from regions → component breakdown → modular assembly

### Phase 4: Multi-Image Refinement
- Refine splats with additional anchors
- Cross-view consistency

---

## 15. Strategic Positioning

This tool pioneers **camera-directed generative scenes from reality captures**, using **fast monocular splatting** for instant proxies. It's the foundation for editing worlds (e.g., swap buildings via regions), evolving from:

**"Direct inside captured reality"** → **"Rebuild with procedural flexibility"**

### Competitive Differentiation

| Competitor | Their Approach | Our Advantage |
|------------|----------------|---------------|
| Martini.ai | Witness refresh for continuity | **Metric-aware splats** + region primitives |
| LTX Studio | Timeline integration | **Faster reconstruction** (<5s vs. minutes) |
| ArtCraft AI | Craft-like controls | **Compositing-native** + forward-compatible data model |

### Key Innovation
**SHARP-inspired monocular splatting** enables:
- Sub-5-second reconstruction (vs. 30s+ for traditional methods)
- Metric scale for consistent camera moves
- Region-based primitives for future procedural editing
- 25–34% better visual quality (LPIPS) vs. depth-projection approaches

---

## 16. Technical References

### SHARP (Apple, December 2025)
- **Paper**: "Sharp Monocular View Synthesis in Less Than a Second"
- **Key Contribution**: Direct Gaussian regression from single RGB image
- **Performance**: ~1M Gaussians in <1s on consumer GPU
- **Quality**: 25–34% LPIPS improvement over prior monocular methods
- **Scale**: Metric-aware depth prediction

### Implementation Notes
- Use SHARP architecture as reference, not direct dependency (proprietary)
- Implement similar regression head: RGB → Gaussian parameters
- Leverage existing depth estimators (e.g., MiDaS, ZoeDepth) for metric initialization
- Optimize for <5s total pipeline (depth + regression + clustering)

---

## 17. Success Metrics (Post-MVP)

### User Validation
- Can users generate 5+ believable novel views from single image?
- Do camera moves feel "cinematic" vs. "3D viewer"?
- Are outputs usable in professional compositing tools?

### Technical Validation
- Reconstruction time <5s (90th percentile)
- Witness drift <10% over 3-step sequence
- Region segmentation accuracy >80% for buildings/sky

### Business Validation
- Does this enable the "building replacement" narrative?
- Can we demo: capture → navigate → swap facade → export?

---

## Appendix A: Witness Philosophy Deep Dive

### Why Three Image States?

1. **Base Witness** = Ground truth anchor
   - Prevents cumulative drift
   - Reference for locked regions
   
2. **Proxy Witness** = Geometric guide
   - Shows what's visible from new pose
   - Identifies disocclusions
   
3. **Refreshed Witness** = Hybrid input
   - Combines base fidelity + proxy geometry
   - Conditions generation for consistency

### Flow Diagram
```
Base Witness + Proxy Depth → Warp → Disocclusion Mask
                                ↓
                          Inpaint (locked regions preserved)
                                ↓
                          Refreshed Witness → Generation
```

---

## Appendix B: Region Primitives for Future Editing

### MVP Implementation
- Auto-segment via depth clustering or SAM
- Store as binary masks + optional plane parameters
- Export with frame outputs

### Future Use Cases
1. **Facade Replacement**: Select region → generate new building → composite
2. **Trim Sheet Generation**: Extract region → decompose to components → library
3. **Procedural Assembly**: Region as slot for UTDG/Promptscape output
4. **Manual Refinement**: User-drawn masks override auto-segmentation

### Data Structure
```json
{
  "region_id": "facade_001",
  "mask": "binary_mask.png",
  "plane_params": [a, b, c, d],  // Optional: planar surface fit
  "semantic_label": "building_facade",
  "locked": false,  // Can be edited/replaced
  "parent_scene": "scene_001"
}
```

---

## Appendix C: Comparison to Original PRD

### Enhancements in v2.0

| Aspect | Original PRD | Enhanced PRD v2.0 |
|--------|--------------|-------------------|
| Reconstruction | Generic "splat-based" | **SHARP-inspired regression** |
| Speed | Implied fast | **Explicit <5s target** |
| Scale | Relative depth | **Metric-aware** |
| Quality | Unspecified | **25–34% LPIPS improvement** |
| Regions | Future mention | **Structural primitives in data model** |
| Normals | Optional | **Standard output pass** |
| Competitive edge | Implied | **Explicit differentiation table** |

### Why This Matters
- **Engineering**: Clear implementation path with SHARP reference
- **Investors**: Concrete performance claims (speed, quality metrics)
- **Product**: Forward-compatible architecture for building replacement
- **Market**: Defensible technical moat vs. Martini/LTX/ArtCraft

---

## Document History
- **v1.0**: Original Scene Authoring MVP PRD
- **v2.0**: Enhanced with SHARP-based reconstruction, metric scale, region primitives (current)
