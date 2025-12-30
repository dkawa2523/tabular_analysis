from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd
from hydra.utils import to_absolute_path
from omegaconf import DictConfig, OmegaConf

from ml_platform.config import export_config_artifact, resolve_output_dir
from ml_platform.integrations.clearml import (
    apply_ui_hygiene,
    connect_hparams,
    set_user_properties,
    task_factory,
    upload_artifact,
)

from tabular_analysis.core.data_io import DatasetRef, load_tabular
from tabular_analysis.integrations.clearml.dataset import create_dataset_from_files

_HEAD_ROWS = 20
_DEBUG_ROWS = 5

def run_dataset_register(cfg: DictConfig) -> None:
    """Register local dataset to ClearML Dataset (optional)."""
    output_dir = _resolve_output_dir(cfg)
    output_dir.mkdir(parents=True, exist_ok=True)

    data_cfg = cfg.data
    local_path = to_absolute_path(str(data_cfg.local_path))
    data_format = str(data_cfg.format).lower()
    if data_format not in {"csv", "parquet"}:
        raise ValueError(f"Unsupported data.format: {data_format}")
    path = Path(local_path)
    if not path.exists():
        raise FileNotFoundError(f"Local data not found: {local_path}")

    df = load_tabular(DatasetRef(local_path=local_path, format=data_format))
    n_rows, n_cols = df.shape

    schema = _build_schema(df)
    schema_path = output_dir / "schema.json"
    _write_json(schema_path, schema)

    head_path = output_dir / "head.csv"
    df.head(_HEAD_ROWS).to_csv(head_path, index=False)

    debug_path = output_dir / "debug_samples.jsonl"
    _write_debug_samples(debug_path, df, head_n=_DEBUG_ROWS, tail_n=_DEBUG_ROWS)

    data_hash = _file_sha256(path)
    clearml_enabled = bool(_cfg_value(cfg, "run.clearml.enabled", False))
    clearml_offline = clearml_enabled and _is_clearml_offline()

    tags = _cfg_value(cfg, "run.clearml.tags") or []
    platform_cfg = _platform_cfg(cfg)
    task_type = _task_type() if clearml_enabled else None
    task = task_factory(platform_cfg, task_type=task_type, tags=tags)

    dataset_id = None
    if clearml_enabled:
        dataset_id = create_dataset_from_files(
            project=str(data_cfg.dataset_project),
            name=str(data_cfg.dataset_name),
            files=[local_path],
            metadata={
                "usecase_id": _cfg_value(cfg, "usecase_id", "unknown"),
                "format": data_format,
                "n_rows": int(n_rows),
                "n_cols": int(n_cols),
                "sha256": data_hash,
            },
            use_current_task=clearml_offline,
        )

    manifest = _build_manifest(
        cfg=cfg,
        local_path=local_path,
        data_format=data_format,
        dataset_id=dataset_id,
        output_dir=output_dir,
        n_rows=int(n_rows),
        n_cols=int(n_cols),
        data_hash=data_hash,
    )
    manifest_path = output_dir / "manifest.json"
    _write_json(manifest_path, manifest)

    config_effective_path = output_dir / "config_effective.yaml"
    _write_config_effective(config_effective_path, cfg, output_dir)

    properties = {
        "usecase_id": _cfg_value(cfg, "usecase_id", "unknown"),
        "process": "dataset_register",
        "dataset_id": dataset_id or "",
        "n_rows": int(n_rows),
        "n_cols": int(n_cols),
    }
    hparams = {
        "data.local_path": local_path,
        "data.format": data_format,
    }
    upload_artifact(task, "schema.json", schema_path)
    upload_artifact(task, "head.csv", head_path)
    upload_artifact(task, "manifest.json", manifest_path)
    upload_artifact(task, "config_effective.yaml", config_effective_path)
    upload_artifact(task, "debug_samples.jsonl", debug_path)
    if clearml_offline:
        connect_hparams(task, hparams)
        try:
            set_user_properties(task, properties)
        except Exception:
            pass
        export_config_artifact(cfg, output_dir=output_dir, task=task)
    else:
        apply_ui_hygiene(task, cfg, hparams=hparams, properties=properties, output_dir=output_dir)

    print(f"dataset_register completed: dataset_id={dataset_id or 'local'} output_dir={output_dir}")

def _resolve_output_dir(cfg: DictConfig) -> Path:
    out_dir = _cfg_value(cfg, "output.out_dir")
    return Path(to_absolute_path(out_dir)) if out_dir else resolve_output_dir(cfg, ".")

def _cfg_value(cfg: DictConfig, dotted_path: str, default: Any | None = None) -> Any:
    value = OmegaConf.select(cfg, dotted_path)
    return default if value is None else value

def _platform_cfg(cfg: DictConfig) -> DictConfig:
    payload = OmegaConf.to_container(cfg, resolve=False)
    platform_cfg = OmegaConf.create(payload)
    _set_if_missing(platform_cfg, "run.clearml.project_name", _cfg_value(cfg, "run.clearml.project_root"))
    _set_if_missing(platform_cfg, "run.clearml.task_name", "dataset_register")
    _set_if_missing(platform_cfg, "run.clearml.queue_name", _cfg_value(cfg, "run.clearml.queue"))
    _set_if_missing(platform_cfg, "run.clearml.ui_clone.repository", _cfg_value(cfg, "run.clearml.code.repository"))
    _set_if_missing(platform_cfg, "run.clearml.ui_clone.branch", _cfg_value(cfg, "run.clearml.code.branch"))
    _set_if_missing(platform_cfg, "run.clearml.ui_clone.entry_point", _cfg_value(cfg, "run.clearml.code.entry_point"))
    return platform_cfg

def _set_if_missing(cfg: DictConfig, dotted_path: str, value: Any | None) -> None:
    if value is None:
        return
    if OmegaConf.select(cfg, dotted_path) is None:
        OmegaConf.update(cfg, dotted_path, value, merge=False)

def _is_clearml_offline() -> bool:
    try:
        from clearml import Dataset  # type: ignore
    except Exception:
        return False
    return Dataset.is_offline()

def _task_type() -> Any | None:
    try:
        from clearml import Task  # type: ignore
    except Exception:
        return None
    return Task.TaskTypes.data_processing

def _build_schema(df) -> Dict[str, Any]:
    columns = []
    for name, dtype in df.dtypes.items():
        missing = int(df[name].isna().sum())
        columns.append(
            {
                "name": str(name),
                "dtype": str(dtype),
                "n_missing": missing,
            }
        )
    return {
        "n_rows": int(df.shape[0]),
        "n_cols": int(df.shape[1]),
        "columns": columns,
    }

def _write_debug_samples(path: Path, df, *, head_n: int, tail_n: int) -> None:
    head_df = df.head(head_n).copy()
    if not head_df.empty:
        head_df["_sample_type"] = "head"
    tail_df = df.tail(tail_n).copy()
    if not tail_df.empty:
        tail_df["_sample_type"] = "tail"
    if head_df.empty and tail_df.empty:
        path.write_text("", encoding="utf-8")
        return
    combined = (
        head_df
        if tail_df.empty
        else tail_df
        if head_df.empty
        else pd.concat([head_df, tail_df], ignore_index=True)
    )
    combined.to_json(path, orient="records", lines=True, date_format="iso", force_ascii=True)

def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=True)

def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def _build_manifest(
    *,
    cfg: DictConfig,
    local_path: str,
    data_format: str,
    dataset_id: str | None,
    output_dir: Path,
    n_rows: int,
    n_cols: int,
    data_hash: str,
) -> Dict[str, Any]:
    return {
        "process": "dataset_register",
        "usecase_id": _cfg_value(cfg, "usecase_id", "unknown"),
        "inputs": {
            "local_path": local_path,
            "format": data_format,
            "sha256": data_hash,
            "n_rows": n_rows,
            "n_cols": n_cols,
        },
        "outputs": {
            "dataset_id": dataset_id,
            "schema": str(output_dir / "schema.json"),
            "head": str(output_dir / "head.csv"),
            "debug_samples": str(output_dir / "debug_samples.jsonl"),
        },
        "metadata": {
            "dataset_name": _cfg_value(cfg, "data.dataset_name"),
            "dataset_project": _cfg_value(cfg, "data.dataset_project"),
        },
    }

def _write_config_effective(path: Path, cfg: DictConfig, output_dir: Path) -> None:
    payload = {
        "usecase_id": _cfg_value(cfg, "usecase_id"),
        "data": {
            "local_path": _cfg_value(cfg, "data.local_path"),
            "format": _cfg_value(cfg, "data.format"),
            "dataset_name": _cfg_value(cfg, "data.dataset_name"),
            "dataset_project": _cfg_value(cfg, "data.dataset_project"),
        },
        "run": {
            "clearml": {
                "enabled": _cfg_value(cfg, "run.clearml.enabled", False),
            }
        },
        "output": {"out_dir": str(output_dir)},
    }
    OmegaConf.save(OmegaConf.create(payload), path)
