from __future__ import annotations

from src.Monde.Monde import Monde


class SystemePhysique_Electromagnetique:
    def calcul_signal(self) -> float:
        return 0.0

    def calcul_snr(self) -> float:
        return 0.0

    def detecter(self) -> bool:
        return False

    def update(self, monde: Monde, dt: float) -> None:
        pass
