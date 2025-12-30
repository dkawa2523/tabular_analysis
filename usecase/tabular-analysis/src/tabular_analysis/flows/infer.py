from __future__ import annotations

from omegaconf import DictConfig

def run_infer(cfg: DictConfig) -> None:
    """Run inference for a given model_id in a selected mode.

    Modes:
    - single: json -> json
    - batch: csv -> predictions.csv
    - optimize: search -> best_solution.json + trials.csv + plots

    TODO (Codex): implement in task T008.
    """
    raise NotImplementedError
