from __future__ import annotations

from typing import Any, Type


class Entite:
    def __init__(self) -> None:
        self.id: int = 0
        self.composants: dict[Type[Any], Any] = {}

    def ajouter_composant(self, composant: Any) -> None:
        self.composants[type(composant)] = composant

    def get(self, type_composant: Type[Any]) -> Any | None:
        return self.composants.get(type_composant)

    def a(self, type_composant: Type[Any]) -> bool:
        return type_composant in self.composants

    def supprimer_composant(self, type_composant: Type[Any]) -> None:
        if type_composant in self.composants:
            del self.composants[type_composant]

    def get_composant(self, type_composant: Type[Any]) -> Any | None:
        return self.get(type_composant)

    def a_composant(self, type_composant: Type[Any]) -> bool:
        return self.a(type_composant)
