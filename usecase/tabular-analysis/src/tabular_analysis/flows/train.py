from __future__ import annotations

from omegaconf import DictConfig

def run_train(cfg: DictConfig) -> None:
    """Train a single model on a single dataset.

    - Independent ClearML task (no parent-child)
    - Produces model artifact and/or ClearML Model registry entry
    - Logs metrics and minimal plots

    TODO (Codex): implement in task T006.
    """
    raise NotImplementedError
