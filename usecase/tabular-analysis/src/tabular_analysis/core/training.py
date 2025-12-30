from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np

@dataclass
class TrainResult:
    metrics: Dict[str, float]
    model: Any
    oof_pred: Any | None
    y_true: Any | None

def train_model_cv(
    X: Any,
    y: Any,
    model_name: str,
    model_params: Dict[str, Any],
    split_cfg: Dict[str, Any],
    metrics_cfg: Dict[str, Any],
) -> TrainResult:
    """Train a single model with CV and return metrics + fitted model.

    TODO: implement in T006 using registry.models + registry.metrics.
    """
    raise NotImplementedError
