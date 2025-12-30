from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

@dataclass
class PreprocessArtifacts:
    X: Any
    y: Any
    bundle: Any  # fitted transformer(s)
    recipe: Dict[str, Any]
    summary_md: str

def fit_transform_tabular(
    df: pd.DataFrame,
    target_col: str,
    id_col: Optional[str],
    cfg: Dict[str, Any],
) -> PreprocessArtifacts:
    """Fit + transform according to cfg.

    Must support multiple preprocessors via registry.
    Initial: numeric imputer + categorical imputer + onehot + standard scaler.

    TODO: implement in T004 using sklearn ColumnTransformer.
    """
    raise NotImplementedError

def transform_tabular(df: pd.DataFrame, bundle: Any, cfg: Dict[str, Any]) -> Any:
    """Apply fitted bundle to new df."""
    raise NotImplementedError

def inverse_transform_target(y_pred: Any, bundle: Any) -> Any:
    """Inverse transform for target if target_transform applied."""
    return y_pred
