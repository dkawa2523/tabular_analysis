from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import pandas as pd

@dataclass(frozen=True)
class DatasetRef:
    dataset_id: Optional[str] = None
    local_path: Optional[str] = None
    format: str = "csv"  # csv|parquet

def load_tabular(ref: DatasetRef) -> pd.DataFrame:
    """Load tabular data from local path (ClearML Dataset handled outside core).

    TODO: implement robust loader (csv/parquet, encoding, etc.).
    """
    if not ref.local_path:
        raise ValueError("local_path is required for core.load_tabular")
    if ref.format == "csv":
        return pd.read_csv(ref.local_path)
    if ref.format == "parquet":
        return pd.read_parquet(ref.local_path)
    raise ValueError(f"Unsupported format: {ref.format}")

