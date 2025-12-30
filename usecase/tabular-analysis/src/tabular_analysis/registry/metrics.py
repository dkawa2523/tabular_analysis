from __future__ import annotations
from typing import Callable, Dict, Iterable

from ml_platform.registry import (
    get_metric as _platform_get_metric,
    list_metrics as _platform_list_metrics,
    register_metric as _platform_register_metric,
)

from tabular_analysis.core.metrics import METRICS as DEFAULT_METRICS

def register_metric(name: str, fn: Callable) -> None:
    _platform_register_metric(name, fn)

def get_metric(name: str) -> Callable:
    try:
        return _platform_get_metric(name)
    except KeyError:
        available = ", ".join(_platform_list_metrics()) or "none"
        raise KeyError(
            f"Unknown metric: {name}. Available: {available}. Add it to registry/metrics.py"
        ) from None

def get_metrics(primary: str, others: Iterable[str] | None = None) -> Dict[str, Callable]:
    metrics: Dict[str, Callable] = {}
    metrics[primary] = get_metric(primary)
    for name in (others or []):
        if name == primary:
            continue
        metrics[name] = get_metric(name)
    return metrics

def _register_defaults() -> None:
    for name, fn in DEFAULT_METRICS.items():
        try:
            _platform_register_metric(name, fn)
        except KeyError:
            pass

_register_defaults()
