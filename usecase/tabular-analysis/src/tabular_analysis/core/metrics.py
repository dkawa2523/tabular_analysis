from __future__ import annotations
from typing import Callable, Dict

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def rmse(y_true, y_pred) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))

METRICS: Dict[str, Callable] = {
    "rmse": rmse,
    "mae": lambda y_true, y_pred: float(mean_absolute_error(y_true, y_pred)),
    "r2": lambda y_true, y_pred: float(r2_score(y_true, y_pred)),
}
