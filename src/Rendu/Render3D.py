from __future__ import annotations

import pygame

from src.Composant.Renderable import Renderable
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
        self.camera = Camera(largeur, hauteur, x=20.0, y=3.0, z=-150.0)
        self.vitesse_camera = 12.0
        self.vitesse_camera_rapide = 17.0
        self.sensibilite_souris = 0.12
        self.souris_capturee = True


    ### Fonctions d'initialisation, et de nettoyage ##
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

    def clear(self, couleur: tuple[int, int, int] = (130, 130, 130)) -> None:
        self.ecran.fill(couleur)








    ## Fonctions de dessin pour les entitÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©s, les lignes, les polygones ##
    def draw_entity(self, renderable, camera: Camera, point: Point3D) -> None:
        couleur = getattr(renderable, "couleur", (255, 255, 255))
        forme = getattr(renderable, "forme", None)
        rayon = getattr(renderable, "rayon", 6)

        if forme == Renderable.FORME_LIGNE:
            points = getattr(renderable, "points", None)
            if isinstance(points, (list, tuple)) and len(points) >= 2:
                p1 = self._decaler_point(point, points[0])
                p2 = self._decaler_point(point, points[1])
                self.draw_line(p1,p2,camera,couleur)
                return
            
            
        if forme == Renderable.FORME_POLYGONE:
            points = getattr(renderable, "points", None)
            if isinstance(points, (list, tuple)) and len(points) >= 3:
                points_3d = [self._decaler_point(point, p) for p in points]
                points_2d = self._project_points(points_3d, camera)
                if points_2d:
                    triangles = self.trianguler_polygone(points_2d)
                    for p1, p2, p3 in triangles:
                        self.draw_triangle(p1, p2, p3, couleur)
                return
            
        if forme == Renderable.FORME_CERCLE:
            points = getattr(renderable, "points", None)
            rayon = getattr(renderable, "rayon", 6)
            segments = getattr(renderable, "segments", 16)

            if isinstance(points, Point3D):
                triangles = self._generer_cercle(points, rayon, segments)
                for tri in triangles:
                    tri_proj = self._project_points(tri, camera)
                    if tri_proj:
                        self.draw_triangle(*tri_proj, couleur)

        return

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

    def draw_triangle(
        self,
        point1: Point3D,
        point2: Point3D,
        point3: Point3D,
        couleur: tuple[int, int, int] = (255, 255, 255),
    ) -> None:        
        points_ecran = [(int(p.x), int(p.y)) for p in [point1, point2, point3] if p is not None]
        pygame.draw.polygon(self.ecran, couleur, points_ecran)

    
    def trianguler_polygone(self, points: list[Point3D]) -> list[tuple[Point3D, Point3D, Point3D]]:
        triangles = []

        for i in range(1, len(points) - 1):
            triangles.append(
                (points[0],points[i],points[i + 1])
            )
        
        return triangles

    def _generer_cercle(self, centre: Point3D, rayon: float, segments: int) -> list[Point3D]:
        points = []

        for i in range(segments):
            angle = 2 * math.pi * i / segments

            x = centre.x + rayon * math.cos(angle)
            y = centre.y
            z = centre.z + rayon * math.sin(angle)

            points.append(Point3D(x, y, z))

        triangles = []

        for i in range(segments):
            p1 = points[i]
            p2 = points[(i + 1) % segments]
            triangles.append((centre, p1, p2))

        return triangles











    ###### FOCNTIONS A LA GESTION DU SOL ######
   
    def _generer_case(self, x: int, z: int, taille: int = 10) -> list[Point3D]:
        """    GÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©nÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¨re les 4 points d'une case du sol ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â  partir de ses coordonnÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©es x et z, et de sa taille.    """
        return [
            Point3D(x, 0, z),
            Point3D(x + taille, 0, z),
            Point3D(x + taille, 0, z + taille),
            Point3D(x, 0, z + taille),
        ]
    
    def draw_sol(self, camera: Camera) -> None:
        """    Dessine un sol en damier en gÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©nÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©rant des cases autour de la position de la camÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©ra, et en les projetant ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â  l'ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©cran.    """
        step = 20 # Taille des cases du sol
        view = 400 # distance de rendu du sol

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
                self.draw_polygon(points_2d, color_sol)

    def draw_point(self, point: Point3D, camera: Camera, couleur: tuple[int, int, int] = (255, 255, 255), rayon: float = 0.2) -> None:
        """    Dessine un point 3D projetÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â© ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â  l'ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©cran, avec une taille ajustÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©e en fonction de la distance pour donner une impression de profondeur.    """
        #projection
        projection = camera.project(point)
        if projection is None:
            return
        
        
        #facteur de perspective pour donner une impression de profondeur
        facteur_perspective = camera.distance_projection / projection.z
        
        # taille a l'ecran en fonction de la distance
        rayon_ecran = rayon * facteur_perspective
        # clamper la taille pour eviter les points trop gros ou trop petits
        rayon_ecran = max(1, min(1000, int(rayon_ecran)))

        pygame.draw.circle(self.ecran, couleur, (int(projection.x), int(projection.y)), rayon_ecran)

   











    ## Fonctions de projection, de gestion des points 3D et de dÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©placement ##
   
    def _project_points(self, points_3d, camera):
        points_2d = []

        for p in points_3d:
            projetee = camera.project(p)

            if projetee is None:
                return None
            points_2d.append(projetee)

        return points_2d
    

    def _decaler_point(self, origine: Point3D, offset) -> Point3D:
        """    DÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©cale un point 3D d'une origine en ajoutant un offset, qui peut ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Âªtre soit un autre Point3D, soit une liste ou un tuple de coordonnÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©es.    """
        if isinstance(offset, Point3D):
            return Point3D(origine.x + offset.x, origine.y + offset.y, origine.z + offset.z)

        if isinstance(offset, (tuple, list)) and len(offset) >= 3:
            return Point3D(origine.x + offset[0], origine.y + offset[1], origine.z + offset[2])

        return origine.copy()
    
    def _gerer_deplacement_camera(self) -> None:
        """    GÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¨re le dÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©placement de la camÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©ra en fonction des touches du clavier, en ajustant la vitesse de dÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©placement en fonction du temps ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©coulÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â© pour assurer une expÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©rience fluide.    """
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
    
    def display(self) -> None:
        """ display() : Met ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â  jour l'affichage en appelant pygame.display.flip(), et limite le nombre de frames par seconde en utilisant self.clock.tick(Config.fps) pour assurer une expÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©rience fluide.    """
        pygame.display.flip()
        if self.clock is not None:
            self.clock.tick(Config.fps)
    
    def gerer_evenements(self) -> bool:
        """    gerer_evenements() : GÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¨re les ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©vÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©nements de la fenÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Âªtre, tels que les mouvements de la souris pour orienter la camÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©ra, les touches du clavier pour dÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©placer la camÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©ra, et les ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©vÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©nements de redimensionnement de la fenÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Âªtre. Retourne False si l'utilisateur souhaite fermer la fenÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Âªtre, sinon True.    """
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
        """    fermer() : Ferme la fenÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Âªtre et libÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¨re les ressources en appelant pygame.quit(), et rÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©initialise les attributs liÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©s ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â  l'affichage.    """
        if self.initialise:
            pygame.quit()
        self.initialise = False
        self.ecran = None
        self.clock = None

    
