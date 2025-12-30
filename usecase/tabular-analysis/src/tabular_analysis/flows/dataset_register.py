from __future__ import annotations

from omegaconf import DictConfig

def run_dataset_register(cfg: DictConfig) -> None:
    """Register local dataset to ClearML Dataset (optional).

    Local-first:
    - If run.clearml.enabled=false, this function should still validate and write local artifacts
      (schema.json, head.csv, manifest.json) and print the dataset reference.
    - If enabled, create/upload a ClearML Dataset and write its dataset_id as artifact/property.

    TODO (Codex): implement in task T003.
    """
    raise NotImplementedError
