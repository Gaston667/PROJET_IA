from __future__ import annotations

import pygame

from src.Config import Config
from src.Rendu.Camera import Camera
from src.Rendu.Point3D import Point3D
from src.Rendu.Render import Render
import math


class Render3D(Render):
    def __init__(self, largeur: int = 800, hauteur: int = 600, titre: str = "Simulation 3D"):
        self.largeur = largeur
        self.hauteur = hauteur
        self.titre = titre
        self.initialise = False
        self.ecran = None
        self.clock = None
        self.camera = Camera(largeur, hauteur, x=20.0, y=18.0, z=-150.0)
        self.vitesse_camera = 7.0
        self.vitesse_camera_rapide = 12.0
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
        self.camera.redimensionner(self.largeur, self.hauteur)
        self.initialise = True

    def clear(self, couleur: tuple[int, int, int] = (135, 206, 235)) -> None:
        self.ecran.fill(couleur)

    def _project_points(self, points_3d, camera):
        points_2d = []

        for p in points_3d:
            projetee = camera.project(p)

            if projetee is None:
                return None
            points_2d.append(projetee)

        return points_2d

    def draw_point(self, point: Point3D, camera: Camera, couleur: tuple[int, int, int] = (255, 255, 255), rayon: int = 4) -> None:
        point_ecran = camera.project(point)
        if point_ecran is None:
            return

        pygame.draw.circle(self.ecran, couleur, (int(point_ecran.x), int(point_ecran.y)), rayon)

    def draw_line(
        self,
        point_debut: Point3D,
        point_fin: Point3D,
        camera: Camera,
        couleur: tuple[int, int, int] = (255, 255, 255),
        largeur: int = 1,
    ) -> None:
        debut = camera.project(point_debut)
        fin = camera.project(point_fin)
        if debut is None or fin is None:
            return

        pygame.draw.line(
            self.ecran,
            couleur,
            (int(debut.x), int(debut.y)),
            (int(fin.x), int(fin.y)),
            largeur,
        )

    def draw_polygon(
        self,
        points: list[Point3D],
        couleur: tuple[int, int, int] = (255, 255, 255),
        largeur: int = 0,
    ) -> None:
        if len(points) < 3:
            return
        
        points = [int(p.x)]

        pygame.draw.polygon(self.ecran, couleur, points, largeur)

    def draw_entity(self, renderable, camera: Camera, point: Point3D) -> None:
        couleur = getattr(renderable, "couleur", (255, 255, 255))
        forme = getattr(renderable, "forme", None)

        if forme in ("line", "ligne"):
            points = getattr(renderable, "points", None)
            if isinstance(points, (list, tuple)) and len(points) >= 2:
                p1 = self._decaler_point(point, points[0])
                p2 = self._decaler_point(point, points[1])
                self.draw_line(p1,p2,camera,couleur)
                return
            

        if forme in ("polygon", "quad", "triangle"):
            points = getattr(renderable, "points", None)
            if isinstance(points, (list, tuple)) and len(points) >= 3:
                points_3d = [self._decaler_point(point, p) for p in points]
                points_2d = self._project_points(points_3d, camera)
                if points_2d:
                    self.draw_polygon(points_2d, couleur)
                return

        self.draw_point(point, camera, couleur)

    def draw_sol(self, camera: Camera) -> None:
        step = 20 # Taille des cases du sol
        view = 400 # distance de rendu du sol

        couleur_sol = (50, 50, 50)
        start_x = int(self.camera.position.x // step) * step
        start_z = int(self.camera.position.z // step) * step

        for x in range(start_x - view, start_x + view + step, step):
            for z in range(start_z - view, start_z + view + step, step):
                # generer les 4 points de la case
                points_3d = self._generer_case(x, z, step)

                points_2d = self._project_points(points_3d, camera)
                if points_2d is None:
                    continue

                # shading simple
                dx = x - camera.position.x
                dz = z - camera.position.z
                dist = math.sqrt(abs(dx*dx + dz*dz))
                shade = max(40, 180 - int(dist * 0.3))
                # ajout d'une variation(effet damier) pour un peu de textture 
                if (x // step + z // step) % 2 == 0:
                    shade -= 10
                color_sol  = (shade//2, shade, shade//2)

                #desinner la case
                self.draw_polygon(points_3d, color_sol)

    def _generer_case(self, x: int, z: int, taille: int = 10) -> list[Point3D]:
        return [
            Point3D(x, 0, z),
            Point3D(x + taille, 0, z),
            Point3D(x + taille, 0, z + taille),
            Point3D(x, 0, z + taille),
        ]

    def display(self) -> None:
        pygame.display.flip()
        if self.clock is not None:
            self.clock.tick(Config.fps)

    def gerer_evenements(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                self.largeur = event.w
                self.hauteur = event.h
                self.ecran = pygame.display.set_mode((self.largeur, self.hauteur), pygame.RESIZABLE)
                self.camera.redimensionner(self.largeur, self.hauteur)
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

    def _decaler_point(self, origine: Point3D, offset) -> Point3D:
        if isinstance(offset, Point3D):
            return Point3D(origine.x + offset.x, origine.y + offset.y, origine.z + offset.z)

        if isinstance(offset, (tuple, list)) and len(offset) >= 3:
            return Point3D(origine.x + offset[0], origine.y + offset[1], origine.z + offset[2])

        return origine.copy()

    def _gerer_deplacement_camera(self) -> None:
        touches = pygame.key.get_pressed()
        dt = (self.clock.get_time() / 1000.0) if self.clock is not None else (1.0 / max(1, Config.fps))
        vitesse_base = self.vitesse_camera_rapide if touches[pygame.K_LSHIFT] or touches[pygame.K_RSHIFT] else self.vitesse_camera
        vitesse = vitesse_base * dt

        dx = 0.0
        dy = 0.0
        dz = 0.0

        avant = self.camera.vecteur_avant()
        droite = self.camera.vecteur_droite()

        if touches[pygame.K_q] or touches[pygame.K_LEFT]:
            dx -= droite.x * vitesse
            dy -= droite.y * vitesse
            dz -= droite.z * vitesse
        if touches[pygame.K_d] or touches[pygame.K_RIGHT]:
            dx += droite.x * vitesse
            dy += droite.y * vitesse
            dz += droite.z * vitesse
        if touches[pygame.K_z] or touches[pygame.K_UP]:
            dx += avant.x * vitesse
            dy += avant.y * vitesse
            dz += avant.z * vitesse
        if touches[pygame.K_s] or touches[pygame.K_DOWN]:
            dx -= avant.x * vitesse
            dy -= avant.y * vitesse
            dz -= avant.z * vitesse
        if touches[pygame.K_a] or touches[pygame.K_PAGEUP]:
            dy += vitesse
        if touches[pygame.K_e] or touches[pygame.K_PAGEDOWN]:
            dy -= vitesse

        if dx != 0.0 or dy != 0.0 or dz != 0.0:
            self.camera.deplacer(dx, dy, dz)
