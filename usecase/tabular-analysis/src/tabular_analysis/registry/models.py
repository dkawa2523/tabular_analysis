from __future__ import annotations
from typing import Any, Callable, Dict

from ml_platform.registry import (
    get_model as _platform_get_model,
    list_models as _platform_list_models,
    register_model as _platform_register_model,
)

# NOTE:
# - Keep registry in one place.
# - Add new models here + conf/model/<name>.yaml

MODEL_ALIASES = {
    "lgbm": "lightgbm",
}

def register_model(name: str, factory: Callable[[Dict[str, Any]], Any]) -> None:
    canonical = _normalize_model_name(name)
    _platform_register_model(canonical, factory)

def get_model(name: str, params: Dict[str, Any]) -> Any:
    canonical = _normalize_model_name(name)
    try:
        factory = _platform_get_model(canonical)
    except KeyError:
        available = ", ".join(_platform_list_models()) or "none"
        aliases = ", ".join(f"{k}->{v}" for k, v in sorted(MODEL_ALIASES.items()))
        alias_msg = f" Aliases: {aliases}." if aliases else ""
        raise KeyError(
            f"Unknown model: {name}. Available: {available}.{alias_msg} "
            "Add it to registry/models.py"
        ) from None
    return factory(params)

def _normalize_model_name(name: str) -> str:
    if not name:
        return name
    key = name.strip().lower()
    return MODEL_ALIASES.get(key, key)

def _safe_register(name: str, factory: Callable[[Dict[str, Any]], Any]) -> None:
    try:
        register_model(name, factory)
    except KeyError:
        pass

def _register_defaults() -> None:
    # ridge
    from sklearn.linear_model import Ridge

    def ridge_factory(params: Dict[str, Any]):
        p = dict(params)
        # sklearn Ridge has no random_state unless solver supports; keep param compatibility.
        p.pop("random_state", None)
        return Ridge(**p)

    _safe_register("ridge", ridge_factory)

    # gpr
    from sklearn.gaussian_process import GaussianProcessRegressor

    def gpr_factory(params: Dict[str, Any]):
        p = dict(params)
        return GaussianProcessRegressor(**p)

    _safe_register("gpr", gpr_factory)

    # lightgbm
    def lgbm_factory(params: Dict[str, Any]):
        try:
            from lightgbm import LGBMRegressor
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "lightgbm is not installed. Install lightgbm or choose ridge/gpr."
            ) from exc
        p = dict(params)
        return LGBMRegressor(**p)

    _safe_register("lightgbm", lgbm_factory)

_register_defaults()
