from __future__ import annotations
from typing import Any, Callable, Dict

from ml_platform.registry import (
    get_preprocessor as _platform_get_preprocessor,
    list_preprocessors as _platform_list_preprocessors,
    register_preprocessor as _platform_register_preprocessor,
)

def register_preprocessor(name: str, factory: Callable[[Dict[str, Any]], Any]) -> None:
    _platform_register_preprocessor(name, factory)

def get_preprocessor(name: str, cfg: Dict[str, Any]) -> Any:
    try:
        factory = _platform_get_preprocessor(name)
    except KeyError:
        available = ", ".join(_platform_list_preprocessors()) or "none"
        raise KeyError(
            f"Unknown preprocess: {name}. Available: {available}. "
            "Add it to registry/preprocessors.py"
        ) from None
    return factory(cfg)

def _register_defaults() -> None:
    # For now, preprocessing pipeline is built in core.preprocessing using config fields.
    # Future: register custom preprocess pipelines here.
    def noop_factory(cfg: Dict[str, Any]) -> Any:
        return None

    try:
        register_preprocessor("std_default", noop_factory)
    except KeyError:
        pass

_register_defaults()
