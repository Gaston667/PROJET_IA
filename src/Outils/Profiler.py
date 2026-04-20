from __future__ import annotations

from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass
from time import perf_counter
from typing import Iterator


@dataclass(frozen=True)
class MesureProfil:
    nom: str
    dernier_ms: float
    moyenne_ms: float
    min_ms: float
    max_ms: float
    total_ms: float
    appels: int


class _StatProfil:
    def __init__(self, nom: str, taille_historique: int) -> None:
        self.nom = nom
        self.historique: deque[float] = deque(maxlen=taille_historique)
        self.total_ms = 0.0
        self.appels = 0
        self.min_ms = float("inf")
        self.max_ms = 0.0
        self.dernier_ms = 0.0

    def ajouter(self, duree_ms: float) -> None:
        self.dernier_ms = duree_ms
        self.historique.append(duree_ms)
        self.total_ms += duree_ms
        self.appels += 1
        self.min_ms = min(self.min_ms, duree_ms)
        self.max_ms = max(self.max_ms, duree_ms)

    def snapshot(self) -> MesureProfil:
        moyenne = sum(self.historique) / len(self.historique) if self.historique else 0.0
        minimum = self.min_ms if self.appels else 0.0
        return MesureProfil(
            nom=self.nom,
            dernier_ms=self.dernier_ms,
            moyenne_ms=moyenne,
            min_ms=minimum,
            max_ms=self.max_ms,
            total_ms=self.total_ms,
            appels=self.appels,
        )


class Profiler:
    def __init__(self, taille_historique: int = 120) -> None:
        self.taille_historique = taille_historique
        self._stats: dict[str, _StatProfil] = {}
        self._compteurs_frame: dict[str, int] = {}
        self._compteurs_total: dict[str, int] = {}
        self._debut_frame: float | None = None
        self.frame_index = 0

    def debut_frame(self) -> None:
        self._debut_frame = perf_counter()
        self._compteurs_frame.clear()

    def fin_frame(self) -> None:
        if self._debut_frame is None:
            return

        self.enregistrer("frame", perf_counter() - self._debut_frame)
        self._debut_frame = None
        self.frame_index += 1

    @contextmanager
    def mesurer(self, nom: str) -> Iterator[None]:
        debut = perf_counter()
        try:
            yield
        finally:
            self.enregistrer(nom, perf_counter() - debut)

    def enregistrer(self, nom: str, duree_secondes: float) -> None:
        stat = self._stats.get(nom)
        if stat is None:
            stat = _StatProfil(nom, self.taille_historique)
            self._stats[nom] = stat
        stat.ajouter(duree_secondes * 1000.0)

    def incrementer(self, nom: str, valeur: int = 1) -> None:
        self._compteurs_frame[nom] = self._compteurs_frame.get(nom, 0) + valeur
        self._compteurs_total[nom] = self._compteurs_total.get(nom, 0) + valeur

    def snapshot(self) -> dict[str, MesureProfil]:
        return {
            nom: stat.snapshot()
            for nom, stat in sorted(self._stats.items())
        }

    def compteurs_frame(self) -> dict[str, int]:
        return dict(sorted(self._compteurs_frame.items()))

    def compteurs_total(self) -> dict[str, int]:
        return dict(sorted(self._compteurs_total.items()))

    def fps_moyen(self) -> float:
        stat = self._stats.get("frame")
        if stat is None:
            return 0.0

        mesure = stat.snapshot()
        if mesure.moyenne_ms <= 0.0:
            return 0.0

        return 1000.0 / mesure.moyenne_ms
