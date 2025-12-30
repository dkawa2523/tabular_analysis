"""ClearML execution mode helpers for solution tasks."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from ml_platform.integrations import clearml as clearml_utils

try:
    from omegaconf import OmegaConf  # type: ignore
except Exception:  # pragma: no cover - optional dependency in some runtimes
    OmegaConf = None


def init_clearml_task(
    cfg: Any,
    *,
    task_type: Any | None = None,
    tags: Iterable[str] | None = None,
    reuse_last_task_id: str | None = None,
) -> Any:
    cfg_for_task = _task_factory_cfg(cfg)
    merged_tags = _merge_tags(_cfg_value(cfg, "run.clearml.tags"), tags)
    task = clearml_utils.task_factory(
        cfg_for_task,
        task_type=task_type,
        tags=merged_tags,
        reuse_last_task_id=reuse_last_task_id,
    )
    _apply_script(task, cfg)
    if clearml_utils.is_clearml_enabled(cfg):
        clearml_utils.maybe_execute_remotely(task, cfg)
    return task


def _task_factory_cfg(cfg: Any) -> dict[str, Any]:
    clearml_cfg: dict[str, Any] = {
        "enabled": bool(_cfg_value(cfg, "run.clearml.enabled", False)),
        "project_name": _cfg_value(cfg, "run.clearml.project_name"),
        "task_name": _cfg_value(cfg, "run.clearml.task_name"),
        "enqueue": False,
        "queue_name": _cfg_value(cfg, "run.clearml.queue_name"),
    }
    ui_clone = _ui_clone_payload(cfg)
    if ui_clone:
        clearml_cfg["ui_clone"] = ui_clone
    return {"run": {"clearml": clearml_cfg}}


def _ui_clone_payload(cfg: Any) -> dict[str, str] | None:
    repository = _cfg_value(cfg, "run.clearml.ui_clone.repository") or _cfg_value(
        cfg, "run.clearml.script.repository"
    )
    entry_point = _cfg_value(cfg, "run.clearml.ui_clone.entry_point") or _cfg_value(
        cfg, "run.clearml.script.entry_point"
    )
    if not repository or not entry_point:
        return None
    payload = {"repository": str(repository), "entry_point": str(entry_point)}
    branch = _cfg_value(cfg, "run.clearml.ui_clone.branch") or _cfg_value(cfg, "run.clearml.script.branch")
    if branch:
        payload["branch"] = str(branch)
    return payload


def _apply_script(task: Any, cfg: Any) -> bool:
    payload = _script_payload(cfg)
    if not payload:
        return False
    setter = getattr(task, "set_script", None)
    if not callable(setter):
        return False
    try:
        setter(**payload)
    except TypeError:
        payload.pop("working_dir", None)
        if not payload:
            return False
        setter(**payload)
    return True


def _script_payload(cfg: Any) -> dict[str, str] | None:
    repository = _cfg_value(cfg, "run.clearml.script.repository") or _cfg_value(
        cfg, "run.clearml.ui_clone.repository"
    )
    entry_point = _cfg_value(cfg, "run.clearml.script.entry_point") or _cfg_value(
        cfg, "run.clearml.ui_clone.entry_point"
    )
    if not repository or not entry_point:
        return None
    payload = {"repository": str(repository), "entry_point": str(entry_point)}
    branch = _cfg_value(cfg, "run.clearml.script.branch") or _cfg_value(cfg, "run.clearml.ui_clone.branch")
    if branch:
        payload["branch"] = str(branch)
    working_dir = _cfg_value(cfg, "run.clearml.script.working_dir") or _cfg_value(
        cfg, "run.clearml.ui_clone.working_dir"
    )
    if working_dir:
        payload["working_dir"] = str(working_dir)
    return payload


def _merge_tags(default_tags: Iterable[str] | None, extra_tags: Iterable[str] | None) -> list[str] | None:
    tags: list[str] = []
    if default_tags:
        tags.extend(list(default_tags))
    if extra_tags:
        tags.extend(list(extra_tags))
    return tags or None


def _cfg_value(cfg: Any, dotted_path: str, default: Any | None = None) -> Any:
    if cfg is None:
        return default
    if OmegaConf is not None:
        try:
            value = OmegaConf.select(cfg, dotted_path)
        except Exception:
            value = None
        if value is not None:
            return value
    current = cfg
    for key in dotted_path.split("."):
        if isinstance(current, Mapping):
            if key not in current:
                return default
            current = current[key]
            continue
        if not hasattr(current, key):
            return default
        current = getattr(current, key)
    return current
