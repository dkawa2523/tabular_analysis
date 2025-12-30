from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class ClearMLContext:
    task: Any
    logger: Any

def init_task_if_enabled(cfg: Dict[str, Any], task_name: str, task_type: str, project: str, tags: list[str]) -> Optional[ClearMLContext]:
    """Initialize ClearML Task.

    Must enforce UI contract:
    - Do NOT auto-connect argparse
    - Do NOT connect full config
    - Set tags and user properties fields consistently
    - Optional set_script for UI clone mode

    TODO: implement in T005 (after local core works).
    """
    return None

def connect_hparams(ctx: ClearMLContext, hparams: Dict[str, Any]) -> None:
    """Connect only relevant hyperparameters."""
    raise NotImplementedError

def set_user_properties(ctx: ClearMLContext, props: Dict[str, str]) -> None:
    raise NotImplementedError

def upload_artifact(ctx: ClearMLContext, name: str, path: str) -> None:
    raise NotImplementedError

def report_matplotlib(ctx: ClearMLContext, title: str, series: str, fig) -> None:
    raise NotImplementedError

def report_table(ctx: ClearMLContext, title: str, series: str, table) -> None:
    raise NotImplementedError
