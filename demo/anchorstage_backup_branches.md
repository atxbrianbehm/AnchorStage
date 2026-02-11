# AnchorStage Demo Backup Branches

## Goal
Preserve the same proof point even when live operations degrade.  
Rule: fallback must not change narrative claim, only evidence source.

## Branch schema
- `branch_id`
- `primary_segment`
- `failure_signal`
- `fallback_action`
- `preserved_proof_point`
- `max_time_impact`
- `rejoin_point`

---

### branch_id: B1_reconstruct_timeout
- `primary_segment`: S2_ingest_reconstruct
- `failure_signal`: Reconstruction exceeds 15 seconds or depth map fails to render.
- `fallback_action`: Load precomputed `scene_id: demo_anime_street_01_prebuilt`; immediately toggle depth/confidence/splat overlays.
- `preserved_proof_point`: Single image can be represented as navigable proxy with depth artifacts.
- `max_time_impact`: +05 seconds
- `rejoin_point`: Start S3_camera_direction

### branch_id: B2_camera_artifact
- `primary_segment`: S3_camera_direction
- `failure_signal`: Live path stutter, drift, or confidence meter mismatch.
- `fallback_action`: Play prevalidated camera path `A_to_B_short_dolly_validated.mp4` with confidence telemetry overlay.
- `preserved_proof_point`: Camera motion is explicitly bounded by void-based trust metric.
- `max_time_impact`: +08 seconds
- `rejoin_point`: Start S4_extras_deterministic

### branch_id: B3_extras_spawn_failure
- `primary_segment`: S4_extras_deterministic
- `failure_signal`: Extras do not instantiate or density/motion settings fail to apply.
- `fallback_action`: Load saved layout `layout_id: commuters_v1`; scrub pose pair to show deterministic behavior.
- `preserved_proof_point`: Extras are directable composited assets with stable scene placement.
- `max_time_impact`: +07 seconds
- `rejoin_point`: Continue S4 occlusion check then S5

### branch_id: B4_occlusion_mismatch
- `primary_segment`: S4_extras_deterministic
- `failure_signal`: Visible depth ordering error after one retry.
- `fallback_action`: Open recorded occlusion validation clip with depth-buffer debug side-by-side.
- `preserved_proof_point`: Extras are depth-tested against proxy geometry.
- `max_time_impact`: +10 seconds
- `rejoin_point`: Start S5_generation_and_passes

### branch_id: B5_generation_latency
- `primary_segment`: S5_generation_and_passes
- `failure_signal`: Generative bridge exceeds 20 seconds.
- `fallback_action`: Load neighboring pose output package showing reprojected, void map, and refreshed frame with lock overlay.
- `preserved_proof_point`: Only void regions are modified; known pixels remain locked.
- `max_time_impact`: +10 seconds
- `rejoin_point`: Continue pass walkthrough in S5

### branch_id: B6_pass_export_gap
- `primary_segment`: S5_generation_and_passes
- `failure_signal`: One or more passes unavailable in live viewer.
- `fallback_action`: Open pre-exported pass ZIP and cycle through files in fixed order: beauty, depth, void, extras ID, extras depth, proxy, confidence JSON.
- `preserved_proof_point`: Output is compositing-native and multi-pass complete.
- `max_time_impact`: +12 seconds
- `rejoin_point`: Start S6_pilot_close

### branch_id: B7_close_disruption
- `primary_segment`: S6_pilot_close
- `failure_signal`: Discussion drifts into open-ended roadmap before pilot ask.
- `fallback_action`: Return to pilot card, deliver 30-second close script from template, ask for named approvers.
- `preserved_proof_point`: Meeting ends with explicit pilot commitment request.
- `max_time_impact`: +00 seconds
- `rejoin_point`: END

---

## Fallback invocation protocol
1. Owner calls "Branch" + `branch_id` out loud.
2. Operator executes mapped fallback asset immediately.
3. Presenter states one-line continuity bridge:
   - "Same proof, precomputed evidence so we stay on clock."
4. Resume at `rejoin_point` without re-explaining prior segment.
