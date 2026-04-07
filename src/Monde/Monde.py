from __future__ import annotations

from typing import Any


class Monde:
    def __init__(self) -> None:
        self.entites: list[Any] = []
        self.systemes: list[Any] = []
        self.temps_courant: float = 0.0
        self.accumulateur: float = 0.0

    def ajouter_entite(self, entite: Any) -> None:
        self.entites.append(entite)
        entite.id = len(self.entites) - 1

    def ajouter_systeme(self, systeme: Any) -> None:
        self.systemes.append(systeme)

    def supprimer_entite(self, entite: Any) -> None:
        if entite in self.entites:
            self.entites.remove(entite)

    def supprimer_systeme(self, systeme: Any) -> None:
        if systeme in self.systemes:
            self.systemes.remove(systeme)

    def update(self, dt: float) -> None:
        for systeme in self.systemes:
            systeme.update(self, dt)
