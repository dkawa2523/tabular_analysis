from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

def get_local_copy_if_dataset_id(dataset_id: str) -> str:
    """Download ClearML Dataset to local cache and return local path."""
    if not dataset_id:
        raise ValueError("dataset_id is required")
    from clearml import Dataset  # type: ignore

    dataset = Dataset.get(dataset_id=dataset_id)
    return dataset.get_local_copy()

def create_dataset_from_files(
    project: str,
    name: str,
    files: list[str],
    metadata: Dict[str, Any],
    use_current_task: bool | None = None,
) -> str:
    """Create and upload a ClearML Dataset from local files. Return dataset_id."""
    if not files:
        raise ValueError("files must not be empty")
    from clearml import Dataset  # type: ignore

    if use_current_task is None:
        use_current_task = False
    dataset = Dataset.create(dataset_project=project, dataset_name=name, use_current_task=use_current_task)
    task = getattr(dataset, "_task", None)
    if task is not None and getattr(getattr(task, "data", None), "script", None) is None:
        setattr(dataset, "_created_task", False)
    for file in files:
        path = Path(file)
        if not path.exists():
            raise FileNotFoundError(f"Dataset file not found: {file}")
        dataset.add_files(path=str(path), max_workers=1)
    if metadata:
        setter = getattr(dataset, "set_metadata", None)
        if callable(setter):
            try:
                setter(metadata)
            except Exception:
                pass
    if not Dataset.is_offline():
        dataset.finalize()
    return dataset.id
