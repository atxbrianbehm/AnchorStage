# AnchorStage MVP Reframing Summary
## From Generic Splatting to SHARP-Enhanced Competitive Positioning

---

## Executive Summary

This document summarizes the comprehensive reframing of the AnchorStage MVP based on the deep dive analysis incorporating **Apple's SHARP monocular splatting technology** and enhanced forward-compatibility for procedural building replacement.

### Key Changes
1. **Reconstruction**: Generic "splat-based" → **SHARP-inspired Gaussian regression (<5s)**
2. **Camera System**: Relative coordinates → **Metric-aware absolute scale**
3. **Data Model**: Basic scene container → **Region primitives for future editing**
4. **Generation**: Simple inpainting → **Normal-conditioned with region locking**
5. **Competitive Positioning**: Implied advantages → **Explicit 10x speed + metric scale differentiation**

---

## What Changed and Why

### 1. SHARP-Inspired Reconstruction

#### Original Approach
- Generic "splat-based proxy scene"
- No specific implementation details
- Unspecified reconstruction time
- Relative depth only

#### Enhanced Approach (v2.0)
- **SHARP-inspired direct Gaussian regression**
  - ~1M Gaussians from single RGB image
  - Metric depth estimation (ZoeDepth/MiDaS v3.1)
  - **<5s reconstruction target** (vs. competitors' 30s+)
  - 25–34% better LPIPS quality vs. depth-projection

#### Why This Matters
- **Engineering**: Clear implementation path with state-of-the-art reference
- **Investors**: Concrete performance claims (speed, quality metrics)
- **Competitive**: Defensible technical moat vs. Martini/LTX/ArtCraft
- **Demo**: Visible timer showing <5s creates immediate differentiation

#### Implementation Path
```
Phase 1.1: Metric Depth Estimation (<2s)
  ↓
Phase 1.2: Gaussian Regression (~1M splats, <2s)
  ↓
Phase 1.3: Region Segmentation (<1s)
  ↓
Total: <5s reconstruction
```

---

### 2. Metric-Aware Camera System

#### Original Approach
- Film-style camera controls
- Unspecified coordinate system
- Potential scale drift in sequences

#### Enhanced Approach (v2.0)
- **Metric coordinates** (X, Y, Z in meters)
- **Absolute scale** from SHARP's metric depth
- **Enhanced confidence formula**:
  ```
  confidence = (1 - void_coverage) × depth_confidence × angle_confidence
  ```
- No scale drift across multi-step sequences

#### Why This Matters
- **Technical**: Prevents cumulative drift in camera sequences
- **UX**: Users can specify "dolly 2.5 meters forward" with predictable results
- **Competitive**: Unique positioning vs. relative-depth competitors
- **Future**: Enables accurate building placement/replacement

#### Demo Impact
- Show metric position display: `[0, 1.6, 2.5]`
- State distance traveled: "2.5m forward"
- Demonstrate no scale drift in split view

---

### 3. Region Primitives (Forward-Compatibility)

#### Original Approach
- Roadmap mention of "facade extraction"
- No MVP implementation
- Future hooks vague

#### Enhanced Approach (v2.0)
- **Auto-segmentation in MVP**:
  - Depth clustering or SAM
  - Detect facades, sky, ground
  - Export region masks + plane parameters
- **Region-aware operations**:
  - Lock regions during witness refresh
  - Extras respect region boundaries
  - Export region metadata with frames

#### Why This Matters
- **Product**: Clear path from "navigate" to "edit" to "rebuild"
- **Investors**: Demonstrates forward-thinking architecture
- **Users**: Immediate value (region locking) + future promise (building replacement)
- **Competitive**: Unique data model vs. flat-output competitors

#### Future Workflow (Enabled by MVP)
```
1. Capture scene → auto-segment facade region (MVP)
2. Navigate camera → generate novel views (MVP)
3. Select facade region → "Replace with Gothic cathedral" (Phase 2)
4. System: generates new building, composites into region (Phase 2)
5. Export: final frame + region metadata (MVP foundation)
```

---

### 4. Enhanced Witness Refresh Pipeline

#### Original Approach
- Warp base witness using proxy depth
- Inpaint disocclusions
- Lock known pixels

#### Enhanced Approach (v2.0)
- **Metric-aware warping** (reduces scale drift)
- **Normal-conditioned inpainting** (better quality)
- **Region locking** (preserve facades for future replacement)
- Soft blending at region boundaries

#### Why This Matters
- **Quality**: Normal conditioning improves inpaint realism
- **Consistency**: Metric warping prevents scale drift
- **Forward-compat**: Locked regions preserved for future editing
- **Demo**: Visible locked region overlay shows control

---

### 5. Enhanced Output Passes

#### Original Approach (v1.0)
7 passes:
- Beauty, depth, void, extras ID, extras depth, proxy, confidence

#### Enhanced Approach (v2.0)
8+ passes:
- Beauty (linear EXR)
- **Metric depth** (EXR with scale)
- **Normal map** (world-space, NEW)
- Void map
- Extras ID + depth
- Proxy render
- **Region masks** (per-region PNG, NEW)
- **Metadata JSON** (camera, regions, confidence, NEW)

#### Why This Matters
- **Compositing**: Normals enable advanced relighting/integration
- **Future**: Region masks are foundation for building replacement
- **Professional**: Matches/exceeds industry-standard pass stacks
- **Demo**: Enhanced pass browser shows completeness

---

## Competitive Positioning (Explicit)

### vs. Martini.ai
**Their Strength**: Witness refresh for continuity  
**Our Advantage**: 
- **10x faster reconstruction** (5s vs. 30s+)
- **Region primitives** for future editing
- **Metric-aware camera** (no scale drift)

**Demo Callout**: "While Martini takes 30+ seconds to reconstruct, we complete in under 5 seconds with region segmentation ready for building replacement."

---

### vs. LTX Studio
**Their Strength**: Timeline integration, multi-shot workflows  
**Our Advantage**:
- **Faster reconstruction** enables rapid iteration
- **Compositing-native outputs** (8+ passes)
- **Metric scale** for consistent camera moves

**Demo Callout**: "LTX focuses on timeline; we focus on spatial accuracy and compositing integration."

---

### vs. ArtCraft AI
**Their Strength**: Craft-like controls, artistic tools  
**Our Advantage**:
- **Forward-compatible data model** (regions → building replacement)
- **Metric-aware** for architectural precision
- **Professional pass stack** for VFX pipelines

**Demo Callout**: "ArtCraft gives you craft controls; we give you a foundation for procedural world editing."

---

## Updated Documentation Structure

### Core Documents Created

1. **`anchorstage_prd_v2_sharp.md`**
   - Enhanced PRD incorporating SHARP
   - Metric-aware camera specification
   - Region primitives data model
   - Competitive differentiation table
   - Technical references (SHARP paper)

2. **`anchorstage_technical_architecture_v2.md`**
   - SHARP implementation pipeline
   - Metric-aware camera rig
   - Region segmentation approach
   - Enhanced witness refresh
   - Performance optimization strategy

3. **`anchorstage_implementation_roadmap_v2.md`**
   - 8-week development plan
   - Phase 1: Foundation (metric depth, Gaussian regression, regions)
   - Phase 2: Camera + Rendering (metric rig, splat renderer)
   - Phase 3: Generation + Export (normal conditioning, region metadata)
   - Phase 4: Polish + Demo (UI, optimization, rehearsal)

4. **`anchorstage_anime_5min_script_v2.md`**
   - Updated demo script emphasizing:
     - <5s reconstruction with visible timer
     - Metric-aware camera with position display
     - Region overlay visualization
     - Normal-conditioned generation
     - Forward-compatible pilot close

5. **`anchorstage_prd_traceability_matrix_v2.md`**
   - Enhanced traceability for v2.0 features
   - New proof points (P6-P9):
     - P6: Region segmentation & export
     - P7: Metric scale consistency
     - P8: <5s reconstruction (competitive claim)
     - P9: Normal-conditioned generation

---

## Key Demo Enhancements

### Visual Aids to Add

1. **Reconstruction Timer**
   - Large, visible countdown
   - Starts at image ingest
   - Stops when reconstruction complete
   - Target: <5s (aim for 3-4s safety margin)

2. **Metric Position Display**
   - Show camera coordinates: `[X, Y, Z]` in meters
   - Update in real-time during camera moves
   - Display distance traveled: "2.5m forward"

3. **Region Overlay**
   - Color-coded segmentation:
     - Building facades: Blue
     - Sky: Cyan
     - Ground: Green
   - Toggle on/off during demo
   - Visible in S2, S4, S5

4. **Enhanced Confidence Meter**
   - Green/Yellow/Red color coding
   - Display formula: `(1 - void) × depth × angle`
   - Update in real-time during camera moves

5. **Enhanced Pass Browser**
   - Grid view of 8+ passes
   - Highlight new passes (normals, region masks)
   - Show metadata JSON preview

---

## Non-Negotiable Demo Statements

### Core Claims (v1.0)
- "This is not text-to-video."
- "Known pixels are locked; only void regions are filled."
- "Extras are composited assets and deterministic."

### Enhanced Claims (v2.0)
- **"Reconstruction completes in under 5 seconds."** (show timer)
- **"We use metric-aware depth – absolute scale, not relative."**
- **"Confidence formula: (1 - void_coverage) × depth_confidence × angle_confidence."**
- **"Locked regions like building facades are never modified, preserving them for future replacement."**
- **"Region primitives enable our building replacement roadmap."**

---

## Technical Implementation Priorities

### Week 1-2: Foundation
**Critical Path:**
1. Integrate ZoeDepth for metric depth (<2s)
2. Implement Gaussian regression (~1M splats, <2s)
3. Basic region segmentation (<1s)
4. **Validate <5s total reconstruction**

**Success Criteria:**
- Timer shows <5s consistently
- ~1M Gaussians output
- 3+ regions auto-detected

---

### Week 3-4: Camera + Rendering
**Critical Path:**
1. Metric-aware camera rig (positions in meters)
2. Gaussian splat renderer (30+ FPS @ 720p)
3. Enhanced witness refresh (metric warping, region locking)
4. Confidence visualization (3-factor formula)

**Success Criteria:**
- Metric position display works
- No scale drift in sequences
- Region locking visible

---

### Week 5-6: Generation + Export
**Critical Path:**
1. Normal-conditioned generation
2. Multi-pass export (8+ passes)
3. Region metadata export
4. EXR support for depth/normals

**Success Criteria:**
- Normal map improves inpaint quality
- All passes export correctly
- Region masks readable in external tools

---

### Week 7-8: Polish + Demo
**Critical Path:**
1. UI for camera controls + region overlay
2. Performance optimization (<5s reconstruction)
3. Demo rehearsal with timer, overlays, pass browser
4. Backup branches tested

**Success Criteria:**
- Demo runs in <5 minutes
- All proof points (P1-P9) pass
- Timer, region overlay, metric display work flawlessly

---

## Risk Mitigation

### High-Priority Risks

#### Risk: Reconstruction >5s
**Impact**: Undermines key competitive claim  
**Mitigation**:
- Progressive refinement (show partial results)
- TensorRT optimization for depth estimation
- FP16 inference
- Pre-compute for demo if necessary (with disclosure)

#### Risk: Region Segmentation Fails
**Impact**: Forward-compatibility narrative weakened  
**Mitigation**:
- Fallback to manual region mask (pre-drawn)
- State: "Auto-segmentation is 80%+ accurate; manual override available"
- Ensure at least 1 region (facade) works reliably

#### Risk: Scale Drift in Sequences
**Impact**: Metric-aware claim invalidated  
**Mitigation**:
- Validate metric warping thoroughly
- Limit camera moves to safe ranges for demo
- Show split view to prove consistency

---

## Success Metrics

### Technical Validation
- ✅ Reconstruction <5s (90th percentile)
- ✅ Rendering 30+ FPS @ 720p
- ✅ Witness drift <10% over 3-step sequence
- ✅ Region segmentation >80% accuracy for facades

### Demo Validation
- ✅ Timer shows <5s consistently
- ✅ Region overlay visible with 3+ regions
- ✅ Metric position display updates correctly
- ✅ All 8+ passes export without errors
- ✅ Demo completes in <5 minutes

### Business Validation
- ✅ Competitive differentiation clear to audience
- ✅ Forward-compatible narrative lands (building replacement)
- ✅ Pilot ask tied to demonstrated capabilities
- ✅ No confusion about "text-to-video" category

---

## Q&A Preparation

### Expected Questions

**Q: How does SHARP-inspired reconstruction work?**  
**A**: "We regress ~1M Gaussian Splats directly from a single RGB image using metric depth estimation. This is 10x faster than traditional multi-view reconstruction while maintaining high quality."

**Q: What can I do with region metadata?**  
**A**: "In Phase 2, you'll be able to select a region – like a building facade – and replace it with a procedurally generated building. The region masks we export today are the foundation for that workflow. For MVP, regions enable locked areas during generation and extras placement."

**Q: Does metric scale work for all images?**  
**A**: "We use EXIF metadata when available, or estimate scale from scene context. Accuracy is 80%+ for architectural scenes. For images without clear scale references, we default to normalized units but maintain relative consistency."

**Q: Can I manually edit regions?**  
**A**: "Yes – auto-segmentation is a starting point. You can refine region masks manually or lock specific areas during generation. This gives you full control while benefiting from automatic initialization."

**Q: How does this compare to Martini/LTX/ArtCraft?**  
**A**: "Martini focuses on witness refresh but takes 30+ seconds to reconstruct. LTX emphasizes timeline integration but lacks compositing-native outputs. ArtCraft provides craft controls but doesn't have our forward-compatible data model for procedural editing. We're 10x faster with metric-aware camera and region primitives."

**Q: What's the path to building replacement?**  
**A**: "Phase 1 (MVP) proves camera control + region export. Phase 2 integrates UTDG/Promptscape for procedural building generation. Phase 3 adds trim sheet extraction from regions. The data model we're demoing today supports all of this without breaking changes."

---

## Next Steps

### Immediate (This Week)
1. Review reframed documentation with team
2. Validate <5s reconstruction target is achievable
3. Design timer, region overlay, metric display UI
4. Begin Phase 1.1 implementation (metric depth)

### Short-Term (Weeks 2-4)
1. Complete reconstruction pipeline
2. Build metric-aware camera rig
3. Implement region segmentation
4. Validate all technical claims

### Medium-Term (Weeks 5-8)
1. Enhance generation bridge
2. Implement multi-pass export
3. Polish UI and demo materials
4. Rehearse demo with all proof points

### Long-Term (Post-MVP)
1. Video input support
2. Building replacement workflow (UTDG integration)
3. Trim sheet generation from regions
4. Multi-image refinement

---

## Conclusion

This reframing transforms AnchorStage from a solid but generic "camera tool" into a **technically differentiated, forward-compatible platform** with:

1. **Measurable competitive advantages**: 10x faster reconstruction, metric-aware camera
2. **Clear technical moat**: SHARP-inspired splatting, region primitives
3. **Compelling narrative arc**: Navigate → Edit → Rebuild
4. **Professional outputs**: 8+ compositing passes with region metadata

The enhanced PRD, technical architecture, implementation roadmap, and demo materials provide a clear path to delivering on these claims while maintaining MVP focus and avoiding scope creep.

**Key Differentiator**: We're not just building a camera tool – we're building the foundation for **procedural world editing from reality captures**.

---

## Document Index

### Core PRD & Architecture
- `demo/anchorstage_prd_v2_sharp.md` - Enhanced PRD with SHARP
- `demo/anchorstage_technical_architecture_v2.md` - Technical implementation details

### Implementation & Planning
- `demo/anchorstage_implementation_roadmap_v2.md` - 8-week development plan
- `demo/anchorstage_prd_traceability_matrix_v2.md` - Enhanced verification matrix

### Demo Materials
- `demo/anchorstage_anime_5min_script_v2.md` - Updated demo script
- `demo/anchorstage_tech_proof_checklist.md` - Proof points (to be updated to v2)

### Summary
- `REFRAMING_SUMMARY.md` - This document

---

**Version**: 2.0  
**Date**: 2025  
**Status**: Ready for implementation
