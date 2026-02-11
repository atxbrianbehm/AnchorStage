# AnchorStage PRD Traceability Matrix v2.0
## SHARP-Enhanced MVP Verification

---

## Purpose
Verify that the demo package is directly grounded in the **Enhanced PRD v2.0** (SHARP-based reconstruction, metric-aware camera, region primitives) and engineering breakdown.

---

## Status Key
- `Covered`: Explicitly represented in script/checklists/cues
- `Covered with Callout`: Represented and should be verbally called out
- `Enhanced in v2.0`: New or significantly improved from v1.0
- `Partial`: Mentioned but requires explicit spoken framing or evidence discipline

---

## PRD Section Alignment

### 1) Product Vision (Enhanced)
**PRD Requirement:**
- Real image ingest, **metric-aware** navigable proxy, directed camera, controllable extras, anchored compositing-ready frames
- "Not text-to-video"
- **NEW**: <5s reconstruction, region primitives for future building replacement

**Coverage:**
- `demo/anchorstage_anime_5min_script_v2.md` (S1, S2, S3, S4, S5, S6; non-negotiable lines)
- **Timer display** for <5s reconstruction claim
- **Region overlay** visualization

**Status:** `Enhanced in v2.0`

---

### 2) MVP Scope (Included/Excluded) - Enhanced
**PRD Requirement:**
- Included: **SHARP-inspired reconstruction**, **region segmentation**, **metric-aware camera**
- Excluded: Procedural building generation (but **data model ready**)

**Coverage:**
- `demo/anchorstage_anime_5min_script_v2.md` (PRD guardrails intro block)
- Explicit callout: "Region primitives enable our building replacement roadmap"

**Status:** `Enhanced in v2.0`

---

### 3) System Overview (5 Subsystems + Regions)
**PRD Requirement:**
- Reconstruction (**SHARP-based**), Camera/Reprojection (**metric-aware**), Void/Witness Refresh (**region locking**), Extras, Generation/Pass export (**enhanced**)

**Coverage:**
- `demo/anchorstage_anime_5min_script_v2.md` (S2-S5 flow)
- `demo/anchorstage_tech_proof_checklist_v2.md` (P1-P6, including new P6 for regions)

**Status:** `Enhanced in v2.0`

---

### 4) Core Concepts (Scene Container with Regions)
**PRD Requirement:**
- Scene as canonical unit with base witness, **metric-aware splats**, depth, confidence, cameras, extras, **regions**

**Coverage:**
- `demo/anchorstage_anime_5min_script_v2.md` (S2 Scene container line + region overlay)
- `demo/anchorstage_technical_architecture_v2.md` (Section 3.1)

**Status:** `Enhanced in v2.0`

---

### 5) Reconstruction Engine (SHARP-Inspired)
**PRD Requirement:**
- **Metric depth estimation** (ZoeDepth/MiDaS v3.1)
- **Direct Gaussian regression** (~1M splats)
- **Region segmentation** (depth clustering or SAM)
- Target: **<5s GPU**

**Coverage:**
- `demo/anchorstage_anime_5min_script_v2.md` (S2 lines + **visible timer**)
- `demo/anchorstage_implementation_roadmap_v2.md` (Phase 1.1-1.3)
- `demo/anchorstage_backup_branches_v2.md` (B1 timeout fallback with <5s target)

**Status:** `Enhanced in v2.0`

**Key Evidence:**
- **Timer shows <5s** (competitive claim)
- **~1M Gaussian splats** visible in overlay
- **Region overlay** shows auto-segmentation

---

### 6) Camera System (Metric-Aware)
**PRD Requirement:**
- Film-style rig with **metric coordinates** (X, Y, Z in meters)
- Movement modes with **absolute scale**
- **Enhanced confidence formula**: `(1 - void_coverage) × depth_confidence × angle_confidence`
- Color coding (green/yellow/red)

**Coverage:**
- `demo/anchorstage_anime_5min_script_v2.md` (S3 lines + **metric position display**)
- `demo/anchorstage_anime_run_of_show_v2.md` (C5 pass condition with metric validation)
- `demo/anchorstage_tech_proof_checklist_v2.md` (P1 enhanced)

**Status:** `Enhanced in v2.0`

**Key Evidence:**
- **Metric position display** (e.g., [0, 1.6, 2.5])
- **Distance traveled** shown (e.g., "2.5m forward")
- **Enhanced confidence formula** stated verbatim

---

### 7) Reprojection Engine (Metric-Aware)
**PRD Requirement:**
- Proxy render, **metric proxy depth**, void map, base-witness reprojection, **lock known pixels + regions**

**Coverage:**
- `demo/anchorstage_anime_5min_script_v2.md` (S5 frame order + **region locking**)
- `demo/anchorstage_tech_proof_checklist_v2.md` (P2 enhanced with region locking)

**Status:** `Enhanced in v2.0`

**Key Evidence:**
- **Locked regions highlighted** (e.g., building facade in green)
- **Metric warping** prevents scale drift

---

### 8) Generative Void Resolution (Normal-Conditioned)
**PRD Requirement:**
- Fill only void regions, preserve locked pixels **and locked regions**
- **NEW**: Condition on **surface normals** for better inpaint quality
- Reference base witness to prevent drift

**Coverage:**
- `demo/anchorstage_anime_5min_script_v2.md` (S5 + **normal conditioning callout**)
- `demo/anchorstage_tech_proof_checklist_v2.md` (P2, P5, P6)
- `demo/anchorstage_backup_branches_v2.md` (B5)

**Status:** `Enhanced in v2.0`

**Key Evidence:**
- **Normal map** visible in pass browser
- **Region locking** demonstrated (facades preserved)

---

### 9) Extras System (Region-Aware)
**PRD Requirement:**
- 2.5D billboards, placement controls, occlusion via **metric proxy depth**, not AI-regenerated
- **NEW**: Respect region boundaries (e.g., don't clip through facades)

**Coverage:**
- `demo/anchorstage_anime_5min_script_v2.md` (S4 + **region-aware placement**)
- `demo/anchorstage_anime_run_of_show_v2.md` (C6, C7)
- `demo/anchorstage_tech_proof_checklist_v2.md` (P3 enhanced)

**Status:** `Enhanced in v2.0`

**Key Evidence:**
- **Region overlay** shows extras avoid facade regions
- **Metric depth occlusion** demonstrated

---

### 10) Frame Generation Order (Enhanced)
**PRD Requirement:**
- Proxy → void → reprojection → **region locking** → extras composite → lock → fill → final

**Coverage:**
- `demo/anchorstage_anime_5min_script_v2.md` (S5 explicit line with region locking)
- `demo/anchorstage_backup_branches_v2.md` (B5, B6)

**Status:** `Enhanced in v2.0`

---

### 11) Output Passes (Enhanced)
**PRD Requirement:**
- Beauty, **metric depth**, **normals**, void, extras ID, extras depth, proxy, **region masks**, confidence metadata

**Coverage:**
- `demo/anchorstage_anime_5min_script_v2.md` (S5 + **enhanced pass browser** with 8+ passes)
- `demo/anchorstage_anime_run_of_show_v2.md` (C9)
- `demo/anchorstage_tech_proof_checklist_v2.md` (P4 enhanced)

**Status:** `Enhanced in v2.0`

**Key Evidence:**
- **Normal map pass** (EXR)
- **Region masks** (per-region PNG)
- **Metadata JSON** (camera, regions, confidence)

---

### 12) Performance Targets (SHARP-Enhanced)
**PRD Requirement:**
- **<5s reconstruction** (vs. competitors' 30s+)
- Real-time 720p proxy (30+ FPS)
- <30s still generation
- <3 min 3s move
- 30 extras preview

**Coverage:**
- `demo/anchorstage_anime_5min_script_v2.md` (PRD guardrails intro block + **visible timer**)
- `demo/anchorstage_backup_branches_v2.md` (latency-aware branching)

**Status:** `Enhanced in v2.0`

**Key Evidence:**
- **Timer displays <5s** (critical competitive claim)

---

### 13) Roadmap Hooks (Region-Based)
**PRD Requirement:**
- **Region segmentation** (MVP)
- **Facade extraction** (future)
- **Replaceable surfaces** (future)
- **Trim sheet generation** (future)
- Macros, continuity

**Coverage:**
- `demo/anchorstage_anime_5min_script_v2.md` (S6 forward-compatible pilot close)
- Explicit callout: "Region primitives enable our building replacement roadmap"

**Status:** `Enhanced in v2.0`

**Handling:**
- Region overlay demonstrated in S2, S4, S5
- Pilot close (S6) ties regions to future building replacement
- If asked: "Current MVP proves camera/extras control + region export; Phase 2 enables building replacement on same Scene container"

---

### 14) Strategic Positioning (Competitive Differentiation)
**PRD Requirement:**
- Controlled camera + extras + compositing-native workflow + anchored continuity foundation
- **NEW**: 10x faster reconstruction, metric-aware camera, region primitives

**Coverage:**
- `demo/anchorstage_anime_5min_script_v2.md` (S1 competitive positioning, S6 pilot close)
- `demo/anchorstage_pilot_close_v2.md` (goal/scope/decision request with region roadmap)

**Status:** `Enhanced in v2.0`

**Key Differentiators:**
- vs. Martini: "10x faster reconstruction + region primitives"
- vs. LTX: "Metric-aware camera prevents scale drift"
- vs. ArtCraft: "Forward-compatible for procedural editing"

---

## Engineering Breakdown Alignment

### A) Reconstruction Math (SHARP-Inspired)
**Coverage:**
- Verbally referenced in S2 ("direct Gaussian regression")
- **Timer evidence** for <5s claim

**Status:** `Enhanced in v2.0`

---

### B) Proxy Rendering (Gaussian Splats with Normals)
**Coverage:**
- Verbally referenced in S2; visualized with splat overlay
- **Normal pass** demonstrated in S5

**Status:** `Enhanced in v2.0`

---

### C) Void Map Calculation (Region-Aware)
**Coverage:**
- Demonstrated in S5 split view and P2 evidence
- **Region locking** overlay visible

**Status:** `Enhanced in v2.0`

---

### D) Reprojection (Metric-Aware)
**Coverage:**
- Demonstrated in S5 split view and frame order narration
- **Metric warping** prevents scale drift

**Status:** `Enhanced in v2.0`

---

### E) Extras Rendering (Region-Aware)
**Coverage:**
- Demonstrated in S4 with **region overlay**
- Ordering in S5

**Status:** `Enhanced in v2.0`

---

### F) Generative Fill Constraints (Normal-Conditioned)
**Coverage:**
- Demonstrated in S5 with **normal map conditioning**
- P2 enhanced

**Status:** `Enhanced in v2.0`

---

### G) Confidence Score Formula (Enhanced)
**Coverage:**
- S3 verbal formula: `(1 - void_coverage) × depth_confidence × angle_confidence`
- P1 checklist enhanced

**Status:** `Enhanced in v2.0`

---

### H) Sequence Handling (Metric-Aware Drift Prevention)
**Coverage:**
- P5 base witness anchoring + **metric warping**

**Status:** `Enhanced in v2.0`

---

### I) Service Data Flow by Scene ID (with Regions)
**Coverage:**
- `demo/anchorstage_anime_5min_script_v2.md` (S5 explicit Scene ID orchestration line)
- **Region metadata** included in flow

**Status:** `Enhanced in v2.0`

---

### J) Region Segmentation (NEW)
**Coverage:**
- Demonstrated in S2 (region overlay)
- Used in S4 (extras placement)
- Exported in S5 (region masks)
- P6 checklist item

**Status:** `NEW in v2.0`

---

## New Proof Points (v2.0)

### P6: Region Segmentation & Export
**Claim:**
- Scene auto-segments into replaceable regions (facades, sky, ground)
- Region masks export with metadata for future editing

**Where Shown:**
- Segment S2 (region overlay), S5 (region masks in pass browser)

**Evidence Required:**
- Region overlay visible with 3+ auto-detected regions
- Region masks export as separate PNG files
- Metadata JSON includes region plane parameters

**Pass/Fail:** [ ]

**Notes:**

---

### P7: Metric Scale Consistency
**Claim:**
- Camera positions use metric coordinates (meters)
- Dolly moves maintain absolute scale (no drift)

**Where Shown:**
- Segment S3 (camera movement with metric display)

**Evidence Required:**
- Metric position display visible (e.g., [0, 1.6, 2.5])
- Distance traveled shown (e.g., "2.5m forward")
- Split view shows no scale drift between base and refreshed witness

**Pass/Fail:** [ ]

**Notes:**

---

### P8: <5s Reconstruction (Competitive Claim)
**Claim:**
- Reconstruction completes in <5 seconds on standard GPU
- 10x faster than competitors (30s+)

**Where Shown:**
- Segment S2 (visible timer)

**Evidence Required:**
- Timer starts at image ingest
- Timer stops when reconstruction complete
- Timer shows <5s (target: 3-4s for safety margin)

**Pass/Fail:** [ ]

**Notes:**

---

### P9: Normal-Conditioned Generation
**Claim:**
- Generation uses surface normals for better inpaint quality
- Normal pass exported for compositing

**Where Shown:**
- Segment S5 (pass browser, normal map visible)

**Evidence Required:**
- Normal map visible in pass browser
- Presenter states "normal-conditioned generation"
- Normal pass exports as EXR

**Pass/Fail:** [ ]

**Notes:**

---

## Final Verdict (v2.0)

The enhanced demo package stands up against the **PRD v2.0** for:
1. **Technical superiority**: <5s reconstruction, metric-aware camera, normal conditioning
2. **Competitive differentiation**: 10x faster than Martini/LTX/ArtCraft
3. **Forward-compatibility**: Region primitives enable building replacement roadmap

### Required Verbal Callouts During Delivery
1. **"Reconstruction completes in under 5 seconds"** (show timer)
2. **"We use metric-aware depth – absolute scale, not relative"**
3. **"Region primitives enable our building replacement roadmap"** (S6 pilot close)
4. **Enhanced confidence formula** stated verbatim in S3
5. **Service orchestration by Scene ID** with region metadata (S5)

### Critical Evidence Items
- ✅ Timer shows <5s reconstruction
- ✅ Region overlay visible in S2, S4, S5
- ✅ Metric position display in S3
- ✅ Normal map in S5 pass browser
- ✅ Region masks export correctly

### Acceptance Gates (Enhanced)
1. All P1-P9 marked pass (including new P6-P9)
2. Demo runtime ≤ 05:15 in rehearsal
3. At least one rehearsal executed entirely via fallback branches
4. Either Presenter or Operator can run full demo solo using run-of-show sheet
5. **Timer displays correctly and stops at <5s**
6. **Region overlay color-coded and visible**
7. **Metric position display updates during camera move**

---

## Post-Demo Capture (Enhanced)

### Record Audience Objections
- Link objections to proof IDs (P1-P9)
- Note any confusion about region primitives vs. building replacement
- Track competitive comparison questions (vs. Martini/LTX/ArtCraft)

### Record Fallback Usage
- Which proof required fallback evidence
- Whether <5s timer was live or pre-recorded

### Log Pilot Close Result
- `approved` (immediate pilot commitment)
- `conditional` (pending technical validation)
- `deferred` (need more evidence)

### Capture Forward-Compatible Interest
- Did region primitives resonate?
- Questions about building replacement timeline?
- Interest in trim sheet generation?

---

## Comparison: v1.0 vs. v2.0

| Aspect | v1.0 | v2.0 (Enhanced) |
|--------|------|-----------------|
| Reconstruction | Generic "splat-based" | **SHARP-inspired, <5s with timer** |
| Camera | Film-style rig | **Metric-aware coordinates** |
| Regions | Not mentioned | **Auto-segmented, exported, locked** |
| Confidence | Simple void ratio | **Enhanced 3-factor formula** |
| Passes | 7 outputs | **8+ outputs (added normals, region masks)** |
| Competitive | Implied | **Explicit differentiation table** |
| Forward-compat | Roadmap mention | **Region primitives demonstrated** |
| Proof points | P1-P5 | **P1-P9 (added 4 new proofs)** |

---

## v2.0 Enhancements Summary

### Technical Enhancements
1. **SHARP-inspired reconstruction** (<5s target, ~1M splats)
2. **Metric-aware camera** (absolute scale, no drift)
3. **Region segmentation** (auto-detected facades, sky, ground)
4. **Normal-conditioned generation** (better inpaint quality)
5. **Enhanced confidence formula** (3-factor metric)

### Demo Enhancements
1. **Visible timer** for <5s reconstruction claim
2. **Region overlay** visualization (color-coded)
3. **Metric position display** during camera moves
4. **Enhanced pass browser** (8+ passes including normals, region masks)
5. **Forward-compatible pilot close** (region → building replacement narrative)

### Competitive Enhancements
1. **Explicit differentiation** vs. Martini/LTX/ArtCraft
2. **10x faster reconstruction** claim with evidence
3. **Metric-aware** positioning (unique in market)
4. **Region primitives** as forward-compatible moat

---

## Rehearsal Checklist (v2.0)

- [ ] Timer displays correctly and stops at <5s
- [ ] Region overlay color-coded (facades: blue, sky: cyan, ground: green)
- [ ] Metric position display updates during camera move
- [ ] Confidence meter shows enhanced formula
- [ ] Normal map visible in pass browser
- [ ] Region masks export as separate files
- [ ] Metadata JSON includes region plane parameters
- [ ] All non-negotiable statements memorized (v1.0 + v2.0)
- [ ] Competitive differentiation table memorized
- [ ] Backup branches tested (B1-B5 updated for v2.0)
- [ ] Q&A responses practiced (SHARP, regions, metric scale)
- [ ] Pilot summary card v2 includes region roadmap graphic
