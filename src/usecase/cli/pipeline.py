"""Pipeline CLI entrypoint (solution)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import hydra
from omegaconf import DictConfig

from ml_platform.integrations import clearml as clearml_utils
from ml_platform.integrations.clearml import apply_ui_hygiene, pipeline_utils
from usecase.clearml_modes import init_clearml_task

_CONFIG_DIR = Path(__file__).resolve().parents[3] / "conf"
_STEP_PROJECT_SUFFIX = {
    "dataset": "00_dataset",
    "preprocess": "10_preprocess",
    "train_parent": "20_train_parent",
    "infer": "30_infer",
}


def _step_project(usecase_id: str, step: str) -> str:
    return f"MFG/{usecase_id}/{_STEP_PROJECT_SUFFIX[step]}"


def _pipeline_task(controller: Any) -> Any | None:
    for name in ("task", "_task", "pipeline_task"):
        value = getattr(controller, name, None)
        if value is not None:
            return value
    return None


def _args_overrides(overrides: Mapping[str, Any]) -> dict[str, Any]:
    return {f"Args/{key}": value for key, value in overrides.items()}


def _collect_step_task_ids(controller: Any) -> dict[str, str]:
    getter = getattr(controller, "get_processed_nodes", None)
    nodes = getter() if callable(getter) else {}
    payload: dict[str, str] = {}
    for name, node in dict(nodes).items():
        task_id = getattr(node, "executed", None)
        if not task_id and getattr(node, "job", None):
            job = node.job
            if hasattr(job, "task_id"):
                task_id = job.task_id() if callable(job.task_id) else job.task_id
        if task_id:
            payload[str(name)] = str(task_id)
    return payload


def _as_list(value: Any) -> list[str] | None:
    if not value:
        return None
    return [str(item) for item in value]


@hydra.main(config_path=str(_CONFIG_DIR), config_name="pipeline", version_base=None)
def main(cfg: DictConfig) -> None:
    hparams = {
        "include_infer": bool(cfg.pipeline.include_infer),
        "infer_mode": str(cfg.pipeline.infer_mode),
        "infer_model_id": str(cfg.pipeline.infer_model_id),
    }
    properties = {"usecase_id": str(cfg.usecase_id), "dataset_id": str(cfg.dataset_id)}
    if not clearml_utils.is_clearml_enabled(cfg):
        task = init_clearml_task(cfg)
        apply_ui_hygiene(task, cfg, hparams=hparams, properties=properties)
        return

    controller = pipeline_utils.create_controller(cfg, tags=_as_list(cfg.run.clearml.tags))
    pipeline_task = _pipeline_task(controller)
    apply_ui_hygiene(pipeline_task, cfg, hparams=hparams, properties=properties)

    controller.add_parameter("dataset_id", str(cfg.dataset_id), description="Dataset ID")
    controller.add_parameter("infer_mode", str(cfg.pipeline.infer_mode), description="Inference mode")
    controller.add_parameter("infer_model_id", str(cfg.pipeline.infer_model_id), description="Model ID for inference")

    run_steps_locally = bool(cfg.pipeline.run_steps_locally)
    if not run_steps_locally:
        queue_name = str(cfg.run.clearml.queue_name) if cfg.run.clearml.queue_name else None
        pipeline_utils.require_clearml_agent(queue_name)

    dataset_overrides = pipeline_utils.handoff_dataset_id(param_name="dataset_id", key="dataset_id")
    preprocess_overrides = pipeline_utils.handoff_dataset_id(param_name="dataset_id", key="dataset_id")
    train_overrides = pipeline_utils.handoff_dataset_id(param_name="dataset_id", key="dataset_id")
    infer_overrides = pipeline_utils.merge_param_overrides(
        pipeline_utils.handoff_dataset_id(param_name="dataset_id", key="dataset_id"),
        {"infer.mode": pipeline_utils.pipeline_param_ref("infer_mode")},
        pipeline_utils.handoff_model_id(param_name="infer_model_id", key="infer.model_id"),
    )

    controller.add_step(
        name="dataset",
        base_task_project=_step_project(str(cfg.usecase_id), "dataset"),
        base_task_name="dataset_register",
        parameter_override=_args_overrides(dataset_overrides),
        clone_base_task=True,
        cache_executed_step=False,
    )
    controller.add_step(
        name="preprocess",
        base_task_project=_step_project(str(cfg.usecase_id), "preprocess"),
        base_task_name="preprocess",
        parents=["dataset"],
        parameter_override=_args_overrides(preprocess_overrides),
        clone_base_task=True,
        cache_executed_step=False,
    )
    controller.add_step(
        name="train_parent",
        base_task_project=_step_project(str(cfg.usecase_id), "train_parent"),
        base_task_name="train_parent",
        parents=["preprocess"],
        parameter_override=_args_overrides(train_overrides),
        clone_base_task=True,
        cache_executed_step=False,
    )
    if bool(cfg.pipeline.include_infer):
        controller.add_step(
            name="infer",
            base_task_project=_step_project(str(cfg.usecase_id), "infer"),
            base_task_name="infer",
            parents=["train_parent"],
            parameter_override=_args_overrides(infer_overrides),
            clone_base_task=True,
            cache_executed_step=False,
        )

    try:
        controller.start_locally(run_pipeline_steps_locally=run_steps_locally)
    finally:
        step_task_ids = _collect_step_task_ids(controller)
        pipeline_utils.write_step_task_ids(step_task_ids, cfg=cfg, task=pipeline_task)


if __name__ == "__main__":
    main()
