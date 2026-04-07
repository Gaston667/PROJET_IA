from __future__ import annotations

from src.Config import Config
from src.Monde.Monde import Monde


class Simulation:
    def __init__(self, monde: Monde | None = None) -> None:
        self.monde = monde if monde is not None else Monde()
        self.temps_courant: float = 0.0
        self.temps_max: float = Config.max_simulation_time
        self.en_cours: bool = True
        self.monde.temps_courant = self.temps_courant

    def step(self, dt: float) -> bool:
        if not self.en_cours:
            return False

        if dt <= 0:
            raise ValueError("Le pas de temps doit etre positif.")

        self.monde.update(dt)
        self.temps_courant += dt
        self.monde.temps_courant = self.temps_courant

        if self.temps_courant >= self.temps_max:
            self.en_cours = False

        return self.en_cours

    def reset(self) -> None:
        self.temps_courant = 0.0
        self.en_cours = True
        self.monde.temps_courant = self.temps_courant

    def est_terminee(self) -> bool:
        return not self.en_cours
