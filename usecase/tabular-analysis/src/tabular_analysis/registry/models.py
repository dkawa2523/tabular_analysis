from __future__ import annotations
from typing import Any, Callable, Dict

# NOTE:
# - Keep registry in one place.
# - Add new models here + conf/model/<name>.yaml

MODEL_FACTORIES: Dict[str, Callable[[Dict[str, Any]], Any]] = {}

def register_model(name: str, factory: Callable[[Dict[str, Any]], Any]) -> None:
    MODEL_FACTORIES[name] = factory

def get_model(name: str, params: Dict[str, Any]):
    if name not in MODEL_FACTORIES:
        raise KeyError(f"Unknown model: {name}. Add it to registry/models.py")
    return MODEL_FACTORIES[name](params)

def _register_defaults() -> None:
    # ridge
    from sklearn.linear_model import Ridge

    def ridge_factory(params: Dict[str, Any]):
        p = dict(params)
        # sklearn Ridge has no random_state unless solver supports; keep param compatibility.
        p.pop("random_state", None)
        return Ridge(**p)

    register_model("ridge", ridge_factory)

    # gpr
    from sklearn.gaussian_process import GaussianProcessRegressor

    def gpr_factory(params: Dict[str, Any]):
        return GaussianProcessRegressor(**params)

    register_model("gpr", gpr_factory)

    # lightgbm
    try:
        from lightgbm import LGBMRegressor
    except Exception:  # pragma: no cover
        LGBMRegressor = None  # type: ignore

    def lgbm_factory(params: Dict[str, Any]):
        if LGBMRegressor is None:
            raise RuntimeError("lightgbm is not installed")
        return LGBMRegressor(**params)

    register_model("lightgbm", lgbm_factory)

_register_defaults()
