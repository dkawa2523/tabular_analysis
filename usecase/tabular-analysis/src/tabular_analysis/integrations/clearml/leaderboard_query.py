from __future__ import annotations
from typing import Any, Dict, List, Optional

def fetch_train_task_summary(task_id: str) -> Dict[str, Any]:
    """Fetch metrics/config/model_id from a training task.

    Contract:
    - train task must store model_id in user properties and/or artifacts.
    - train task must report primary metric scalar.

    TODO: implement in T010.
    """
    raise NotImplementedError

def find_tasks_by_filter(project: Optional[str], tags: List[str]) -> List[str]:
    """Optional fallback: search tasks by project/tags."""
    raise NotImplementedError
