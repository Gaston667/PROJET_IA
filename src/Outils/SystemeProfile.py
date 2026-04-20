from __future__ import annotations

from typing import Any

from src.Outils.Profiler import Profiler


class SystemeProfile:
    def __init__(self, systeme: Any, profiler: Profiler, nom: str | None = None) -> None:
        self.systeme = systeme
        self.profiler = profiler
        self.nom = nom or type(systeme).__name__

    def update(self, monde: Any, dt: float) -> None:
        with self.profiler.mesurer(f"systeme.{self.nom}"):
            self.systeme.update(monde, dt)

    def __getattr__(self, nom: str) -> Any:
        return getattr(self.systeme, nom)
