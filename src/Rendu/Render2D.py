from __future__ import annotations

import pygame

from src.Composant.Position import Position
from src.Config import Config
from src.Rendu.Camera import Camera
from src.Rendu.Point3D import Point3D
from src.Rendu.Render import Render


class Render2D(Render):
    def __init__(self, largeur: int = 800, hauteur: int = 600, titre: str = "Simulation 2D"):
        self.largeur = largeur
        self.hauteur = hauteur
        self.titre = titre
        self.initialise = False
        self.ecran = None
        self.clock = None
        self.camera = Camera()

    def initialiser(self) -> None:
        if self.initialise:
            return

        pygame.init()
        self.ecran = pygame.display.set_mode((self.largeur, self.hauteur), pygame.RESIZABLE)
        pygame.display.set_caption(self.titre)
        self.clock = pygame.time.Clock()
        self.initialise = True

    def clear(self, couleur: tuple[int, int, int] = (255, 255, 255)) -> None:
        self.ecran.fill(couleur)

    def draw_entity(self, renderable, camera: Camera, position: Position) -> None:
        couleur = getattr(renderable, "couleur", (0, 0, 255))
        projection = camera.conversion(position.x, position.y, position.z, self.largeur, self.hauteur)
        if projection is None:
            return

        self.draw_point(projection, couleur)

    def draw_point(self, point: Point3D, couleur: tuple[int, int, int] = (255, 255, 255), rayon: int = 6) -> None:
        pygame.draw.circle(self.ecran, couleur, (int(point.x), int(point.y)), rayon)

    def display(self) -> None:
        pygame.display.flip()
        if self.clock is not None:
            self.clock.tick(Config.fps)

    def gerer_evenements(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.fermer()
                return False
            if event.type == pygame.VIDEORESIZE:
                self.largeur = event.w
                self.hauteur = event.h
                self.ecran = pygame.display.set_mode((self.largeur, self.hauteur), pygame.RESIZABLE)
        return True

    def fermer(self) -> None:
        if self.initialise:
            pygame.quit()
        self.initialise = False
        self.ecran = None
        self.clock = None
