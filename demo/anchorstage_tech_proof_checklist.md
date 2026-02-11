# AnchorStage Technical Proof Checklist

## Use
Pre-demo and post-demo verification sheet to confirm the five non-negotiable technical claims were demonstrated.

## Checklist fields
- `proof_id`
- `claim`
- `where_shown`
- `evidence_required`
- `pass_fail`
- `notes`

---

## Proof items

### proof_id: P1_confidence_formula
- `claim`:
  - Confidence is derived from void coverage.
  - `confidence = 1 - (void_pixels / total_pixels)`
- `where_shown`:
  - Segment S3 camera movement.
- `evidence_required`:
  - Confidence meter visible while camera moves.
  - Presenter states formula in plain language.
- `pass_fail`: [ ]
- `notes`:

### proof_id: P2_locked_pixels
- `claim`:
  - Non-void (known) pixels are locked; generation touches only void regions.
- `where_shown`:
  - Segment S5 generation bridge.
- `evidence_required`:
  - Side-by-side of `witness_reprojected`, `void_map`, `witness_refreshed`.
  - Lock overlay visible on non-void area.
- `pass_fail`: [ ]
- `notes`:

### proof_id: P3_extras_occlusion
- `claim`:
  - Extras are depth-tested against proxy scene, producing correct occlusion.
- `where_shown`:
  - Segment S4 extras + occlusion scrub.
- `evidence_required`:
  - At least one frame where extra passes behind foreground geometry.
  - Presenter states extras are composited deterministic assets.
- `pass_fail`: [ ]
- `notes`:

### proof_id: P4_pass_export_stack
- `claim`:
  - Output is compositing-native with complete pass stack.
- `where_shown`:
  - Segment S5 pass browser/export.
- `evidence_required`:
  - Show each pass: beauty, depth, void map, extras ID, extras depth, proxy render, confidence metadata.
- `pass_fail`: [ ]
- `notes`:

### proof_id: P5_base_witness_anchor
- `claim`:
  - Refresh references base witness to prevent cumulative drift across sequence steps.
- `where_shown`:
  - Segment S5 narrative and sequence explanation.
- `evidence_required`:
  - Presenter explicitly states base witness anchor behavior.
  - Optional diagram or node graph visible with base witness input.
- `pass_fail`: [ ]
- `notes`:

---

## Acceptance gates
1. All P1-P5 marked pass.
2. Demo runtime <= 05:15 in rehearsal.
3. At least one rehearsal executed entirely via fallback branches.
4. Either Presenter or Operator can run full demo solo using run-of-show sheet.

## Post-demo capture
- Record audience objections linked to proof IDs.
- Record any proof that required fallback evidence.
- Log pilot close result:
  - `approved`
  - `conditional`
  - `deferred`
