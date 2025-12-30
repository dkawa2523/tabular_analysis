from __future__ import annotations

from omegaconf import DictConfig

def run_leaderboard(cfg: DictConfig) -> None:
    """Aggregate training tasks and create a leaderboard.

    Base input: leaderboard.task_ids (list of ClearML task ids)
    Optional: filter by project/tags (to build task_ids)
    Output: leaderboard.csv, selection_rationale.md, recommended_model_id

    NOTE:
    - No parent-child linkage.
    - Leaderboard is an independent analysis task.

    TODO (Codex): implement in task T010.
    """
    raise NotImplementedError
