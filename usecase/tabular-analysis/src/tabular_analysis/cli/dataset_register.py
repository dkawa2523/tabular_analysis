from __future__ import annotations
import hydra
from omegaconf import DictConfig

from tabular_analysis.cli._common import CONFIG_PATH
from tabular_analysis.flows.dataset_register import run_dataset_register

@hydra.main(version_base=None, config_path=CONFIG_PATH, config_name="dataset_register")
def main(cfg: DictConfig) -> None:
    run_dataset_register(cfg)

if __name__ == "__main__":
    main()
