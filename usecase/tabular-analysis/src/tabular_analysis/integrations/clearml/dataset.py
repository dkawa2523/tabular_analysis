from __future__ import annotations
from typing import Any, Dict, Optional

def get_local_copy_if_dataset_id(dataset_id: str) -> str:
    """Download ClearML Dataset to local cache and return local path.

    TODO: implement using clearml.Dataset.get(...).get_local_copy().
    """
    raise NotImplementedError

def create_dataset_from_files(project: str, name: str, files: list[str], metadata: Dict[str, Any]) -> str:
    """Create and upload a ClearML Dataset from local files. Return dataset_id."""
    raise NotImplementedError
