from __future__ import annotations

"""Common CLI helpers for Hydra config handling."""

from typing import Any, Dict

from omegaconf import OmegaConf

# NOTE:
# - We intentionally avoid connecting the full config to ClearML.
# - Each task connects ONLY its relevant subset (UI contract).

def cfg_to_yaml(cfg: Any) -> str:
    return OmegaConf.to_yaml(cfg, resolve=True)

def cfg_to_dict(cfg: Any) -> Dict[str, Any]:
    return OmegaConf.to_container(cfg, resolve=True)  # type: ignore

def ensure_out_dir(path: str) -> None:
    import os
    os.makedirs(path, exist_ok=True)
