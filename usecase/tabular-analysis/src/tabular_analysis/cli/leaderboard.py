from __future__ import annotations
import hydra
from omegaconf import DictConfig

from tabular_analysis.cli._common import CONFIG_PATH
from tabular_analysis.flows.leaderboard import run_leaderboard

@hydra.main(version_base=None, config_path=CONFIG_PATH, config_name="leaderboard")
def main(cfg: DictConfig) -> None:
    run_leaderboard(cfg)

if __name__ == "__main__":
    main()
