from __future__ import annotations

from typing import Any

from src.Config import Config
from .Simulation import Simulation


class Environnement:
    def __init__(self, simulation: Simulation | None = None, agent_id: int | None = None) -> None:
        self.simulation = simulation if simulation is not None else Simulation()
        self.agent_id = agent_id

    def reset(self) -> dict[str, Any]:
        self.simulation.reset()
        return self.get_observation()

    def step(self, action: Any) -> tuple[dict[str, Any], float]:
        _ = action
        self.simulation.step(Config.delta_t)
        return self.get_observation(), self.compute_reward()

    def get_observation(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "temps_courant": self.simulation.temps_courant,
            "en_cours": self.simulation.en_cours,
        }

    def compute_reward(self) -> float:
        return 0.0
