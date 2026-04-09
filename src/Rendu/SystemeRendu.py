from __future__ import annotations

import pygame

from src.Composant.Position import Position
from src.Composant.Renderable import Renderable
from src.Monde.Monde import Monde
from src.Rendu.Point3D import Point3D


class SystemeRendu:
    def __init__(self, renderer, camera=None, overlay=None) -> None:
        self.renderer = renderer
        self.camera = camera if camera is not None else renderer.camera
        self.overlay = overlay

    def render(self, monde: Monde) -> None:
        if not self.renderer.initialise:
            self.renderer.initialiser()

        self.renderer.clear()

        # Dessiner le sol 
        self.renderer.draw_sol(self.renderer.camera)

        # Dessiner les objets
        for entite in monde.entites:
            renderable = entite.get(Renderable)
            position = entite.get(Position)
            
            if position and renderable is None:
                continue

            if not renderable.visible:
                continue


            point = Point3D(position.x, position.y, position.z)
            self.renderer.draw_entity(renderable, self.camera, point)

        if self.overlay is not None:
            self.overlay(self.renderer, monde)

        self.renderer.display()
