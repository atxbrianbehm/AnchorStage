# AnchorStage Anime Studio Demo Script (5-Min Live Walkthrough)

## Demo intent
Prove AnchorStage is a camera-directed spatial reconstruction system with deterministic extras and compositing-ready outputs.

## PRD guardrails to state during intro
- Included in MVP: single image ingest, monocular depth to splat proxy, camera rig and movement, void-based refresh, billboard extras with occlusion, compositing pass export.
- Explicitly out of scope for this demo: true 3D character animation, video ingest, procedural building swaps, relighting, multi-user collaboration.
- Performance targets to reference: reconstruction under 5 seconds, real-time 720p proxy preview, still generation under 30 seconds, 3-second move under 3 minutes, 30 extras in real-time preview.

## Segment format
Each segment follows:
- `segment_id`
- `time_start`
- `time_end`
- `intent`
- `presenter_lines`
- `operator_actions`
- `expected_visual`
- `proof_point`
- `risk_if_fail`
- `fallback_path`

---

### segment_id: S1_problem_frame
- `time_start`: 00:00
- `time_end`: 00:30
- `intent`: Frame category and stakes before showing product.
- `presenter_lines`:
  - "This is not text-to-video. We start from a real image and give you directable camera movement with spatial continuity."
  - "Today we’ll ingest one still, move camera with trust boundaries, place extras, and export compositing passes."
- `operator_actions`:
  - Open AnchorStage scene authoring workspace at empty project state.
  - Show title overlay: "AnchorStage: Camera-Directed Spatial Reconstruction."
- `expected_visual`:
  - Clean workspace, one input slot, no generated outputs yet.
- `proof_point`:
  - Category positioning is explicit before any output is shown.
- `risk_if_fail`:
  - Audience misclassifies tool as generic generation.
- `fallback_path`:
  - Use backup opening slide with same two lines and continue to S2.

### segment_id: S2_ingest_reconstruct
- `time_start`: 00:30
- `time_end`: 01:20
- `intent`: Show single-image ingest and reconstruction into navigable proxy.
- `presenter_lines`:
  - "We ingest a single production still and reconstruct a spatial proxy in seconds."
  - "Under the hood: monocular depth, pixel back-projection, and Gaussian splat conversion."
  - "What matters for your team is that this gives a controllable Scene container, not just a flat image."
- `operator_actions`:
  - Drag one anime background still into ingest.
  - Trigger reconstruction.
  - Toggle overlays in order: depth map, confidence map, splat view.
- `expected_visual`:
  - Completed scene with proxy depth and visible splat cloud.
- `proof_point`:
  - Single image becomes navigable proxy with depth/confidence artifacts.
- `risk_if_fail`:
  - Reconstruction delay or incomplete depth.
- `fallback_path`:
  - Load precomputed `scene_id: demo_anime_street_01_prebuilt` and show same overlays.

### segment_id: S3_camera_direction
- `time_start`: 01:20
- `time_end`: 02:20
- `intent`: Demonstrate intentional camera control with explicit reliability boundary.
- `presenter_lines`:
  - "Now we direct camera like a film rig: reframe, subtle dolly, parallax pan, and subtle lens changes."
  - "As we move, AnchorStage calculates how much frame area is known versus void."
  - "Confidence is computed as 1 minus void-pixel ratio. Green is safe, yellow is moderate fill, red is heavy hallucination."
- `operator_actions`:
  - Set initial camera A.
  - Execute controlled move to camera B with live confidence meter visible.
  - Pause at one yellow threshold frame to discuss tradeoff.
- `expected_visual`:
  - Smooth camera move with confidence color transition.
- `proof_point`:
  - Guardrailed motion via trust metric, not hidden heuristics.
- `risk_if_fail`:
  - Stutter or unstable pose interpolation.
- `fallback_path`:
  - Play prevalidated camera path clip with live metric overlay and continue.

### segment_id: S4_extras_deterministic
- `time_start`: 02:20
- `time_end`: 03:20
- `intent`: Show extras as deterministic composited layer with depth occlusion.
- `presenter_lines`:
  - "Extras are 2.5D billboard agents placed in scene space, not regenerated each frame."
  - "We can control density, motion mix, and style while preserving deterministic behavior."
  - "Occlusion uses proxy depth, so extras pass behind geometry correctly."
- `operator_actions`:
  - Open extras panel.
  - Set preset: `anime_commuter_light`, density `28`, motion mix `walk:70 idle:30`.
  - Place extras with ground-plane distribution.
  - Scrub across two camera poses to show occlusion stability.
- `expected_visual`:
  - Crowd sprites appear grounded and correctly occluded behind foreground structures.
- `proof_point`:
  - Extras are directable and deterministic with depth-tested occlusion.
- `risk_if_fail`:
  - Misplacement or occlusion artifact.
- `fallback_path`:
  - Load saved extras layout `layout_id: commuters_v1` and replay scrub.

### segment_id: S5_generation_and_passes
- `time_start`: 03:20
- `time_end`: 04:20
- `intent`: Prove fill pipeline is constrained and outputs are pipeline-native.
- `presenter_lines`:
  - "Frame order is fixed: proxy render, void map, reprojection, extras composite, then masked generation."
  - "Known pixels are locked. Only void regions are filled."
  - "Reconstruction, proxy rendering, reprojection, extras, and generation are orchestrated per Scene ID."
  - "Every frame exports beauty plus depth, void, extras ID, extras depth, proxy render, and confidence metadata."
- `operator_actions`:
  - Show split view: `witness_reprojected`, `void_map`, `witness_refreshed`.
  - Enable lock overlay for non-void pixels.
  - Open pass browser and cycle through all pass outputs.
- `expected_visual`:
  - Clear masked-fill behavior and complete pass stack visible.
- `proof_point`:
  - Constrained generation and compositing-ready outputs are explicit.
- `risk_if_fail`:
  - Bridge latency or pass display error.
- `fallback_path`:
  - Open pre-rendered frame package and annotate each pass in same sequence.

### segment_id: S6_pilot_close
- `time_start`: 04:20
- `time_end`: 05:00
- `intent`: Convert demo momentum into pilot commitment.
- `presenter_lines`:
  - "What you saw is controlled camera movement plus controlled extras from a single still, with compositing-native outputs."
  - "We propose a scoped pilot on your art direction: one location family, three shot types, two review cycles, two-week timeline."
  - "If this meets your bar, we align today on pilot kickoff owners and target start date."
- `operator_actions`:
  - Display pilot summary card with scope, timeline, success criteria.
  - Leave final frame and pass thumbnails on screen during ask.
- `expected_visual`:
  - Clear pilot ask tied to demonstrated capabilities.
- `proof_point`:
  - Meeting closes with concrete commitment request.
- `risk_if_fail`:
  - Close becomes vague or deferred.
- `fallback_path`:
  - Use one-page pilot template and ask for named technical and creative approvers.

---

## Hard timing guardrails
- Segment hard stop times must be enforced to finish by 05:00.
- If any segment exceeds by 10+ seconds, switch to that segment's fallback immediately.

## Non-negotiable statements to include verbatim
- "This is not text-to-video."
- "Confidence is computed as one minus void-pixel ratio."
- "Known pixels are locked; only void regions are filled."
- "Extras are composited assets and deterministic."
