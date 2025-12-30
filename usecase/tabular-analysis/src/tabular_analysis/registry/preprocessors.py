from __future__ import annotations
from typing import Any, Callable, Dict

PREPROCESS_FACTORIES: Dict[str, Callable[[Dict[str, Any]], Any]] = {}

def register_preprocessor(name: str, factory: Callable[[Dict[str, Any]], Any]) -> None:
    PREPROCESS_FACTORIES[name] = factory

def get_preprocessor(name: str, cfg: Dict[str, Any]) -> Any:
    if name not in PREPROCESS_FACTORIES:
        raise KeyError(f"Unknown preprocess: {name}. Add it to registry/preprocessors.py")
    return PREPROCESS_FACTORIES[name](cfg)

def _register_defaults() -> None:
    # For now, preprocessing pipeline is built in core.preprocessing using config fields.
    # Future: register custom preprocess pipelines here.
    def noop_factory(cfg: Dict[str, Any]) -> Any:
        return None

    register_preprocessor("std_default", noop_factory)

_register_defaults()
