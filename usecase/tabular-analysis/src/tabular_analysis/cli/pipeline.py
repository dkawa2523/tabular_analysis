from __future__ import annotations
import hydra
from omegaconf import DictConfig

from tabular_analysis.pipelines.local_pipeline import run_pipeline_local

@hydra.main(version_base=None, config_path="../../../conf", config_name="pipeline")
def main(cfg: DictConfig) -> None:
    # NOTE: local is the primary dev target.
    run_pipeline_local(cfg)

if __name__ == "__main__":
    main()
