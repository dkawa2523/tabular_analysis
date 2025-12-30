from __future__ import annotations
import hydra
from omegaconf import DictConfig

from tabular_analysis.flows.leaderboard import run_leaderboard

@hydra.main(version_base=None, config_path="../../../conf", config_name="leaderboard")
def main(cfg: DictConfig) -> None:
    run_leaderboard(cfg)

if __name__ == "__main__":
    main()
