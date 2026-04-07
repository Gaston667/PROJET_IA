from __future__ import annotations

import pygame

from src.Composant.Position import Position
from src.Rendu.Camera import Camera
from src.Rendu.Render import Render


class Render3D(Render):
    def __init__(self, largeur: int = 800, hauteur: int = 600, titre: str = "Simulation 3D"):
        self.largeur = largeur
        self.hauteur = hauteur
        self.titre = titre
        self.initialise = False
        self.ecran = None
        self.clock = None
        self.camera = Camera(x=20.0, y=18.0, z=-150.0)
        self.distance_projection = 600.0
        self.vitesse_camera = 2.0
        self.vitesse_camera_rapide = 6.0
        self.sensibilite_souris = 0.12
        self.souris_capturee = True

    def initialiser(self) -> None:
        if self.initialise:
            return

        pygame.init()
        self.ecran = pygame.display.set_mode((self.largeur, self.hauteur), pygame.RESIZABLE)
        pygame.display.set_caption(self.titre)
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        self.clock = pygame.time.Clock()
        self.initialise = True

    def draw_entity(self, renderable, camera: Camera, position: Position) -> None:
        couleur = getattr(renderable, "couleur", (255, 255, 255))
        projection = camera.conversion(
            position.x,
            position.y,
            position.z,
            self.largeur,
            self.hauteur,
            self.distance_projection,
        )
        if projection is None:
            return

        self.draw_cercle(couleur, projection)

    def gerer_evenements(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                self.largeur = event.w
                self.hauteur = event.h
                self.ecran = pygame.display.set_mode((self.largeur, self.hauteur), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.souris_capturee = not self.souris_capturee
                pygame.mouse.set_visible(not self.souris_capturee)
                pygame.event.set_grab(self.souris_capturee)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.souris_capturee:
                self.souris_capturee = True
                pygame.mouse.set_visible(False)
                pygame.event.set_grab(True)
            if event.type == pygame.MOUSEMOTION and self.souris_capturee:
                self.camera.orienter(
                    event.rel[0] * self.sensibilite_souris,
                    -event.rel[1] * self.sensibilite_souris,
                )

        self._gerer_deplacement_camera()
        return True

    def fermer(self) -> None:
        if self.initialise:
            pygame.quit()
        self.initialise = False
        self.ecran = None
        self.clock = None

    def draw_sky(self) -> None:
        self.ecran.fill((135, 206, 235))

    def draw_cercle(self, couleur, projection) -> None:
        x_ecran, y_ecran = projection
        pygame.draw.circle(self.ecran, couleur, (x_ecran, y_ecran), 6)

    def _gerer_deplacement_camera(self) -> None:
        touches = pygame.key.get_pressed()
        vitesse = self.vitesse_camera_rapide if touches[pygame.K_LSHIFT] or touches[pygame.K_RSHIFT] else self.vitesse_camera

        dx = 0.0
        dy = 0.0
        dz = 0.0

        avant_x, avant_y, avant_z = self.camera.vecteur_avant()
        droite_x, _, droite_z = self.camera.vecteur_droite()

        if touches[pygame.K_q] or touches[pygame.K_LEFT]:
            dx -= droite_x * vitesse
            dz -= droite_z * vitesse
        if touches[pygame.K_d] or touches[pygame.K_RIGHT]:
            dx += droite_x * vitesse
            dz += droite_z * vitesse
        if touches[pygame.K_z] or touches[pygame.K_UP]:
            dx += avant_x * vitesse
            dy += avant_y * vitesse
            dz += avant_z * vitesse
        if touches[pygame.K_s] or touches[pygame.K_DOWN]:
            dx -= avant_x * vitesse
            dy -= avant_y * vitesse
            dz -= avant_z * vitesse
        if touches[pygame.K_a] or touches[pygame.K_PAGEUP]:
            dy += vitesse
        if touches[pygame.K_e] or touches[pygame.K_PAGEDOWN]:
            dy -= vitesse

        if dx != 0.0 or dy != 0.0 or dz != 0.0:
            self.camera.deplacer(dx, dy, dz)

