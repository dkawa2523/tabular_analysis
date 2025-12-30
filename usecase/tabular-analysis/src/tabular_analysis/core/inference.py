from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import pandas as pd

def predict_single(model: Any, X_row: Any) -> Any:
    return model.predict(X_row)

def predict_batch(model: Any, X: Any) -> Any:
    return model.predict(X)

def optimize_inputs(
    model: Any,
    bundle: Any,
    search_space: Dict[str, Dict[str, float]],
    fixed: Dict[str, Any],
    n_trials: int,
    direction: str,
) -> Dict[str, Any]:
    """Very simple optimizer placeholder.

    TODO: implement properly (e.g., random search first, optional optuna later).
    """
    raise NotImplementedError
