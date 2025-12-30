from __future__ import annotations
from typing import Callable, Dict

from tabular_analysis.core.metrics import METRICS as DEFAULT_METRICS

METRICS: Dict[str, Callable] = dict(DEFAULT_METRICS)

def register_metric(name: str, fn: Callable) -> None:
    METRICS[name] = fn

def get_metric(name: str) -> Callable:
    if name not in METRICS:
        raise KeyError(f"Unknown metric: {name}. Add it to registry/metrics.py")
    return METRICS[name]
