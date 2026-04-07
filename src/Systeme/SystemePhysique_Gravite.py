from __future__ import annotations

from src.Composant.Force import Force
from src.Composant.Masse import Masse
from src.Config import Config
from src.Monde.Monde import Monde


class SystemePhysique_Gravite:
    def __init__(self, g: float | None = None) -> None:
        self.g = Config.gravite if g is None else g

    def update(self, monde: Monde, dt: float) -> None:
        _ = dt

        for entite in monde.entites:
            force = entite.get(Force)
            masse = entite.get(Masse)

            if force is None or masse is None:
                continue

            force.fy += -masse.valeur * self.g
