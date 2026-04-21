from __future__ import annotations

from functools import lru_cache
import logging
import math

import pygame

from src.Composant.Renderable import Renderable
from src.Config import Config
from src.Rendu.Camera import Camera
from src.Rendu.Plan import Plan
from src.Rendu.Point3D import Point3D
from src.Rendu.Render import Render

logger = logging.getLogger(__name__)


class Render3D(Render):
    """
    Moteur de rendu 3D utilisant Pygame.

    Cette classe gère l'affichage d'une scène 3D en projetant les objets
    sur un écran 2D via une caméra perspective. Elle supporte le rendu de
    lignes, polygones, cercles et points dans un espace 3D.

    Attributes:
        largeur (int): Largeur de la fenêtre en pixels.
        hauteur (int): Hauteur de la fenêtre en pixels.
        titre (str): Titre de la fenêtre.
        initialise (bool): Indique si Pygame a été initialisé.
        ecran (pygame.Surface | None): Surface d'affichage Pygame.
        clock (pygame.time.Clock | None): Horloge pour limiter les FPS.
        vitesse_camera (float): Vitesse de déplacement normale de la caméra.
        vitesse_camera_rapide (float): Vitesse de déplacement rapide (Shift).
        sensibilite_souris (float): Sensibilité de la souris pour orienter la caméra.
        souris_capturee (bool): Indique si la souris est capturée par la fenêtre.

    Example:
        >>> render = Render3D(800, 600, "Ma Simulation")
        >>> render.initialiser()
        >>> render.clear()
        >>> render.display()
        >>> render.fermer()
    """

    def __init__(
        self,
        largeur: int = 800,
        hauteur: int = 600,
        titre: str = "Simulation 3D"
    ) -> None:
        """
        Initialise le moteur de rendu 3D.

        Args:
            largeur (int): Largeur de la fenêtre en pixels. Par défaut 800.
            hauteur (int): Hauteur de la fenêtre en pixels. Par défaut 600.
            titre (str): Titre de la fenêtre. Par défaut "Simulation 3D".
        """
        self.largeur = largeur
        self.hauteur = hauteur
        self.titre = titre
        self.initialise = False
        self.ecran: pygame.Surface | None = None
        self.clock: pygame.time.Clock | None = None

        self.camera = Camera(largeur, hauteur, x=20.0, y=3.0, z=-150.0)

        self.vitesse_camera = 12.0
        self.vitesse_camera_rapide = 17.0
        self.sensibilite_souris = 0.12
        self.souris_capturee = False
        self._initialiser_occlusion_pixels()
        self.objets_occlus_pixels = 0
        self.objets_rendus = 0

    # =========================================================================
    # SECTION 1 : Cycle de vie (initialisation, affichage, fermeture)
    # =========================================================================

    def _verifier_initialisation(self) -> None:
        """
        Vérifie que le moteur a bien été initialisé avant toute opération.

        Raises:
            RuntimeError: Si initialiser() n'a pas été appelé au préalable.
        """
        if not self.initialise or self.ecran is None:
            raise RuntimeError(
                "Render3D non initialisé. Appelez initialiser() avant toute opération."
            )

    def initialiser(self) -> None:
        """
        Initialise Pygame et crée la fenêtre d'affichage.

        Cette méthode est idempotente : si Pygame est déjà initialisé,
        elle ne fait rien. Elle configure également la capture de la souris
        et initialise l'horloge FPS.

        Returns:
            None
        """
        if self.initialise:
            return

        pygame.init()
        self.ecran = pygame.display.set_mode(
            (self.largeur, self.hauteur),
            pygame.RESIZABLE
        )
        pygame.display.set_caption(self.titre)

        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

        self.clock = pygame.time.Clock()
        self.camera.redimensionner(self.largeur, self.hauteur)
        self.initialise = True

    def clear(self, couleur: tuple[int, int, int] = (130, 130, 130)) -> None:
        """
        Efface l'écran en le remplissant avec une couleur unie.

        Args:
            couleur (tuple[int, int, int]): Couleur RGB de fond. Par défaut gris.

        Raises:
            RuntimeError: Si initialiser() n'a pas été appelé.

        Returns:
            None
        """
        self._verifier_initialisation()
        self._vider_occlusion_pixels()
        self.objets_occlus_pixels = 0
        self.objets_rendus = 0
        self.ecran.fill(couleur)

    def display(self) -> None:
        """
        Met à jour l'affichage et limite le nombre de frames par seconde.

        Raises:
            RuntimeError: Si initialiser() n'a pas été appelé.

        Returns:
            None
        """
        self._verifier_initialisation()
        pygame.display.flip()

        if self.clock is not None:
            self.clock.tick(Config.fps)
            fps_actuel = int(self.clock.get_fps())
            pygame.display.set_caption(f"{self.titre} | FPS: {fps_actuel}")

    def fermer(self) -> None:
        """
        Ferme la fenêtre et libère les ressources Pygame.

        Returns:
            None
        """
        if self.initialise:
            pygame.quit()

        self.initialise = False
        self.ecran = None
        self.clock = None

    # =========================================================================
    # SECTION 2 : Gestion des événements et contrôle de la caméra
    # =========================================================================

    def gerer_evenements(self) -> bool:
        """
        Gère les événements Pygame et met à jour la caméra.

        Raises:
            RuntimeError: Si initialiser() n'a pas été appelé.

        Returns:
            bool: False si l'utilisateur souhaite quitter, True sinon.
        """
        self._verifier_initialisation()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.VIDEORESIZE:
                self.largeur = event.w
                self.hauteur = event.h
                self.ecran = pygame.display.set_mode(
                    (self.largeur, self.hauteur),
                    pygame.RESIZABLE
                )
                self.camera.redimensionner(self.largeur, self.hauteur)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.souris_capturee = not self.souris_capturee
                pygame.mouse.set_visible(not self.souris_capturee)
                pygame.event.set_grab(self.souris_capturee)

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and not self.souris_capturee
            ):
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

    def _gerer_deplacement_camera(self) -> None:
        """
        Gère le déplacement de la caméra via les touches du clavier.

        Touches supportées :
        - Z / Flèche Haut    : avancer
        - S / Flèche Bas     : reculer
        - Q / Flèche Gauche  : déplacer à gauche (strafe)
        - D / Flèche Droite  : déplacer à droite (strafe)
        - A / Page Up        : monter
        - E / Page Down      : descendre
        - Shift gauche       : accélérer le déplacement

        Returns:
            None
        """
        touches = pygame.key.get_pressed()
        dt = self.clock.get_time() / 1000.0 if self.clock else 0.016

        vitesse = (
            self.vitesse_camera_rapide
            if touches[pygame.K_LSHIFT]
            else self.vitesse_camera
        ) * dt

        dx, dy, dz = 0.0, 0.0, 0.0
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

    # =========================================================================
    # SECTION 3 : Projection et géométrie 3D
    # =========================================================================

    def _project_points(
        self,
        points: list[Point3D],
    ) -> list[tuple[float, float]] | None:
        """
        Projette une liste de points 3D en coordonnées écran 2D via self.camera.

        Si l'un des points n'est pas visible, retourne None.

        Args:
            points (list[Point3D]): Liste de points 3D à projeter.

        Returns:
            list[tuple[float, float]] | None: Coordonnées 2D projetées,
                ou None si au moins un point est hors champ.
        """
        points_2d = []
        for p in points:
            proj = self.camera.project(p)
            if proj is None:
                return None
            points_2d.append((proj.x, proj.y))
        return points_2d

    def trianguler_polygone(
        self,
        points: list[tuple[float, float]]
    ) -> list[tuple[tuple[float, float], tuple[float, float], tuple[float, float]]]:
        """
        Triangule un polygone convexe en éventail depuis le premier sommet.

        ⚠️ Fonctionne uniquement pour les polygones convexes.

        Args:
            points (list[tuple[float, float]]): Sommets du polygone 2D.
                Doit contenir au moins 3 points.

        Returns:
            list[tuple]: Liste de triangles (p1, p2, p3). Retourne [] si < 3 points.

        Example:
            >>> points = [(0,0), (1,0), (1,1), (0,1)]
            >>> len(render.trianguler_polygone(points))
            2
        """
        if len(points) < 3:
            logger.warning(
                "trianguler_polygone : %d point(s) fourni(s), minimum requis : 3.",
                len(points)
            )
            return []

        pivot = points[0]
        return [
            (pivot, points[i], points[i + 1])
            for i in range(1, len(points) - 1)
        ]

    @staticmethod
    @lru_cache(maxsize=64)
    def _generer_offsets_sphere(
        rayon: float,
        segments: int = 16,
        anneaux: int = 8
    ) -> list[tuple]:
        """
        Précalcule les offsets d'une sphère centrée en (0,0,0).
        Mis en cache par rayon/segments/anneaux.

        Args:
            rayon (float): Rayon de la sphère.
            segments (int): Subdivisions horizontales. Par défaut 16.
            anneaux (int): Subdivisions verticales. Par défaut 8.

        Returns:
            list[tuple]: Triangles sous forme de tuples (hashables).

        Example:
            >>> offsets = Render3D._generer_offsets_sphere(5.0)
            >>> len(offsets) > 0
            True
        """
        if rayon <= 0 or segments < 3 or anneaux < 2:
            return []

        triangles = []
        phi_step   = math.pi / anneaux
        theta_step = 2 * math.pi / segments

        def offset(phi, theta):
            x = rayon * math.sin(phi) * math.cos(theta)
            y = rayon * math.cos(phi)
            z = rayon * math.sin(phi) * math.sin(theta)
            return (x, y, z)

        for i in range(anneaux):
            phi_haut = i * phi_step
            phi_bas  = (i + 1) * phi_step
            for j in range(segments):
                theta_gauche = j * theta_step
                theta_droite = (j + 1) * theta_step

                haut_gauche = offset(phi_haut, theta_gauche)
                haut_droite = offset(phi_haut, theta_droite)
                bas_gauche  = offset(phi_bas,  theta_gauche)
                bas_droite  = offset(phi_bas,  theta_droite)

                triangles.append((haut_gauche, bas_gauche,  haut_droite))
                triangles.append((haut_droite, bas_gauche,  bas_droite))

        return triangles


    def _generer_sphere(
        self,
        centre: Point3D,
        rayon: float,
        segments: int = 16,
        anneaux: int = 8
    ) -> list[list[Point3D]]:
        """
        Génère la géométrie d'une sphère 3D sous forme de triangles.

        Args:
            centre (Point3D): Centre de la sphère en espace 3D.
            rayon (float): Rayon de la sphère.
            segments (int): Subdivisions horizontales. Par défaut 16.
            anneaux (int): Subdivisions verticales. Par défaut 8.

            | segments | anneaux | triangles total |   qualité  |
            |----------|---------|-----------------|------------|
            | 8        | 4       | 64              | très basse | 
            | 16       | 8       | 256             | **défaut** |
            | 32       | 16      | 1024            | haute       |
            | 64       | 32      | 4096            | très haute |



        Returns:
            list[list[Point3D]]: Liste de triangles composant la sphère.

        Example:
            >>> triangles = render._generer_sphere(Point3D(0,0,0), 5.0)
            >>> len(triangles) > 0
            True
        """
        if rayon <= 0:
            logger.warning("_generer_sphere : rayon invalide (%.2f), sphère ignorée.", rayon)
            return []

        if segments < 3 or anneaux < 2:
            logger.warning(
                "_generer_sphere : segments (%d) ou anneaux (%d) insuffisants.",
                segments, anneaux
            )
            return []

        cx, cy, cz = centre.x, centre.y, centre.z
        offsets = self._generer_offsets_sphere(rayon, segments, anneaux)  # ← depuis le cache

        triangles = []
        for (ox1,oy1,oz1), (ox2,oy2,oz2), (ox3,oy3,oz3) in offsets:
            triangles.append([
                Point3D(cx+ox1, cy+oy1, cz+oz1),
                Point3D(cx+ox2, cy+oy2, cz+oz2),
                Point3D(cx+ox3, cy+oy3, cz+oz3),
            ])

        return triangles


    # =========================================================================
    # SECTION 4 : Culling         
    # =========================================================================

    # gestion du frustum de vision pour le culling (optimisation du rendu)
    def extraire_plans_frustum(self) -> list[Plan]:
        """
        Construit les 6 plans du frustum depuis
        la position/direction et l'orientation de la caméra 
             
        Returns:
            list[Plan]: Liste des 6 plans du frustum (near, far, gauche, droit, bas, haut).    
        """

        # Vecteurs de la caméra
        va = self.camera.vecteur_avant()
        vd = self.camera.vecteur_droite()
        vh = self.camera.vecteur_haut()
        pos = self.camera.position

        near = Config.near_plane
        far = Config.far_plane
        aspect = self.camera.largeur / self.camera.hauteur
        h = math.tan(math.radians(self.camera.fov) / 2)  # hauteur du near plane
        w = h * aspect  # largeur du near plane

        return [
            self._construire_plan(va,pos.decaler(va, near)),
            self._construire_plan(va.inverser(),pos.decaler(va, far)),
            
            self._construire_plan(vd.combiner(va, w).normaliser(), pos),  # gauche
            self._construire_plan(vd.inverser().combiner(va,  w).normaliser(), pos),  # droite
            self._construire_plan(vh.combiner(va, h).normaliser(), pos),  # bas
            self._construire_plan(vh.inverser().combiner(va,  h).normaliser(), pos),  # haut
        ]
    
    def _construire_plan(self, normale: Point3D, point: Point3D) -> Plan:
        """
        Construit un Plan depuis une normale et un point sur le plan.
        Args:
            normale : Vecteur normal du plan (Point3D).
            point   : Un point appartenant au plan (Point3D).
        Returns:
            Plan avec d = -(N · P)
        """
        d = -(normale.x * point.x + normale.y * point.y + normale.z * point.z)
        return Plan(normale.x, normale.y, normale.z, d)

    def objet_dans_frustum(
        self,
        plans: list[Plan],
        points: list[Point3D],
        rayon: float = 0.0,
    ) -> bool:
        """
        Teste si un objet est potentiellement visible dans le frustum.

        Un objet est invisible seulement si TOUS ses points
        sont derrière UN MÊME plan.

        Args:
            plans  : Les 6 plans du frustum.
            points : Sommets de l'objet (Point3D).
            rayon  : Rayon de marge (sphère ou objet arrondi).

        Returns:
            False si sûrement hors frustum, True sinon.
        """
        for plan in plans:
            if self._tous_points_dehors(plan, points, rayon):
                return False
        return True
    

    def _tous_points_dehors(
        self,
        plan: Plan,
        points: list[Point3D],
        rayon: float,
    ) -> bool:
        """
        Vérifie si TOUS les points sont derrière ce plan.

        Un point est "dehors" si sa distance au plan
        est inférieure à -rayon.

        Args:
            plan   : Le plan à tester.
            points : Sommets de l'objet.
            rayon  : Marge de tolérance.

        Returns:
            True si tous les points sont derrière le plan.
        """
        for p in points:
            if plan.distance_point(p.x, p.y, p.z) >= -rayon:
                return False  # au moins un point est devant
        return True



    #  Principe général du hi-z :
    #  1. Début de frame  → _vider_hiz()
    #  2. Pour chaque objet dessiné → _mettre_a_jour_hiz() avec sa profondeur
    #  3. Pour chaque nouvel objet  → _tester_hiz() avant de le dessiner
    #     Si l'objet est entièrement derrière les occulteurs → SKIP
    #
    #  Le buffer Hi-Z est une grille basse résolution (HIZ_COLS × HIZ_ROWS).
    #  Chaque cellule = profondeur MAX des objets déjà rendus dans cette tuile.
    def _initialiser_hiz(self):
        """
        Crée le Hi-Z buffer et le remplit à 0.

        Appelé une seule fois dans __init__().
        Structure : liste 2D [row][col] de flottants.
        0.0 = aucun occulteur = tout objet passe.
        """

        self._hiz : list[list[float]] =[
            [0.0] * Config.HIZ_COLS
            for _ in range(Config.HIZ_ROWS)
        ]
            
    def _vider_hiz(self):
        """
        Remet toutes les cellules du Hi-Z buffer à 0.

        Doit être appelé EN DÉBUT DE FRAME, avant tout dessin.
        Sinon les occulteurs de la frame précédente bloqueraient
        des objets qui ne sont plus cachés.
        """

        for row in self._hiz:
            for c in range(Config.HIZ_COLS):
                row[c] = 0.0

    def _pixel_vers_tuile(self, px: float, py: float) -> tuple[int,int] | None:
        """
        Convertit des coordonnées pixel écran en indices de tuile Hi-Z.

        Args:
            px (float): Coordonnée X en pixels.
            py (float): Coordonnée Y en pixels.

        Returns:
            tuple[int, int] | None: (col, row) de la tuile,
            ou None si hors écran.
        """    

        w,h = self.ecran.get_size()

        # On normalise [0..1] puis on scale sur la grille
        col = int((px / w) * Config.HIZ_COLS)
        row = int((py / h) * Config.HIZ_ROWS)

        # Hors écran on ignore
        if col < 0 or col >= Config.HIZ_COLS or row < 0 or row >= Config.HIZ_ROWS:
            return None

        return col, row
    
    

    # ─────────────────────────────────────────────────────────────────────────────
    #  SECTION 4 : Hi-Z Occlusion Culling
    #
    #  Principe général :
    #  1. Début de frame  → _vider_hiz()
    #  2. Pour chaque objet dessiné → _mettre_a_jour_hiz() avec sa profondeur
    #  3. Pour chaque nouvel objet  → _tester_hiz() avant de le dessiner
    #     Si l'objet est entièrement derrière les occulteurs → SKIP
    #
    #  Le buffer Hi-Z est une grille basse résolution (HIZ_COLS × HIZ_ROWS).
    #  Chaque cellule = profondeur MAX des objets déjà rendus dans cette tuile.
    # ─────────────────────────────────────────────────────────────────────────────


    def _initialiser_occlusion_pixels(self) -> None:
        """
        Crée le Hi-Z buffer et le remplit à 0.

        Appelé une seule fois dans __init__().
        Structure : liste 2D [row][col] de flottants.
        0.0 = aucun occulteur = tout objet passe.
        """
        self._occlusion_pixels: list[list[float]] = [
            [0.0] * max(1, int(self.largeur))
            for _ in range(max(1, int(self.hauteur)))
        ]


    def _vider_occlusion_pixels(self) -> None:
        """
        Remet toutes les cellules du Hi-Z buffer à 0.

        Doit être appelé EN DÉBUT DE FRAME, avant tout dessin.
        Sinon les occulteurs de la frame précédente bloqueraient
        des objets qui ne sont plus cachés.
        """
        if self.ecran is not None:
            largeur, hauteur = self.ecran.get_size()
            if (
                len(self._occlusion_pixels) != hauteur
                or len(self._occlusion_pixels[0]) != largeur
            ):
                self._occlusion_pixels = [
                    [0.0] * largeur
                    for _ in range(hauteur)
                ]
                return

        for row in self._occlusion_pixels:
            for x in range(len(row)):
                row[x] = 0.0


    def _pixel_vers_tuile(self, px: float, py: float) -> tuple[int, int] | None:
        """
        Convertit des coordonnées pixel écran en indices de tuile Hi-Z.

        Args:
            px (float): Coordonnée X en pixels.
            py (float): Coordonnée Y en pixels.

        Returns:
            tuple[int, int] | None: (col, row) de la tuile,
            ou None si hors écran.
        """
        w, h = self.ecran.get_size()

        # On normalise [0..1] puis on scale sur la grille
        col = int((px / w) * Config.HIZ_COLS)
        row = int((py / h) * Config.HIZ_ROWS)

        # Hors écran → on ignore
        if col < 0 or col >= Config.HIZ_COLS or row < 0 or row >= Config.HIZ_ROWS:
            return None

        return col, row


    def _mettre_a_jour_occlusion_pixels(
        self,
        px_min: float,
        py_min: float,
        px_max: float,
        py_max: float,
        profondeur: float
    ) -> None:
        """
        Met à jour toutes les tuiles couvertes par un rectangle écran.

        Pour chaque tuile couverte, on stocke la profondeur MAX :
        si l'objet est PLUS LOIN que ce qui était déjà là, on écrase.
        Cela permet de savoir "au plus loin, il y a un objet à Z=X".

        Args:
            px_min (float): Bord gauche du rectangle en pixels.
            py_min (float): Bord haut du rectangle en pixels.
            px_max (float): Bord droit du rectangle en pixels.
            py_max (float): Bord bas du rectangle en pixels.
            profondeur (float): Profondeur de l'objet (distance caméra).
        """
        w, h = self.ecran.get_size()

        # Convertir les coins en tuiles (clampé dans la grille)
        x_min = max(0, int(px_min))
        x_max = min(w - 1, int(px_max))
        y_min = max(0, int(py_min))
        y_max = min(h - 1, int(py_max))

        if x_min > x_max or y_min > y_max:
            return

        for y in range(y_min, y_max + 1):
            ligne = self._occlusion_pixels[y]
            for x in range(x_min, x_max + 1):
                if ligne[x] == 0.0 or profondeur < ligne[x]:
                    ligne[x] = profondeur


    def _tester_occlusion_pixels(
        self,
        point: "Point3D",
        rayon: float = 0.0
    ) -> bool:
        """
        Teste si un objet est visible selon le Hi-Z buffer.

        Algorithme :
        1. On projette le centre de l'objet à l'écran.
        2. On calcule son empreinte écran (bounding box 2D via le rayon).
        3. On lit la profondeur MAX stockée dans les tuiles couvertes.
        4. Si la profondeur MIN de l'objet > profondeur MAX du buffer
        → l'objet est DERRIÈRE tous les occulteurs → caché → False.

        Args:
            point (Point3D): Position 3D de l'objet dans la scène.
            rayon (float): Rayon de la bounding sphere de l'objet.

        Returns:
            bool: True  → objet potentiellement visible (on le dessine).
                False → objet certainement caché (on le skipe).
        """
        # ── 1. Projeter le centre ────────────────────────────────────────────
        proj = self.camera.project(point)
        if proj is None:
            # Derrière la caméra, pas besoin de tester
            return False

        px, py, profondeur = proj.x, proj.y, proj.z

        # ── 2. Bounding box écran ────────────────────────────────────────────
        # On estime la taille écran du rayon via une projection approximative.
        # Si rayon == 0 on utilise juste le pixel central.
        if rayon > 0 and profondeur > 0:
            # Taille apparente ≈ rayon / profondeur × focale (approx simple)
            w, h = self.ecran.get_size()
            focale = w  # approximation : focale ≈ largeur écran
            taille_ecran = (rayon / profondeur) * focale
        else:
            taille_ecran = 1.0

        px_min = px - taille_ecran
        px_max = px + taille_ecran
        py_min = py - taille_ecran
        py_max = py + taille_ecran

        # ── 3. Lire la profondeur MAX dans les tuiles couvertes ──────────────
        w, h = self.ecran.get_size()

        x_min = max(0, int(px_min))
        x_max = min(w - 1, int(px_max))
        y_min = max(0, int(py_min))
        y_max = min(h - 1, int(py_max))

        if x_min > x_max or y_min > y_max:
            return False

        # ── 4. Comparaison ───────────────────────────────────────────────────
        # profondeur MIN de l'objet = profondeur - rayon (face avant)
        profondeur_min_objet = profondeur - rayon

        for y in range(y_min, y_max + 1):
            ligne = self._occlusion_pixels[y]
            for x in range(x_min, x_max + 1):
                val = ligne[x]
                if val == 0.0 or profondeur_min_objet <= val:
                    return True

        # Visible (ou pas encore d'info dans le buffer)
        return False

    def _mettre_a_jour_occlusion_objet(self, point: Point3D, rayon: float = 1.0) -> None:
        proj = self.camera.project(point)
        if proj is None:
            return

        px, py, profondeur = proj.x, proj.y, proj.z
        taille = (rayon / profondeur) * self.ecran.get_width() if profondeur > 0 else 1
        self._mettre_a_jour_occlusion_pixels(
            px - taille,
            py - taille,
            px + taille,
            py + taille,
            profondeur,
        )
        
    # =========================================================================
    # SECTION 4 : Dessin des primitives (ligne, triangle, point)
    # =========================================================================

    def draw_line(
        self,
        point_debut: Point3D,
        point_fin: Point3D,
        couleur: tuple[int, int, int] = (255, 255, 255),
        largeur: int = 1,
    ) -> None:
        """
        Projette et dessine une ligne 3D sur l'écran 2D.

        Si l'un des deux points n'est pas visible, la ligne n'est pas dessinée.

        Args:
            point_debut (Point3D): Point de départ en espace 3D.
            point_fin (Point3D): Point de fin en espace 3D.
            couleur (tuple[int, int, int]): Couleur RGB. Par défaut blanc.
            largeur (int): Épaisseur en pixels. Par défaut 1.

        Raises:
            RuntimeError: Si initialiser() n'a pas été appelé.

        Returns:
            None
        """
        self._verifier_initialisation()

        debut = self.camera.project(point_debut)
        fin = self.camera.project(point_fin)

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
        point1: tuple[float, float],
        point2: tuple[float, float],
        point3: tuple[float, float],
        couleur: tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        """
        Dessine un triangle plein à partir de trois points 2D déjà projetés.

        Args:
            point1 (tuple[float, float]): Premier sommet en coordonnées écran.
            point2 (tuple[float, float]): Deuxième sommet en coordonnées écran.
            point3 (tuple[float, float]): Troisième sommet en coordonnées écran.
            couleur (tuple[int, int, int]): Couleur RGB. Par défaut blanc.

        Raises:
            RuntimeError: Si initialiser() n'a pas été appelé.

        Returns:
            None
        """
        self._verifier_initialisation()

        pygame.draw.polygon(
            self.ecran,
            couleur,
            [
                (int(point1[0]), int(point1[1])),
                (int(point2[0]), int(point2[1])),
                (int(point3[0]), int(point3[1])),
            ]
        )

    def draw_point(
        self,
        point: Point3D,
        couleur: tuple[int, int, int] = (255, 255, 255),
        rayon_base: int = 6,
    ) -> None:
        """
        Projette et dessine un point 3D avec effet de perspective.

        Le rayon diminue avec la distance à la caméra pour simuler la profondeur.

        Args:
            point (Point3D): Position du point en espace 3D.
            couleur (tuple[int, int, int]): Couleur RGB. Par défaut blanc.
            rayon_base (int): Rayon de base avant perspective. Par défaut 6.

        Raises:
            RuntimeError: Si initialiser() n'a pas été appelé.

        Returns:
            None
        """
        self._verifier_initialisation()

        point_proj = self.camera.project(point)
        if point_proj is None:
            return

        # Utilisation de Point3D.distance() pour calculer la distance caméra → point
        cam_pos = Point3D(self.camera.position.x, self.camera.position.y, self.camera.position.z)
        distance = point.distance(cam_pos)

        # Réduction du rayon avec la distance, minimum 1px
        rayon = max(1, int(rayon_base * 50 / max(distance, 0.1)))

        pygame.draw.circle(
            self.ecran,
            couleur,
            (int(point_proj.x), int(point_proj.y)),
            rayon
        )

    # =========================================================================
    # SECTION 5 : Dessin des entités et de l'environnement
    # =========================================================================

    def draw_entity(self, renderable: Renderable, point: Point3D, frustum: list | None) -> None:
        self._verifier_initialisation()

        cam_pos = Point3D(self.camera.position.x, self.camera.position.y, self.camera.position.z)

        # ── Distance culling ─────────────────────────────────────────────────
        if point.distance(cam_pos) > Config.distance_culling:
            return

        couleur = getattr(renderable, "couleur", (255, 255, 255))
        forme = getattr(renderable, "forme", None)
        rayon = getattr(renderable, "rayon", 0.0)

        #Oclusion culling
        if not self._tester_occlusion_pixels(point, rayon):
            self.objets_occlus_pixels += 1
            return

        # --- Ligne ---
        if forme == Renderable.FORME_LIGNE:
            points = getattr(renderable, "points", None)
            if not isinstance(points, (list, tuple)) or len(points) < 2:
                logger.warning("draw_entity FORME_LIGNE : 'points' invalide (%s).", points)
                return
            pts_test = [point.add(p) for p in points]
            # ── Frustum culling ──────────────────────────────────────────────
            if frustum is not None and not self.objet_dans_frustum(frustum, pts_test, rayon):
                return
            if self._project_points(pts_test[:2]) is None:
                return
            self.draw_line(pts_test[0], pts_test[1], couleur)
            self._mettre_a_jour_occlusion_objet(point, rayon)
            self.objets_rendus += 1
            return

        # --- Polygone convexe ---
        if forme == Renderable.FORME_POLYGONE:
            points = getattr(renderable, "points", None)
            if not isinstance(points, (list, tuple)) or len(points) < 3:
                logger.warning("draw_entity FORME_POLYGONE : 'points' invalide (%s).", points)
                return
            pts_test = [point.add(p) for p in points]
            # ── Frustum culling ──────────────────────────────────────────────
            if frustum is not None and not self.objet_dans_frustum(frustum, pts_test, rayon):
                return
            points_2d = self._project_points(pts_test)
            if points_2d:
                for p1, p2, p3 in self.trianguler_polygone(points_2d):
                    self.draw_triangle(p1, p2, p3, couleur)
                self._mettre_a_jour_occlusion_objet(point, rayon)
                self.objets_rendus += 1
            return

        # --- Cercle / Sphère ---
        if forme == Renderable.FORME_CERCLE:
            # ── Frustum culling (un seul point + rayon suffit pour une sphère) ──
            if frustum is not None and not self.objet_dans_frustum(frustum, [point], rayon):
                return
            segments = getattr(renderable, "segments", 16)
            anneaux = getattr(renderable, "anneaux", 8)
            dessine = False
            for tri in self._generer_sphere(point, rayon, segments, anneaux):
                tri_proj = self._project_points(tri)
                if tri_proj:
                    self.draw_triangle(*tri_proj, couleur)
                    dessine = True
            if dessine:
                self._mettre_a_jour_occlusion_objet(point, rayon)
                self.objets_rendus += 1
            return
        
        # Après le dessin, mettre à jour le buffer :


    def draw_sol(
        self,
        taille_case: float = 20.0,
        nb_cases: int = 20,
        couleur: tuple[int, int, int] = (80, 180, 80),
        frustum: list | None = None
    ) -> None:
        """
        Dessine un sol en damier autour de la position actuelle de self.camera.

        Le damier est généré dynamiquement depuis la position caméra,
        simulant un sol infini. Chaque case est composée de deux triangles.
        Plus une case est éloignée, plus elle est sombre (distance shading).
        Le damier alterne entre la couleur donnée et une version plus sombre.

        Args:
            taille_case (float): Taille d'une case en unités monde. Par défaut 20.0.
            nb_cases (int): Nombre de cases visibles dans chaque direction. Par défaut 20.
            couleur (tuple): Couleur de base des cases paires. Par défaut (80, 80, 80).

        Returns:
            None
        """
        self._verifier_initialisation()

        # Couleur des cases impaires : version plus sombre de la couleur de base
        couleur2 = (
            int(couleur[0] * 0.6),
            int(couleur[1] * 0.6),
            int(couleur[2] * 0.6),
        )

        cam_x = self.camera.position.x
        cam_z = self.camera.position.z

        cam_case_x = int(cam_x // taille_case)
        cam_case_z = int(cam_z // taille_case)

        distance_max = nb_cases * taille_case

        for ix in range(-nb_cases, nb_cases + 1):
            for iz in range(-nb_cases, nb_cases + 1):

                case_x = cam_case_x + ix
                case_z = cam_case_z + iz

                x0 = case_x * taille_case
                z0 = case_z * taille_case

                # Centre de la case via Point3D pour utiliser .distance()
                centre_case = Point3D(x0 + taille_case / 2, 0.0, z0 + taille_case / 2)
                cam_sol = Point3D(cam_x, 0.0, cam_z)

                # Utilisation de Point3D.distance() pour le shading
                distance = centre_case.distance(cam_sol)

                shade = max(0.0, 1.0 - (distance / distance_max))

                base = couleur if (case_x + case_z) % 2 == 0 else couleur2
                couleur_case = (
                    int(base[0] * shade),
                    int(base[1] * shade),
                    int(base[2] * shade),
                )

                # --- Définition des 4 coins 3D de la case ---
                #   0 --- 1
                #   |     |
                #   3 --- 2
                origine = Point3D(x0, 0.0, z0)
                coins = [
                    origine,                                              # coin 0 : haut-gauche
                    origine.add(Point3D(taille_case, 0.0, 0.0)),         # coin 1 : haut-droit
                    origine.add(Point3D(taille_case, 0.0, taille_case)), # coin 2 : bas-droit
                    origine.add(Point3D(0.0, 0.0, taille_case)),         # coin 3 : bas-gauche
                ]

                coins_2d = self._project_points(coins)
                if coins_2d is None:
                    continue

                
                # ── Frustum culling par case ─────────────────────────────
                # if frustum is not None:
                #     if not self.objet_dans_frustum(frustum, coins):
                #         continue

                # Découpage en 2 triangles
                self.draw_triangle(coins_2d[0], coins_2d[1], coins_2d[2], couleur_case)
                self.draw_triangle(coins_2d[0], coins_2d[2], coins_2d[3], couleur_case)

