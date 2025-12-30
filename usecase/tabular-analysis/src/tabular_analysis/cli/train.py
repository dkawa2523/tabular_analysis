from __future__ import annotations
import hydra
from omegaconf import DictConfig

from tabular_analysis.cli._common import CONFIG_PATH
from tabular_analysis.flows.train import run_train

@hydra.main(version_base=None, config_path=CONFIG_PATH, config_name="train")
def main(cfg: DictConfig) -> None:
    run_train(cfg)

if __name__ == "__main__":
    main()
