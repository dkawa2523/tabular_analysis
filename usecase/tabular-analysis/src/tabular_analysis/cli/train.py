from __future__ import annotations
import hydra
from omegaconf import DictConfig

from tabular_analysis.flows.train import run_train

@hydra.main(version_base=None, config_path="../../../conf", config_name="train")
def main(cfg: DictConfig) -> None:
    run_train(cfg)

if __name__ == "__main__":
    main()
