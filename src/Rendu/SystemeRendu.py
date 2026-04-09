from __future__ import annotations

from src.Composant.Position import Position
from src.Composant.Renderable import Renderable
from src.Monde.Monde import Monde


class SystemeRendu:
    def __init__(self, renderer, camera=None, overlay=None) -> None:
        self.renderer = renderer
        self.camera = camera if camera is not None else renderer.camera
        self.overlay = overlay

    def render(self, monde: Monde) -> None:
        if not self.renderer.initialise:
            self.renderer.initialiser()

        self.renderer.clear()

        for entite in monde.entites:
            position = entite.get(Position)
            if position is None:
                position = getattr(entite, "position", None)

            if position is None:
                continue

            renderable = entite.get(Renderable)
            if renderable is not None and not renderable.visible:
                continue

            self.renderer.draw_entity(renderable, self.camera, position)

        if self.overlay is not None:
            self.overlay(self.renderer, monde)

        self.renderer.display()
