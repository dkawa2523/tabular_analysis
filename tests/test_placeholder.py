from collections.abc import Mapping
from pathlib import Path
import sys
import types

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
PLATFORM_SRC = REPO_ROOT.parent / "ml-platform" / "src"

for path in (SRC_PATH, PLATFORM_SRC):
    if path.exists() and str(path) not in sys.path:
        sys.path.insert(0, str(path))


class AttrView(Mapping):
    def __init__(self, data):
        self._data = data

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __getattr__(self, key):
        if key not in self._data:
            raise AttributeError(key)
        value = self._data[key]
        return AttrView(value) if isinstance(value, dict) else value


def test_pipeline_dry_run(tmp_path):
    try:
        import hydra  # noqa: F401
    except Exception:
        hydra_stub = types.ModuleType("hydra")
        def _main(*_args, **_kwargs):
            def decorator(func):
                return func
            return decorator
        hydra_stub.main = _main
        sys.modules["hydra"] = hydra_stub

    try:
        import omegaconf  # noqa: F401
    except Exception:
        omega_stub = types.ModuleType("omegaconf")
        class DictConfig(dict):
            pass
        omega_stub.DictConfig = DictConfig
        sys.modules["omegaconf"] = omega_stub
    from usecase.cli import pipeline as pipeline_cli

    cfg = AttrView(
        {
            "usecase_id": "template",
            "dataset_id": "smoke",
            "pipeline": {
                "include_infer": False,
                "infer_mode": "batch",
                "infer_model_id": "",
                "run_steps_locally": False,
            },
            "run": {"clearml": {"enabled": False, "tags": []}},
            "hydra": {"run": {"dir": str(tmp_path)}},
        }
    )
    runner = getattr(pipeline_cli.main, "__wrapped__", pipeline_cli.main)
    runner(cfg)
