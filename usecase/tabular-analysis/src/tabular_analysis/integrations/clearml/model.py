from __future__ import annotations
from typing import Any, Dict

def register_model(model_path: str, model_name: str, project: str, metadata: Dict[str, Any]) -> str:
    """Register a trained model to ClearML Model registry and return model_id."""
    raise NotImplementedError

def load_model_by_id(model_id: str) -> str:
    """Return local path to model file for a ClearML Model id."""
    raise NotImplementedError
