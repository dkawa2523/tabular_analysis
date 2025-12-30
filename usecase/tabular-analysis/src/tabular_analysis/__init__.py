"""tabular-analysis usecase package.

Design:
- core/ : pure logic (no ClearML dependency)
- integrations/clearml/ : ClearML UI/logging responsibility
- registry/ : extension points (models/preprocessors/metrics)
- cli/ : Hydra entrypoints (python -m tabular_analysis.cli.<task>)
- conf/ : Hydra configs for each CLI entrypoint

This package is implemented by Codex tasks under work/.
"""
