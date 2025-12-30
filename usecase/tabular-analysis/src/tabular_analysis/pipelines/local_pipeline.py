from __future__ import annotations

from omegaconf import DictConfig, OmegaConf

from tabular_analysis.flows.dataset_register import run_dataset_register
from tabular_analysis.flows.preprocess import run_preprocess
from tabular_analysis.flows.train import run_train
from tabular_analysis.flows.leaderboard import run_leaderboard
from tabular_analysis.flows.infer import run_infer

def run_pipeline_local(cfg: DictConfig) -> None:
    """Local-first pipeline.

    Responsibilities:
    - Iterate preprocess_grid x models and execute independent tasks.
    - Collect produced train_task_ids and call leaderboard with them.
    - Optionally call infer using recommended model_id.

    NOTE:
    - Even in local mode, if ClearML enabled, each task should create its own ClearML Task
      (no parent-child).
    - In pipeline mode, user should not specify task_ids manually.

    TODO: implement in T012 after core tasks exist.
    """
    raise NotImplementedError
