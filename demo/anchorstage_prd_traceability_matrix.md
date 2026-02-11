# AnchorStage PRD Traceability Matrix

## Purpose
Verify that the demo package is directly grounded in the original Scene Authoring MVP PRD and engineering breakdown.

## Status key
- `Covered`: Explicitly represented in script/checklists/cues.
- `Covered with Callout`: Represented and should be verbally called out.
- `Partial`: Mentioned but requires explicit spoken framing or evidence discipline.

---

## PRD section alignment

### 1) Product Vision
- PRD requirement:
  - Real image ingest, navigable proxy, directed camera, controllable extras, anchored compositing-ready frames.
  - "Not text-to-video."
- Coverage:
  - `demo/anchorstage_anime_5min_script.md` (S1, S2, S3, S4, S5; non-negotiable lines)
- Status: `Covered`

### 2) MVP Scope (Included/Excluded)
- PRD requirement:
  - Included and excluded lists are explicit.
- Coverage:
  - `demo/anchorstage_anime_5min_script.md` (PRD guardrails intro block)
- Status: `Covered with Callout`

### 3) System Overview (5 subsystems, shared Scene container)
- PRD requirement:
  - Reconstruction, Camera/Reprojection, Void/Witness Refresh, Extras, Generation/Pass export.
- Coverage:
  - `demo/anchorstage_anime_5min_script.md` (S2-S5 flow)
  - `demo/anchorstage_tech_proof_checklist.md` (P1-P5)
- Status: `Covered`

### 4) Core Concepts (Scene container fields)
- PRD requirement:
  - Scene as canonical unit with base witness, splats, depth, confidence, cameras, extras.
- Coverage:
  - `demo/anchorstage_anime_5min_script.md` (S2 Scene container line)
- Status: `Covered with Callout`

### 5) Reconstruction Engine
- PRD requirement:
  - Monocular depth, back-projection, splat conversion, depth/confidence outputs, target <5s GPU.
- Coverage:
  - `demo/anchorstage_anime_5min_script.md` (S2 lines + intro performance targets)
  - `demo/anchorstage_backup_branches.md` (B1 timeout fallback)
- Status: `Covered`

### 6) Camera System / Frustum of Trust
- PRD requirement:
  - Film-style rig, movement modes, confidence/void metric and color coding.
- Coverage:
  - `demo/anchorstage_anime_5min_script.md` (S3 lines)
  - `demo/anchorstage_anime_run_of_show.md` (C5 pass condition)
  - `demo/anchorstage_tech_proof_checklist.md` (P1)
- Status: `Covered`

### 7) Reprojection Engine
- PRD requirement:
  - Proxy render, proxy depth, void map, base-witness reprojection, lock known pixels.
- Coverage:
  - `demo/anchorstage_anime_5min_script.md` (S5 frame order)
  - `demo/anchorstage_tech_proof_checklist.md` (P2)
- Status: `Covered`

### 8) Generative Void Resolution
- PRD requirement:
  - Fill only void regions, preserve locked pixels, reference base witness to prevent drift.
- Coverage:
  - `demo/anchorstage_anime_5min_script.md` (S5)
  - `demo/anchorstage_tech_proof_checklist.md` (P2, P5)
  - `demo/anchorstage_backup_branches.md` (B5)
- Status: `Covered`

### 9) Extras System (format, placement, occlusion)
- PRD requirement:
  - 2.5D billboards, placement controls, occlusion via proxy depth, not AI-regenerated.
- Coverage:
  - `demo/anchorstage_anime_5min_script.md` (S4)
  - `demo/anchorstage_anime_run_of_show.md` (C6, C7)
  - `demo/anchorstage_tech_proof_checklist.md` (P3)
- Status: `Covered`

### 10) Frame Generation Order
- PRD requirement:
  - Proxy -> void -> reprojection -> extras composite -> lock -> fill -> final.
- Coverage:
  - `demo/anchorstage_anime_5min_script.md` (S5 explicit line)
  - `demo/anchorstage_backup_branches.md` (B5, B6)
- Status: `Covered`

### 11) Output Passes
- PRD requirement:
  - Beauty, depth, void, extras ID, extras depth, proxy, confidence metadata.
- Coverage:
  - `demo/anchorstage_anime_5min_script.md` (S5)
  - `demo/anchorstage_anime_run_of_show.md` (C9)
  - `demo/anchorstage_tech_proof_checklist.md` (P4)
- Status: `Covered`

### 12) Performance Targets
- PRD requirement:
  - <5s reconstruction, real-time 720p proxy, <30s still generation, <3 min 3s move, 30 extras preview.
- Coverage:
  - `demo/anchorstage_anime_5min_script.md` (PRD guardrails intro block)
  - `demo/anchorstage_backup_branches.md` (latency-aware branching)
- Status: `Covered with Callout`

### 13) Roadmap Hooks
- PRD requirement:
  - Region segmentation, facade extraction, replaceable surfaces, trim sheet, macros, continuity.
- Coverage:
  - Not central to 5-minute MVP demo by design.
- Status: `Partial`
- Handling:
  - If asked, use close statement: "Current MVP proves camera/extras control; roadmap expands to editable world operations on same Scene container."

### 14) Strategic Positioning
- PRD requirement:
  - Controlled camera + extras + compositing-native workflow + anchored continuity foundation.
- Coverage:
  - `demo/anchorstage_anime_5min_script.md` (S1, S6)
  - `demo/anchorstage_pilot_close.md` (goal/scope/decision request)
- Status: `Covered`

---

## Engineering breakdown alignment

### A) Reconstruction math (depth to 3D)
- Coverage:
  - Verbally referenced in S2 ("pixel back-projection").
- Status: `Covered with Callout`

### B) Proxy rendering (Gaussian splats)
- Coverage:
  - Verbally referenced in S2; visualized with splat overlay.
- Status: `Covered with Callout`

### C) Void map calculation
- Coverage:
  - Demonstrated in S5 split view and P2 evidence.
- Status: `Covered`

### D) Reprojection
- Coverage:
  - Demonstrated in S5 split view and frame order narration.
- Status: `Covered`

### E) Extras rendering math/ordering
- Coverage:
  - Demonstrated in S4 and ordering in S5.
- Status: `Covered`

### F) Generative fill constraints
- Coverage:
  - Demonstrated in S5 and P2.
- Status: `Covered`

### G) Confidence score formula
- Coverage:
  - S3 verbal formula + P1 checklist.
- Status: `Covered`

### H) Sequence handling and drift prevention
- Coverage:
  - P5 base witness anchoring.
- Status: `Covered`

### I) Service data flow by Scene ID
- Coverage:
  - `demo/anchorstage_anime_5min_script.md` (S5 explicit Scene ID orchestration line).
- Status: `Covered with Callout`

---

## Final verdict
The current demo package stands up against the PRD for MVP positioning and technical defensibility, with two deliberate verbal callouts required during delivery:
1. Roadmap hooks are intentionally out of the 5-minute flow.
2. Service orchestration by Scene ID should be spoken explicitly once in S5.
