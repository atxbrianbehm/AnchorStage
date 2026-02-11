# AnchorStage Anime Demo Run of Show

## Purpose
Operational cue sheet for presenter/operator roles to run the 5-minute live walkthrough with deterministic handoffs.

## Cue schema
- `cue_id`
- `trigger`
- `owner`
- `asset_or_scene_id`
- `pass_condition`
- `abort_condition`
- `next_cue`

---

### cue_id: C1_open_workspace
- `trigger`: Meeting starts; screen share live.
- `owner`: Operator
- `asset_or_scene_id`: `workspace_home`
- `pass_condition`: Empty authoring workspace visible and responsive.
- `abort_condition`: App unavailable or frozen at launch.
- `next_cue`: C2_problem_frame

### cue_id: C2_problem_frame
- `trigger`: C1 pass.
- `owner`: Presenter
- `asset_or_scene_id`: `title_overlay_anchorstage`
- `pass_condition`: Category statement delivered within 30 seconds.
- `abort_condition`: Audience question derails framing before statement completed.
- `next_cue`: C3_ingest_image

### cue_id: C3_ingest_image
- `trigger`: C2 pass.
- `owner`: Operator
- `asset_or_scene_id`: `input/anime_street_still_01.png`
- `pass_condition`: Input image loaded into ingest slot.
- `abort_condition`: File load fails.
- `next_cue`: C4_reconstruct_scene

### cue_id: C4_reconstruct_scene
- `trigger`: C3 pass.
- `owner`: Operator
- `asset_or_scene_id`: `scene_id: demo_anime_street_01`
- `pass_condition`: Depth + confidence + splat overlays available.
- `abort_condition`: Reconstruction exceeds 15 seconds or overlay generation fails.
- `next_cue`: C5_camera_move

### cue_id: C5_camera_move
- `trigger`: C4 pass.
- `owner`: Operator
- `asset_or_scene_id`: `camera_path: A_to_B_short_dolly`
- `pass_condition`: Confidence meter visible; at least one yellow-frame pause shown.
- `abort_condition`: Motion artifact obscures trust-readout explanation.
- `next_cue`: C6_extras_setup

### cue_id: C6_extras_setup
- `trigger`: C5 pass.
- `owner`: Operator
- `asset_or_scene_id`: `extras_preset: anime_commuter_light`
- `pass_condition`: Extras appear with expected density and motion mix.
- `abort_condition`: Extras fail to instantiate in preview.
- `next_cue`: C7_occlusion_check

### cue_id: C7_occlusion_check
- `trigger`: C6 pass.
- `owner`: Operator
- `asset_or_scene_id`: `occlusion_scrub_pair: pose_B, pose_C`
- `pass_condition`: At least one clear foreground occlusion example is visible.
- `abort_condition`: Depth test artifact persists after one retry.
- `next_cue`: C8_generation_bridge

### cue_id: C8_generation_bridge
- `trigger`: C7 pass.
- `owner`: Operator
- `asset_or_scene_id`: `frame_node: pose_C_refresh`
- `pass_condition`: Reprojected, void, and refreshed views shown side-by-side.
- `abort_condition`: Bridge response exceeds 20 seconds.
- `next_cue`: C9_pass_export

### cue_id: C9_pass_export
- `trigger`: C8 pass.
- `owner`: Operator
- `asset_or_scene_id`: `export_bundle: pose_C_passes`
- `pass_condition`: Beauty/depth/void/extras ID/extras depth/proxy/confidence all displayed.
- `abort_condition`: Any pass missing from viewer.
- `next_cue`: C10_pilot_close

### cue_id: C10_pilot_close
- `trigger`: C9 pass.
- `owner`: Presenter
- `asset_or_scene_id`: `pilot_close_card_v1`
- `pass_condition`: Pilot ask delivered in under 40 seconds with named next step.
- `abort_condition`: Ask becomes non-specific or no owner assigned.
- `next_cue`: END

---

## Time budget by cue block
- C1-C2: 00:30
- C3-C4: 00:50
- C5: 01:00
- C6-C7: 01:00
- C8-C9: 01:00
- C10: 00:40

Total: 05:00

## Owner roles
- `Presenter`: Narrative frame, technical framing lines, pilot close.
- `Operator`: Product operation, overlays, pass output walkthrough.
- `Technical Lead`: Confirms technical claims during Q&A and supports fallback choices.
