# AnchorStage MVP Prototype

This repository contains a runnable prototype for the Scene Authoring MVP described in the PRD.

Implemented subsystems:
- Scene Reconstruction Engine
- Camera Rig + Reprojection Engine
- Void Map + Witness Refresh
- Extras Placement & Rendering
- Generation Bridge + Pass Export

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m anchorstage.demo_runner
python -m unittest discover -s tests -v
```

## Notes
- The reconstruction model is a deterministic placeholder depth estimator for prototype behavior.
- Generative fill is simulated with a constrained masked fill that never overwrites locked pixels.
- Extras are deterministic billboards rendered before fill and depth-tested against proxy depth.

