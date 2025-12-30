from __future__ import annotations

from omegaconf import DictConfig

def run_preprocess(cfg: DictConfig) -> None:
    """Preprocess a dataset and (optionally) publish as ClearML Dataset.

    Each preprocess run is an independent task (no parent-child).
    Output should include:
    - preprocess_bundle.joblib
    - preprocess_summary.md (categorized)
    - recipe.json
    - preprocessed dataset file (parquet)
    - (if ClearML enabled) a new Dataset id

    TODO (Codex): implement in task T004.
    """
    raise NotImplementedError
