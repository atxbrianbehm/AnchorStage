# AnchorStage Anime Studio Demo Script v2.0 (5-Min Live Walkthrough)
## SHARP-Enhanced MVP Demo

---

## Demo Intent
Prove AnchorStage is a **metric-aware, camera-directed spatial reconstruction system** with:
- **<5s reconstruction** (SHARP-inspired Gaussian Splatting)
- **Region primitives** for future building replacement
- **Deterministic extras** with depth occlusion
- **Compositing-ready outputs** with enhanced passes

---

## PRD Guardrails to State During Intro

### Included in MVP
- Single image ingest with **metric-aware depth estimation**
- **SHARP-inspired Gaussian Splat reconstruction** (<5s target)
- **Region segmentation** (auto-detected facades, sky, ground)
- Camera rig with **metric coordinates** (no scale drift)
- Void-based witness refresh with **region locking**
- Billboard extras with occlusion
- **Enhanced pass export** (beauty, depth, normals, region masks)

### Explicitly Out of Scope
- True 3D character animation
- Video ingest (Phase 2)
- **Procedural building generation** (data model ready, execution future)
- Relighting or physics simulation
- Multi-user collaboration

### Performance Targets to Reference
- **Reconstruction: <5 seconds** (vs. competitors' 30s+)
- Real-time 720p proxy preview (30+ FPS)
- Still generation: <30 seconds
- 3-second camera move: <3 minutes
- 30 extras in real-time preview

### Competitive Positioning
- **vs. Martini.ai**: Faster reconstruction + region primitives
- **vs. LTX Studio**: Metric-aware camera + compositing-native
- **vs. ArtCraft AI**: Forward-compatible for procedural editing

---

## Segment Format
Each segment follows:
- `segment_id`
- `time_start` / `time_end`
- `intent`
- `presenter_lines`
- `operator_actions`
- `expected_visual`
- `proof_point`
- `risk_if_fail`
- `fallback_path`

---

## S1: Problem Frame (00:00 - 00:30)

### Intent
Frame category and competitive differentiation before showing product.

### Presenter Lines
- "This is not text-to-video. We start from a **real image** and give you directable camera movement with **metric-aware spatial continuity**."
- "Today we'll ingest one still, reconstruct in **under 5 seconds**, move camera with trust boundaries, place extras, and export **compositing passes with region metadata**."
- "Our reconstruction is **10x faster** than traditional methods, using SHARP-inspired Gaussian Splatting."

### Operator Actions
- Open AnchorStage scene authoring workspace at empty project state
- Show title overlay: "AnchorStage: Metric-Aware Camera-Directed Reconstruction"
- Display comparison slide: "5s reconstruction vs. competitors' 30s+"

### Expected Visual
- Clean workspace, one input slot, no generated outputs yet
- Comparison slide visible (optional)

### Proof Point
- Category positioning + competitive differentiation explicit before any output shown

### Risk if Fail
- Audience misclassifies tool as generic generation

### Fallback Path
- Use backup opening slide with same lines and continue to S2

---

## S2: Ingest + SHARP Reconstruction (00:30 - 01:30)

### Intent
Show single-image ingest and **fast metric-aware reconstruction** into navigable proxy with regions.

### Presenter Lines
- "We ingest a single production still and reconstruct a **metric-aware spatial proxy in under 5 seconds**."
- "Under the hood: **metric depth estimation**, direct **Gaussian Splat regression** (~1M splats), and **automatic region segmentation**."
- "This gives you a controllable Scene container with **absolute scale** and **replaceable regions**, not just a flat image."
- **[SHOW TIMER]**: "Watch the reconstruction complete in real-time."

### Operator Actions
- Drag one anime background still into ingest
- **Start visible timer** (target: <5s)
- Trigger reconstruction
- Toggle overlays in order:
  1. Metric depth map (with scale bar showing meters)
  2. Confidence map
  3. Gaussian splat view (~1M splats)
  4. **Region overlay** (facades, sky, ground color-coded)
- **Stop timer** when reconstruction completes

### Expected Visual
- Completed scene with:
  - Proxy depth (metric scale visible)
  - Visible splat cloud (~1M Gaussians)
  - **Region overlay** showing auto-segmented areas
- **Timer shows <5s** (key competitive claim)

### Proof Point
- Single image becomes navigable proxy with **metric scale**, depth/confidence, and **region primitives** in <5s

### Risk if Fail
- Reconstruction delay >5s or incomplete depth

### Fallback Path
- Load precomputed `scene_id: demo_anime_street_01_prebuilt_v2` with regions and show same overlays
- State: "Pre-built for demo stability, but live reconstruction targets <5s"

---

## S3: Metric-Aware Camera Direction (01:30 - 02:30)

### Intent
Demonstrate intentional camera control with **metric coordinates** and explicit reliability boundary.

### Presenter Lines
- "Now we direct camera like a film rig: reframe, dolly, parallax pan, and lens changes."
- "Because we have **metric scale**, camera moves maintain **absolute depth** – no scale drift across sequences."
- "As we move, AnchorStage calculates how much frame area is known versus void."
- "**Confidence formula**: `(1 - void_coverage) × depth_confidence × angle_confidence`. Green is safe, yellow is moderate fill, red is heavy hallucination."

### Operator Actions
- Set initial camera A (show position in **meters**: e.g., [0, 1.6, 0])
- Execute controlled dolly move to camera B (e.g., [0, 1.6, 2.5])
  - Show **metric distance traveled** (e.g., "2.5m forward")
- Live confidence meter visible during move
- Pause at one yellow threshold frame to discuss tradeoff
- Show **no scale drift** by comparing base witness and refreshed witness

### Expected Visual
- Smooth camera move with:
  - Confidence color transition (green → yellow)
  - **Metric position display** (X, Y, Z in meters)
  - Parallax effect from Gaussian splats
- Split view: base witness vs. refreshed witness (aligned scale)

### Proof Point
- Guardrailed motion via **enhanced confidence metric** + **metric-aware consistency**

### Risk if Fail
- Stutter or unstable pose interpolation

### Fallback Path
- Play prevalidated camera path clip with live metric overlay and continue

---

## S4: Extras + Region-Aware Occlusion (02:30 - 03:20)

### Intent
Show extras as deterministic composited layer with depth occlusion, **respecting region boundaries**.

### Presenter Lines
- "Extras are 2.5D billboard agents placed in scene space, not regenerated each frame."
- "We can control density, motion mix, and style while preserving deterministic behavior."
- "Occlusion uses **metric proxy depth**, so extras pass behind geometry correctly."
- **[NEW]**: "Extras respect **region boundaries** – for example, they won't clip through auto-detected building facades."

### Operator Actions
- Open extras panel
- Set preset: `anime_commuter_light`, density `28`, motion mix `walk:70 idle:30`
- Place extras with ground-plane distribution
- **Toggle region overlay** to show extras avoid facade regions
- Scrub across two camera poses to show:
  - Occlusion stability
  - Region-aware placement

### Expected Visual
- Crowd sprites appear:
  - Grounded and correctly occluded behind foreground structures
  - **Respecting region boundaries** (visible in overlay)
- Smooth occlusion as camera moves

### Proof Point
- Extras are directable, deterministic, with **metric depth-tested occlusion** and **region awareness**

### Risk if Fail
- Misplacement or occlusion artifact

### Fallback Path
- Load saved extras layout `layout_id: commuters_v2_regions` and replay scrub

---

## S5: Enhanced Generation + Multi-Pass Export (03:20 - 04:30)

### Intent
Prove fill pipeline is constrained, **normal-conditioned**, and outputs include **region metadata** for future editing.

### Presenter Lines
- "Frame order is fixed: proxy render, void map, reprojection, **region locking**, extras composite, then masked generation."
- "Known pixels are locked. **Locked regions** (like building facades) are **never modified** – preserving them for future replacement."
- **[NEW]**: "Generation is conditioned on **surface normals** for better inpaint quality."
- "Reconstruction, proxy rendering, reprojection, extras, and generation are orchestrated per Scene ID."
- **[NEW]**: "Every frame exports: beauty, **metric depth**, **normals**, void map, extras passes, proxy render, **region masks**, and confidence metadata."

### Operator Actions
- Show split view: `witness_reprojected`, `void_map`, `witness_refreshed`
- Enable lock overlay for non-void pixels
- **Highlight locked regions** (e.g., building facade in green)
- Open **enhanced pass browser** and cycle through:
  1. Beauty render
  2. **Metric depth** (EXR with scale)
  3. **Normal map** (world-space)
  4. Void map (inpainted regions)
  5. Extras ID + depth
  6. Proxy render
  7. **Region masks** (per-region PNG)
  8. **Metadata JSON** (camera, regions, confidence)

### Expected Visual
- Clear masked-fill behavior with **region locking** visible
- Complete **enhanced pass stack** with region metadata
- **Normal map** conditioning visible in inpaint quality

### Proof Point
- Constrained generation with **region preservation** and **compositing-ready outputs with region metadata**

### Risk if Fail
- Bridge latency or pass display error

### Fallback Path
- Open pre-rendered frame package v2 and annotate each pass in same sequence

---

## S6: Forward-Compatible Pilot Close (04:30 - 05:00)

### Intent
Convert demo momentum into pilot commitment, **emphasizing future building replacement**.

### Presenter Lines
- "What you saw is **metric-aware camera movement** plus controlled extras from a single still, with **compositing-native outputs**."
- **[NEW]**: "The **region primitives** you saw are the foundation for our **building replacement roadmap** – select a facade, generate a new building, composite it back in."
- "We propose a scoped pilot on your art direction: one location family, three shot types, two review cycles, two-week timeline."
- "If this meets your bar, we align today on pilot kickoff owners and target start date."

### Operator Actions
- Display **enhanced pilot summary card** with:
  - Scope: metric-aware reconstruction + region export
  - Timeline: 2 weeks
  - Success criteria: <5s reconstruction, region metadata export
  - **Future hook**: Building replacement workflow (Phase 2)
- Leave final frame and **region overlay** on screen during ask

### Expected Visual
- Clear pilot ask tied to demonstrated capabilities
- **Region overlay** visible as "future-ready" feature

### Proof Point
- Meeting closes with concrete commitment request + **forward-compatible narrative**

### Risk if Fail
- Close becomes vague or deferred

### Fallback Path
- Use one-page pilot template v2 with region roadmap and ask for named technical and creative approvers

---

## Hard Timing Guardrails
- Segment hard stop times must be enforced to finish by 05:00
- If any segment exceeds by 10+ seconds, switch to that segment's fallback immediately

---

## Non-Negotiable Statements to Include Verbatim

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

## Key Competitive Differentiators to Emphasize

| Competitor | Their Approach | Our Advantage (State in Demo) |
|------------|----------------|-------------------------------|
| Martini.ai | Witness refresh | "**10x faster reconstruction** + region primitives" |
| LTX Studio | Timeline integration | "**Metric-aware camera** prevents scale drift" |
| ArtCraft AI | Craft controls | "**Forward-compatible** for procedural editing" |

---

## Visual Aids to Prepare

1. **Reconstruction Timer**: Large, visible countdown (target: <5s)
2. **Metric Scale Overlay**: Show camera position in meters
3. **Region Color Coding**:
   - Building facades: Blue
   - Sky: Cyan
   - Ground: Green
4. **Confidence Meter**: Green/Yellow/Red with formula displayed
5. **Enhanced Pass Browser**: Grid view of all 8+ passes
6. **Pilot Summary Card v2**: Include region roadmap graphic

---

## Backup Branches (Updated for v2.0)

### B1: Reconstruction Timeout
- If reconstruction >5s, load `demo_anime_street_01_prebuilt_v2`
- State: "Pre-built for demo stability, but live reconstruction targets <5s"

### B2: Camera Stutter
- Play prevalidated camera path clip with metric overlay

### B3: Extras Misplacement
- Load saved extras layout `layout_id: commuters_v2_regions`

### B4: Pass Display Error
- Open pre-rendered frame package v2 with all passes

### B5: Region Segmentation Failure
- Fallback to manual region mask (pre-drawn facade)
- State: "Auto-segmentation is 80%+ accurate; manual override available"

---

## Post-Demo Q&A Prep

### Expected Questions

**Q: How does SHARP-inspired reconstruction work?**
A: "We regress ~1M Gaussian Splats directly from a single RGB image using metric depth estimation. This is 10x faster than traditional multi-view reconstruction."

**Q: What can I do with region metadata?**
A: "In Phase 2, you'll be able to select a region – like a building facade – and replace it with a procedurally generated building. The region masks we export today are the foundation for that workflow."

**Q: Does metric scale work for all images?**
A: "We use EXIF metadata when available, or estimate scale from scene context. Accuracy is 80%+ for architectural scenes."

**Q: Can I manually edit regions?**
A: "Yes – auto-segmentation is a starting point. You can refine region masks manually or lock specific areas during generation."

---

## Success Criteria for Demo

### Technical Validation
- ✅ Reconstruction completes in <5s (timer visible)
- ✅ Region overlay shows 3+ auto-detected regions
- ✅ Camera move maintains metric scale (no drift)
- ✅ Locked regions preserved during generation
- ✅ All 8+ passes export correctly

### Narrative Validation
- ✅ Competitive differentiation clear (vs. Martini/LTX/ArtCraft)
- ✅ Forward-compatible story lands (building replacement)
- ✅ Pilot ask tied to demonstrated capabilities

### Audience Engagement
- ✅ No confusion about "text-to-video" category
- ✅ Region primitives understood as future hook
- ✅ Metric scale advantage clear

---

## Rehearsal Checklist

- [ ] Timer displays correctly and stops at <5s
- [ ] Region overlay color-coded and visible
- [ ] Metric position display updates during camera move
- [ ] Confidence meter formula matches PRD
- [ ] All 8+ passes load in browser
- [ ] Pilot summary card v2 includes region roadmap
- [ ] Backup branches tested (B1-B5)
- [ ] Non-negotiable statements memorized
- [ ] Q&A responses practiced
