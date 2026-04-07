from __future__ import annotations

from abc import ABC, abstractmethod


class Render(ABC):
    @abstractmethod
    def initialiser(self) -> None:
        pass

    @abstractmethod
    def draw_entity(self, renderable, camera, position) -> None:
        pass

    @abstractmethod
    def fermer(self) -> None:
        pass
