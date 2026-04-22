from __future__ import annotations

from functools import lru_cache
import logging
import math

import numpy as np
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
    Moteur de rendu 3D temps réel utilisant Pygame.

    Ce moteur transforme une scène 3D en image 2D grâce à une caméra
    perspective. Il implémente plusieurs techniques d'optimisation pour
    éviter de dessiner des objets inutilement :

    ┌─────────────────────────────────────────────────────────────┐
    │  PIPELINE DE RENDU                                          │
    │                                                             │
    │  1. Distance Culling   → objet trop loin ? SKIP            │
    │  2. Frustum Culling    → objet hors champ ? SKIP           │
    │  3. Occlusion Culling  → objet caché derrière un autre ?   │
    │       ├─ Hi-Z Buffer   → grille basse résolution (rapide)  │
    │       └─ Pixel Buffer  → pixel exact (précis)              │
    │  4. Projection 3D→2D   → rendu final                       │
    └─────────────────────────────────────────────────────────────┘

    Attributes:
        largeur (int): Largeur de la fenêtre en pixels.
        hauteur (int): Hauteur de la fenêtre en pixels.
        titre (str): Titre de la fenêtre.
        initialise (bool): True si Pygame a été initialisé.
        ecran (pygame.Surface | None): Surface d'affichage Pygame.
        clock (pygame.time.Clock | None): Horloge pour limiter les FPS.
        camera (Camera): Caméra perspective de la scène.
        vitesse_camera (float): Vitesse de déplacement normale.
        vitesse_camera_rapide (float): Vitesse avec Shift enfoncé.
        sensibilite_souris (float): Sensibilité de rotation à la souris.
        souris_capturee (bool): True si la souris est capturée.
        objets_rendus (int): Compteur d'objets dessinés cette frame.
        objets_occlus (int): Compteur d'objets ignorés par occlusion.

    Example:
        >>> render = Render3D(800, 600, "Ma Simulation")
        >>> render.initialiser()
        >>> render.effacer()
        >>> # ... dessiner des objets ...
        >>> render.afficher()
        >>> render.fermer()
    """

    # =========================================================================
    # SECTION 1 — Initialisation et cycle de vie
    # =========================================================================
    #
    #  Gère la création de la fenêtre, l'initialisation de Pygame et
    #  la destruction propre des ressources.
    #
    #  Méthodes publiques :
    #    initialiser()  → crée la fenêtre, démarre Pygame
    #    effacer()      → vide l'écran avant chaque frame
    #    afficher()     → envoie la frame à l'écran
    #    fermer()       → libère toutes les ressources
    # =========================================================================

    def __init__(
        self,
        largeur: int = 800,
        hauteur: int = 600,
        titre: str = "Simulation 3D"
    ) -> None:
        """
        Initialise le moteur de rendu 3D sans ouvrir de fenêtre.

        La fenêtre n'est créée qu'au premier appel à ``initialiser()``.
        Les buffers d'occlusion sont alloués immédiatement pour éviter
        des vérifications ``None`` ultérieures.

        Args:
            largeur (int): Largeur de la fenêtre en pixels. Défaut : 800.
            hauteur (int): Hauteur de la fenêtre en pixels. Défaut : 600.
            titre (str): Titre affiché dans la barre de fenêtre.
        """
        self.largeur = largeur
        self.hauteur = hauteur
        self.titre = titre
        self.initialise = False
        self.ecran: pygame.Surface | None = None
        self.clock: pygame.time.Clock | None = None

        self.camera = Camera(largeur, hauteur, x=0.0, y=3.0, z=0.0)

        self.vitesse_camera = 12.0
        self.vitesse_camera_rapide = 17.0
        self.hauteur_min_camera = 1.0
        self.sensibilite_souris = 0.12
        self.souris_capturee = False

        # Compteurs de performance (réinitialisés chaque frame dans effacer())
        self.objets_rendus = 0
        self.objets_occlus = 0
        self.objets_occlus_pixels = 0

        # Buffers d'occlusion (voir Section 4)
        self._initialiser_buffer_pixels()

    def _verifier_initialisation(self) -> None:
        """
        Garde-fou : lève une exception si le moteur n'est pas prêt.

        Doit être appelé en tête de chaque méthode publique qui
        accède à ``self.ecran``.

        Raises:
            RuntimeError: Si ``initialiser()`` n'a pas encore été appelé.
        """
        if not self.initialise or self.ecran is None:
            raise RuntimeError(
                "Render3D non initialisé. Appelez initialiser() avant toute opération."
            )

    def initialiser(self) -> None:
        """
        Ouvre la fenêtre Pygame et prépare le moteur.

        Idempotent : sans effet si déjà appelé. Configure la caméra
        aux dimensions de la fenêtre et démarre l'horloge FPS.

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

    def effacer(self, couleur: tuple[int, int, int] = (130, 130, 130)) -> None:
        """
        Prépare une nouvelle frame : vide l'écran et remet les buffers à zéro.

        Doit être appelé **en début de frame**, avant tout dessin.

        Args:
            couleur (tuple[int, int, int]): Couleur de fond RGB. Défaut : gris.

        Raises:
            RuntimeError: Si ``initialiser()`` n'a pas été appelé.
        """
        self._verifier_initialisation()
        self.ecran.fill(couleur)

        # Remet les buffers d'occlusion à zéro pour la nouvelle frame
        self._vider_buffer_pixels()

        # Remet les compteurs à zéro
        self.objets_rendus = 0
        self.objets_occlus = 0
        self.objets_occlus_pixels = 0

    def afficher(self) -> None:
        """
        Envoie la frame courante à l'écran et limite les FPS.

        Met également à jour le titre de la fenêtre avec le FPS actuel.

        Raises:
            RuntimeError: Si ``initialiser()`` n'a pas été appelé.
        """
        self._verifier_initialisation()
        pygame.display.flip()

        if self.clock is not None:
            self.clock.tick(Config.fps)
            fps_actuel = int(self.clock.get_fps())
            pygame.display.set_caption(f"{self.titre} | FPS: {fps_actuel}")

    def fermer(self) -> None:
        """
        Ferme la fenêtre et libère toutes les ressources Pygame.

        Remet le moteur dans son état non-initialisé.
        Peut être appelé même si ``initialiser()`` n'a pas été appelé.
        """
        if self.initialise:
            pygame.quit()

        self.initialise = False
        self.ecran = None
        self.clock = None

    # =========================================================================
    # SECTION 2 — Gestion des événements et contrôle caméra
    # =========================================================================
    #
    #  Traite les événements clavier/souris de Pygame et déplace la caméra.
    #
    #  Touches de déplacement :
    #    Z / ↑        → avancer
    #    S / ↓        → reculer
    #    Q / ←        → aller à gauche (strafe)
    #    D / →        → aller à droite (strafe)
    #    A / PgUp     → monter
    #    E / PgDn     → descendre
    #    Shift gauche → accélérer
    #    Échap        → capturer / libérer la souris
    #    Clic gauche  → capturer la souris
    # =========================================================================

    def gerer_evenements(self) -> bool:
        """
        Traite la file d'événements Pygame et met à jour la caméra.

        Doit être appelé **une fois par frame**, en début de boucle.

        Raises:
            RuntimeError: Si ``initialiser()`` n'a pas été appelé.

        Returns:
            bool: ``False`` si l'utilisateur veut quitter, ``True`` sinon.
        """
        self._verifier_initialisation()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.VIDEORESIZE:
                self.largeur, self.hauteur = event.w, event.h
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

        self._deplacer_camera_clavier()
        return True

    def _deplacer_camera_clavier(self) -> None:
        """
        Lit l'état du clavier et déplace la caméra en conséquence.

        Utilise ``dt`` (delta-time) pour un déplacement indépendant
        du nombre de FPS.

        Returns:
            None
        """
        touches = pygame.key.get_pressed()
        dt = self.clock.get_time() / 1000.0 if self.clock else 0.016

        vitesse = (
            self.vitesse_camera_rapide if touches[pygame.K_LSHIFT]
            else self.vitesse_camera
        ) * dt

        dx, dy, dz = 0.0, 0.0, 0.0
        avant  = self.camera.vecteur_avant()
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
            if self.camera.position.y < self.hauteur_min_camera:
                self.camera.position.y = self.hauteur_min_camera

    # =========================================================================
    # SECTION 3 — Projection et géométrie 3D
    # =========================================================================
    #
    #  Transforme des points 3D en coordonnées écran 2D.
    #  Génère la géométrie des primitives (sphères, polygones).
    #
    #  Méthodes :
    #    projeter_points()         → liste de Point3D → liste de (x,y) écran
    #    trianguler_polygone()     → polygone convexe → liste de triangles
    #    _generer_sphere()         → centre+rayon → triangles 3D
    #    _generer_offsets_sphere() → offsets mis en cache (lru_cache)
    # =========================================================================

    def projeter_points(
        self,
        points: list[Point3D],
    ) -> list[tuple[float, float]] | None:
        """
        Projette une liste de points 3D en coordonnées écran 2D.

        Utilise la caméra perspective courante. Si **un seul** point
        est hors du volume visible (derrière la caméra, etc.),
        toute la liste est rejetée.

        Args:
            points (list[Point3D]): Points 3D à projeter.

        Returns:
            list[tuple[float, float]] | None:
                Coordonnées 2D ``(x, y)`` en pixels, ou ``None``
                si au moins un point est invisible.
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
        Décompose un polygone convexe en triangles (méthode en éventail).

        La triangulation en éventail part du premier sommet ``points[0]``
        et relie chaque paire de sommets consécutifs :
        ``(p0,p1,p2), (p0,p2,p3), (p0,p3,p4), ...``

        ⚠️ Fonctionne **uniquement** pour les polygones convexes.

        Args:
            points (list[tuple[float, float]]): Sommets 2D du polygone.
                Minimum 3 points requis.

        Returns:
            list[tuple]: Liste de triangles ``(p1, p2, p3)``.
                Retourne ``[]`` si moins de 3 points.

        Example:
            >>> points = [(0,0), (1,0), (1,1), (0,1)]
            >>> len(render.trianguler_polygone(points))
            2
        """
        if len(points) < 3:
            logger.warning(
                "trianguler_polygone : %d point(s) reçu(s), minimum requis : 3.",
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
        Précalcule les offsets de triangles d'une sphère centrée en (0,0,0).

        Le résultat est mis en **cache** par ``(rayon, segments, anneaux)``
        via ``lru_cache``. Appeler deux fois avec les mêmes paramètres
        ne recalcule rien.

        Les offsets sont des tuples hashables (obligatoire pour lru_cache).
        La méthode ``_generer_sphere()`` les applique ensuite à un centre réel.

        Args:
            rayon (float): Rayon de la sphère.
            segments (int): Subdivisions horizontales (longitude). Défaut : 16.
            anneaux (int): Subdivisions verticales (latitude). Défaut : 8.

        Qualité vs performance :

            | segments | anneaux | triangles | qualité     |
            |----------|---------|-----------|-------------|
            | 8        | 4       | 64        | très basse  |
            | 16       | 8       | 256       | défaut      |
            | 32       | 16      | 1 024     | haute       |
            | 64       | 32      | 4 096     | très haute  |

        Returns:
            list[tuple]: Triangles sous forme de tuples
                ``((x1,y1,z1), (x2,y2,z2), (x3,y3,z3))``.
                Retourne ``[]`` si les paramètres sont invalides.
        """
        if rayon <= 0 or segments < 3 or anneaux < 2:
            return []

        triangles  = []
        phi_step   = math.pi / anneaux
        theta_step = 2 * math.pi / segments

        def offset(phi: float, theta: float) -> tuple[float, float, float]:
            return (
                rayon * math.sin(phi) * math.cos(theta),
                rayon * math.cos(phi),
                rayon * math.sin(phi) * math.sin(theta),
            )

        for i in range(anneaux):
            phi_haut = i * phi_step
            phi_bas  = (i + 1) * phi_step
            for j in range(segments):
                theta_gauche = j * theta_step
                theta_droite = (j + 1) * theta_step

                hg = offset(phi_haut, theta_gauche)
                hd = offset(phi_haut, theta_droite)
                bg = offset(phi_bas,  theta_gauche)
                bd = offset(phi_bas,  theta_droite)

                triangles.append((hg, bg, hd))
                triangles.append((hd, bg, bd))

        return triangles

    def _generer_sphere(
        self,
        centre: Point3D,
        rayon: float,
        segments: int = 16,
        anneaux: int = 8
    ) -> list[list[Point3D]]:
        """
        Génère les triangles 3D d'une sphère autour d'un centre donné.

        Utilise ``_generer_offsets_sphere()`` (mis en cache) et y ajoute
        les coordonnées du centre pour obtenir des points 3D réels.

        Args:
            centre (Point3D): Centre de la sphère dans la scène.
            rayon (float): Rayon en unités monde.
            segments (int): Subdivisions horizontales. Défaut : 16.
            anneaux (int): Subdivisions verticales. Défaut : 8.

        Returns:
            list[list[Point3D]]: Liste de triangles, chacun étant
                une liste de 3 ``Point3D``.
                Retourne ``[]`` si les paramètres sont invalides.

        Example:
            >>> triangles = render._generer_sphere(Point3D(0, 0, 0), 5.0)
            >>> len(triangles) > 0
            True
        """
        if rayon <= 0:
            logger.warning("_generer_sphere : rayon invalide (%.2f), ignoré.", rayon)
            return []
        if segments < 3 or anneaux < 2:
            logger.warning(
                "_generer_sphere : segments=%d ou anneaux=%d insuffisants.",
                segments, anneaux
            )
            return []

        cx, cy, cz = centre.x, centre.y, centre.z
        offsets = self._generer_offsets_sphere(rayon, segments, anneaux)

        return [
            [
                Point3D(cx + ox1, cy + oy1, cz + oz1),
                Point3D(cx + ox2, cy + oy2, cz + oz2),
                Point3D(cx + ox3, cy + oy3, cz + oz3),
            ]
            for (ox1, oy1, oz1), (ox2, oy2, oz2), (ox3, oy3, oz3) in offsets
        ]

    # =========================================================================
    # SECTION 4 — Frustum Culling
    # =========================================================================
    #
    #  Le frustum est le volume pyramidal visible par la caméra.
    #  Tout objet entièrement en dehors est rejeté AVANT la projection.
    #
    #  Fonctionnement :
    #    1. extraire_plans_frustum()  → calcule les 6 plans du frustum
    #    2. objet_dans_frustum()      → teste un objet contre les 6 plans
    #    3. _tous_points_dehors()     → helper : tous les points sont-ils
    #                                   du mauvais côté d'un plan ?
    #
    #  Un objet est rejeté seulement si TOUS ses points sont derrière
    #  UN MÊME plan (condition conservative → pas de faux négatifs).
    # =========================================================================

    def extraire_plans_frustum(self) -> list[Plan]:
        """
        Calcule les 6 plans délimitant le volume visible de la caméra.

        Les plans sont construits depuis la position, la direction et
        le FOV de la caméra. Un objet en dehors de tous ces plans
        est garanti invisible.

        Plans retournés (dans l'ordre) :
            0. Near   — plan proche
            1. Far    — plan lointain
            2. Gauche — bord gauche
            3. Droite — bord droit
            4. Bas    — bord bas
            5. Haut   — bord haut

        Returns:
            list[Plan]: Les 6 plans du frustum.
        """
        va  = self.camera.vecteur_avant()
        vd  = self.camera.vecteur_droite()
        vh  = self.camera.vecteur_haut()
        pos = self.camera.position

        near   = Config.near_plane
        far    = Config.far_plane
        aspect = self.camera.largeur / self.camera.hauteur
        demi_h = math.tan(math.radians(self.camera.fov) / 2)
        demi_w = demi_h * aspect

        return [
            self._construire_plan(va,                                  pos.decaler(va, near)),
            self._construire_plan(va.inverser(),                       pos.decaler(va, far)),
            self._construire_plan(vd.combiner(va, demi_w).normaliser(),          pos),
            self._construire_plan(vd.inverser().combiner(va, demi_w).normaliser(), pos),
            self._construire_plan(vh.combiner(va, demi_h).normaliser(),          pos),
            self._construire_plan(vh.inverser().combiner(va, demi_h).normaliser(), pos),
        ]

    def _construire_plan(self, normale: Point3D, point: Point3D) -> Plan:
        """
        Construit un plan géométrique depuis une normale et un point.

        Formule : ``d = -(N · P)`` où ``·`` est le produit scalaire.

        Args:
            normale (Point3D): Vecteur normal du plan (non nécessairement unitaire).
            point (Point3D): Un point appartenant au plan.

        Returns:
            Plan: Plan avec équation ``Nx·x + Ny·y + Nz·z + d = 0``.
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

        Test conservatif : un objet n'est rejeté que si TOUS ses points
        (+ la marge ``rayon``) sont du mauvais côté d'un même plan.
        Cela évite les faux négatifs (objets visibles rejetés par erreur).

        Args:
            plans (list[Plan]): Les 6 plans du frustum.
            points (list[Point3D]): Sommets représentatifs de l'objet.
            rayon (float): Marge de sécurité (bounding sphere). Défaut : 0.

        Returns:
            bool: ``False`` si l'objet est certainement hors frustum,
                  ``True`` s'il est potentiellement visible.
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
        Vérifie si TOUS les points sont derrière un plan donné.

        Un point est considéré "derrière" si sa distance signée au plan
        est strictement inférieure à ``-rayon``.

        Args:
            plan (Plan): Le plan à tester.
            points (list[Point3D]): Points à tester.
            rayon (float): Marge de tolérance (bounding sphere).

        Returns:
            bool: ``True`` si tous les points sont derrière le plan.
        """
        for p in points:
            if plan.distance_point(p.x, p.y, p.z) >= -rayon:
                return False
        return True

    # =========================================================================
    # SECTION 5 — Occlusion Culling : Hi-Z Buffer (grille basse résolution)
    # =========================================================================
    #
    #  Le Hi-Z buffer est une grille 2D basse résolution (HIZ_COLS × HIZ_ROWS).
    #  Chaque cellule stocke la profondeur MAXIMALE des objets déjà dessinés
    #  dans cette tuile d'écran.
    #
    #  Pipeline Hi-Z (par frame) :
    #    1. _vider_buffer_hiz()        → début de frame, tout à 0
    #    2. dessiner un objet occulteur → _enregistrer_occulteur_hiz()
    #    3. tester un nouvel objet      → _est_visible_hiz()
    #       → si objet plus loin que toutes les tuiles couvertes → SKIP
    #
    #  Avantage  : très rapide (peu de cellules à lire/écrire).
    #  Limite    : approximatif (faux positifs possibles, jamais faux négatifs).
    # =========================================================================

    def _initialiser_buffer_hiz(self) -> None:
        """
        Alloue le Hi-Z buffer et le remplit à zéro.

        Doit être appelé **une seule fois** dans ``__init__()``.
        Crée une grille ``HIZ_ROWS × HIZ_COLS`` de flottants.
        ``0.0`` signifie "aucun occulteur connu" → tout objet passe.
        """
        self._hiz: list[list[float]] = [
            [0.0] * Config.HIZ_COLS
            for _ in range(Config.HIZ_ROWS)
        ]

    def _vider_buffer_hiz(self) -> None:
        """
        Remet toutes les cellules du Hi-Z buffer à zéro.

        Doit être appelé **en début de frame** (via ``effacer()``).
        Sans cela, les occulteurs de la frame précédente
        masqueraient des objets qui ne le sont plus.
        """
        for row in self._hiz:
            for c in range(Config.HIZ_COLS):
                row[c] = 0.0

    def _coords_ecran_vers_tuile_hiz(
        self,
        px: float,
        py: float
    ) -> tuple[int, int] | None:
        """
        Convertit des coordonnées pixel en indices de tuile Hi-Z.

        Args:
            px (float): Coordonnée X en pixels.
            py (float): Coordonnée Y en pixels.

        Returns:
            tuple[int, int] | None: ``(col, row)`` de la tuile,
                ou ``None`` si hors écran.
        """
        w, h = self.ecran.get_size()
        col  = int((px / w) * Config.HIZ_COLS)
        row  = int((py / h) * Config.HIZ_ROWS)

        if col < 0 or col >= Config.HIZ_COLS or row < 0 or row >= Config.HIZ_ROWS:
            return None

        return col, row

    def _enregistrer_occulteur_hiz(
        self,
        px_min: float,
        py_min: float,
        px_max: float,
        py_max: float,
        profondeur: float
    ) -> None:
        """
        Enregistre un objet opaque comme occulteur dans le Hi-Z buffer.

        Pour chaque tuile couverte par le rectangle écran de l'objet,
        on stocke la profondeur MAX. Cela permet ensuite de savoir
        "dans cette zone, le plus loin visible est à Z=X".

        Args:
            px_min (float): Bord gauche du rectangle écran (pixels).
            py_min (float): Bord haut du rectangle écran (pixels).
            px_max (float): Bord droit du rectangle écran (pixels).
            py_max (float): Bord bas du rectangle écran (pixels).
            profondeur (float): Distance caméra-objet.
        """
        w, h = self.ecran.get_size()

        col_min = max(0, int((px_min / w) * Config.HIZ_COLS))
        col_max = min(Config.HIZ_COLS - 1, int((px_max / w) * Config.HIZ_COLS))
        row_min = max(0, int((py_min / h) * Config.HIZ_ROWS))
        row_max = min(Config.HIZ_ROWS - 1, int((py_max / h) * Config.HIZ_ROWS))

        for row in range(row_min, row_max + 1):
            for col in range(col_min, col_max + 1):
                if profondeur > self._hiz[row][col]:
                    self._hiz[row][col] = profondeur

    def _est_visible_hiz(
        self,
        point: Point3D,
        rayon: float = 0.0
    ) -> bool:
        """
        Teste si un objet est visible selon le Hi-Z buffer.

        Algorithme :
            1. Projeter le centre de l'objet à l'écran.
            2. Calculer sa bounding box 2D via le rayon.
            3. Lire la profondeur MAX dans les tuiles couvertes.
            4. Si la face avant de l'objet (``profondeur - rayon``)
               est plus loin que toutes les tuiles → objet caché.

        Args:
            point (Point3D): Centre 3D de l'objet.
            rayon (float): Rayon de la bounding sphere. Défaut : 0.

        Returns:
            bool: ``True`` → potentiellement visible (à dessiner).
                  ``False`` → certainement caché (à ignorer).
        """
        proj = self.camera.project(point)
        if proj is None:
            return False

        px, py, profondeur = proj.x, proj.y, proj.z

        if rayon > 0 and profondeur > 0:
            w, _ = self.ecran.get_size()
            taille_ecran = (rayon / profondeur) * w
        else:
            taille_ecran = 1.0

        px_min = px - taille_ecran
        px_max = px + taille_ecran
        py_min = py - taille_ecran
        py_max = py + taille_ecran

        w, h = self.ecran.get_size()

        col_min = max(0, int((px_min / w) * Config.HIZ_COLS))
        col_max = min(Config.HIZ_COLS - 1, int((px_max / w) * Config.HIZ_COLS))
        row_min = max(0, int((py_min / h) * Config.HIZ_ROWS))
        row_max = min(Config.HIZ_ROWS - 1, int((py_max / h) * Config.HIZ_ROWS))

        profondeur_face_avant = profondeur - rayon

        for row in range(row_min, row_max + 1):
            for col in range(col_min, col_max + 1):
                val = self._hiz[row][col]
                # Si une cellule est vide ou si l'objet est devant → visible
                if val == 0.0 or profondeur_face_avant <= val:
                    return True

        return False

    def _enregistrer_occulteur_hiz_objet(
        self,
        point: Point3D,
        rayon: float = 1.0
    ) -> None:
        """
        Enregistre un objet sphérique comme occulteur Hi-Z après l'avoir dessiné.

        Projette le centre, calcule la taille écran du rayon,
        et met à jour les tuiles couvertes.

        Args:
            point (Point3D): Centre 3D de l'objet.
            rayon (float): Rayon de la bounding sphere.
        """
        proj = self.camera.project(point)
        if proj is None:
            return

        px, py, profondeur = proj.x, proj.y, proj.z
        taille = (rayon / profondeur) * self.ecran.get_width() if profondeur > 0 else 1.0

        self._enregistrer_occulteur_hiz(
            px - taille, py - taille,
            px + taille, py + taille,
            profondeur,
        )

    # =========================================================================
    # SECTION 6 — Occlusion Culling : Buffer Pixel (précision maximale)
    # =========================================================================
    #
    #  Le buffer pixel est une grille de la même taille que l'écran.
    #  Chaque pixel stocke la profondeur du premier objet dessiné à cet endroit.
    #
    #  Avantage  : précision au pixel près → zéro faux positif.
    #  Limite    : coûteux en mémoire et en temps si la scène est dense.
    #
    #  Pipeline pixel (par frame) :
    #    1. _vider_buffer_pixels()            → début de frame, tout à 0
    #    2. dessiner un triangle occulteur    → _enregistrer_triangle_pixels()
    #    3. tester un objet avant de dessiner → _est_visible_pixels() (bbox)
    #       ou → _tester_triangle_pixels()    (test par triangle exact)
    # =========================================================================

    def _initialiser_buffer_pixels(self) -> None:
        """
        Alloue le buffer d'occlusion pixel-perfect.

        Crée une grille ``hauteur × largeur`` de flottants.
        ``0.0`` signifie "aucun objet dessiné ici".

        Doit être appelé **une seule fois** dans ``__init__()``.
        """
        self._buffer_pixels = np.zeros(
            (max(1, int(self.hauteur)), max(1, int(self.largeur))),
            dtype=np.float32,
        )

    def _vider_buffer_pixels(self) -> None:
        """
        Remet le buffer pixel à zéro pour une nouvelle frame.

        Redimensionne automatiquement le buffer si la fenêtre
        a changé de taille depuis la dernière frame.

        Doit être appelé **en début de frame** (via ``effacer()``).
        """
        if self.ecran is not None:
            largeur, hauteur = self.ecran.get_size()
            if (
                self._buffer_pixels.shape[0] != hauteur
                or self._buffer_pixels.shape[1] != largeur
            ):
                self._buffer_pixels = np.zeros((hauteur, largeur), dtype=np.float32)
                return

        self._buffer_pixels.fill(0.0)

    def _est_visible_pixels(
        self,
        point: Point3D,
        rayon: float = 0.0
    ) -> bool:
        """
        Teste si un objet est visible selon le buffer pixel (bounding box).

        Projette le centre, calcule la bbox 2D, et cherche un pixel
        dans la zone qui n'est pas encore occupé ou qui est devant
        l'occulteur existant.

        Args:
            point (Point3D): Centre 3D de l'objet.
            rayon (float): Rayon de la bounding sphere.

        Returns:
            bool: ``True`` → potentiellement visible.
                  ``False`` → certainement caché.
        """
        proj = self.camera.project(point)
        if proj is None:
            return False

        px, py, profondeur = proj.x, proj.y, proj.z

        if rayon > 0 and profondeur > 0:
            w, _ = self.ecran.get_size()
            taille_ecran = (rayon / profondeur) * w
        else:
            taille_ecran = 1.0

        w, h = self.ecran.get_size()
        x_min = max(0, int(px - taille_ecran))
        x_max = min(w - 1, int(px + taille_ecran))
        y_min = max(0, int(py - taille_ecran))
        y_max = min(h - 1, int(py + taille_ecran))

        if x_min > x_max or y_min > y_max:
            return False

        profondeur_face_avant = profondeur - rayon

        zone = self._buffer_pixels[y_min:y_max + 1, x_min:x_max + 1]
        return bool(np.any((zone == 0.0) | (profondeur_face_avant <= zone)))

    def _enregistrer_occulteur_pixels(
        self,
        px_min: float,
        py_min: float,
        px_max: float,
        py_max: float,
        profondeur: float
    ) -> None:
        """
        Marque une zone rectangulaire écran comme occupée dans le buffer pixel.

        Pour chaque pixel de la zone, si aucun objet n'y est encore
        ou si le nouvel objet est plus proche, on met à jour la profondeur.

        Args:
            px_min (float): Bord gauche (pixels).
            py_min (float): Bord haut (pixels).
            px_max (float): Bord droit (pixels).
            py_max (float): Bord bas (pixels).
            profondeur (float): Distance caméra-objet.
        """
        w, h = self.ecran.get_size()
        x_min = max(0, int(px_min))
        x_max = min(w - 1, int(px_max))
        y_min = max(0, int(py_min))
        y_max = min(h - 1, int(py_max))

        if x_min > x_max or y_min > y_max:
            return

        zone = self._buffer_pixels[y_min:y_max + 1, x_min:x_max + 1]
        masque = (zone == 0.0) | (profondeur < zone)
        zone[masque] = profondeur

    def _tester_triangle_pixels(self, triangle: list[Point3D]) -> bool:
        """
        Teste si un triangle projeté est visible dans le buffer pixel.

        Test précis au pixel : pour chaque pixel dans la bounding box
        du triangle, on vérifie s'il est à l'intérieur du triangle
        (test barycentrique) et si sa profondeur le rend visible.

        Args:
            triangle (list[Point3D]): 3 sommets du triangle projeté
                en coordonnées écran (x, y, z=profondeur).

        Returns:
            bool: ``True`` si au moins un pixel est visible.
        """
        w, h = self.ecran.get_size()
        x_min = max(0, int(min(p.x for p in triangle)))
        x_max = min(w - 1, int(max(p.x for p in triangle)))
        y_min = max(0, int(min(p.y for p in triangle)))
        y_max = min(h - 1, int(max(p.y for p in triangle)))

        if x_min > x_max or y_min > y_max:
            return False

        p1, p2, p3 = triangle
        profondeur = min(p.z for p in triangle)
        yy, xx = np.ogrid[y_min:y_max + 1, x_min:x_max + 1]
        px = xx + 0.5
        py = yy + 0.5

        d1 = (px - p2.x) * (p1.y - p2.y) - (p1.x - p2.x) * (py - p2.y)
        d2 = (px - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (py - p3.y)
        d3 = (px - p1.x) * (p3.y - p1.y) - (p3.x - p1.x) * (py - p1.y)
        dedans = ~(((d1 < 0) | (d2 < 0) | (d3 < 0)) & ((d1 > 0) | (d2 > 0) | (d3 > 0)))

        zone = self._buffer_pixels[y_min:y_max + 1, x_min:x_max + 1]
        visible = dedans & ((zone == 0.0) | (profondeur <= zone))
        return bool(np.any(visible))

    def _enregistrer_triangle_pixels(self, triangle: list[Point3D]) -> None:
        """
        Enregistre un triangle dessiné dans le buffer pixel.

        Pour chaque pixel à l'intérieur du triangle (test barycentrique),
        met à jour la profondeur si l'objet est plus proche.

        Args:
            triangle (list[Point3D]): 3 sommets du triangle projeté
                en coordonnées écran (x, y, z=profondeur).
        """
        w, h = self.ecran.get_size()
        x_min = max(0, int(min(p.x for p in triangle)))
        x_max = min(w - 1, int(max(p.x for p in triangle)))
        y_min = max(0, int(min(p.y for p in triangle)))
        y_max = min(h - 1, int(max(p.y for p in triangle)))

        if x_min > x_max or y_min > y_max:
            return

        p1, p2, p3 = triangle
        profondeur = min(p.z for p in triangle)
        yy, xx = np.ogrid[y_min:y_max + 1, x_min:x_max + 1]
        px = xx + 0.5
        py = yy + 0.5

        d1 = (px - p2.x) * (p1.y - p2.y) - (p1.x - p2.x) * (py - p2.y)
        d2 = (px - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (py - p3.y)
        d3 = (px - p1.x) * (p3.y - p1.y) - (p3.x - p1.x) * (py - p1.y)
        dedans = ~(((d1 < 0) | (d2 < 0) | (d3 < 0)) & ((d1 > 0) | (d2 > 0) | (d3 > 0)))

        zone = self._buffer_pixels[y_min:y_max + 1, x_min:x_max + 1]
        masque = dedans & ((zone == 0.0) | (profondeur < zone))
        zone[masque] = profondeur

    def _point_dans_triangle_2d(
        self,
        px: float,
        py: float,
        p1: Point3D,
        p2: Point3D,
        p3: Point3D,
    ) -> bool:
        """
        Teste si un point 2D est à l'intérieur d'un triangle 2D.

        Utilise le test des signes des produits en croix
        (méthode des demi-plans). Fonctionne pour tout triangle
        non dégénéré, quelle que soit son orientation.

        Args:
            px (float): Coordonnée X du point à tester.
            py (float): Coordonnée Y du point à tester.
            p1 (Point3D): Premier sommet (seuls x et y sont utilisés).
            p2 (Point3D): Deuxième sommet.
            p3 (Point3D): Troisième sommet.

        Returns:
            bool: ``True`` si le point est à l'intérieur ou sur le bord.
        """
        d1 = (px - p2.x) * (p1.y - p2.y) - (p1.x - p2.x) * (py - p2.y)
        d2 = (px - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (py - p3.y)
        d3 = (px - p1.x) * (p3.y - p1.y) - (p3.x - p1.x) * (py - p1.y)

        negatif = d1 < 0 or d2 < 0 or d3 < 0
        positif = d1 > 0 or d2 > 0 or d3 > 0
        return not (negatif and positif)

    def draw_line(
        self,
        point_debut: Point3D,
        point_fin: Point3D,
        couleur: tuple[int, int, int] = (255, 255, 255),
        largeur: int = 1,
    ) -> None:
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
        self._verifier_initialisation()

        pygame.draw.polygon(
            self.ecran,
            couleur,
            [
                (int(point1[0]), int(point1[1])),
                (int(point2[0]), int(point2[1])),
                (int(point3[0]), int(point3[1])),
            ],
        )


    def draw_entity(self, renderable: Renderable, point: Point3D, frustum: list | None) -> None:
        """
        Dessine une entité 3D sur l'écran après plusieurs étapes de culling.

        Pipeline complet :
            1. Distance culling  → trop loin ? SKIP
            2. Hi-Z culling      → caché (test grossier) ? SKIP
            3. Pixel culling     → caché (test précis) ? SKIP
            4. Frustum culling   → hors champ ? SKIP
            5. Dessin            → projection + rasterisation
            6. Mise à jour       → Hi-Z buffer + Pixel buffer

        Args:
            renderable (Renderable): Composant contenant forme, couleur, points...
            point (Point3D): Position monde de l'entité.
            frustum (list | None): Plans du frustum caméra, ou None pour désactiver.

        Returns:
            None
        """
        self._verifier_initialisation()

        cam_pos = Point3D(
            self.camera.position.x,
            self.camera.position.y,
            self.camera.position.z,
        )

        couleur  = getattr(renderable, "couleur", (255, 255, 255))
        forme    = getattr(renderable, "forme", None)
        rayon    = getattr(renderable, "rayon", 0.0)

        # ── Étape 1 : Distance culling ────────────────────────────────────────
        # Rejette les objets trop éloignés de la caméra.
        if point.distance(cam_pos) > Config.distance_culling:
            return

        # ── Étape 2 : Hi-Z culling (grossier, très rapide) ───────────────────
        # Rejette ~80% des objets cachés sans calcul coûteux.
        # ── Étape 3 : Pixel culling (précis, plus coûteux) ───────────────────
        # Rejette les objets restants cachés pixel par pixel.
        if forme != Renderable.FORME_CERCLE and not self._est_visible_pixels(point, rayon):
            self.objets_occlus += 1
            self.objets_occlus_pixels += 1
            return

        # =====================================================================
        # ── Étape 4 : Dessin selon la forme ───────────────────────────────────
        # =====================================================================

        # ── Cas 1 : Ligne ─────────────────────────────────────────────────────
        if forme == Renderable.FORME_LIGNE:
            points = getattr(renderable, "points", None)
            if not isinstance(points, (list, tuple)) or len(points) < 2:
                logger.warning("draw_entity FORME_LIGNE : 'points' invalide (%s).", points)
                return

            pts_monde = [point.add(p) for p in points]

            if frustum is not None and not self.objet_dans_frustum(frustum, pts_monde, rayon):
                return

            if self.projeter_points(pts_monde[:2]) is None:
                return

            self.draw_line(pts_monde[0], pts_monde[1], couleur)

            # ── Étape 5 : Mise à jour des buffers ────────────────────────────
            self.objets_rendus += 1
            return

        # ── Cas 2 : Polygone convexe ──────────────────────────────────────────
        if forme == Renderable.FORME_POLYGONE:
            points = getattr(renderable, "points", None)
            if not isinstance(points, (list, tuple)) or len(points) < 3:
                logger.warning("draw_entity FORME_POLYGONE : 'points' invalide (%s).", points)
                return

            pts_monde = [point.add(p) for p in points]

            if frustum is not None and not self.objet_dans_frustum(frustum, pts_monde, rayon):
                return

            projections = [self.camera.project(p) for p in pts_monde]

            if all(projections):
                for i in range(1, len(projections) - 1):
                    tri_proj = [projections[0], projections[i], projections[i + 1]]
                    self.draw_triangle(
                        (tri_proj[0].x, tri_proj[0].y),
                        (tri_proj[1].x, tri_proj[1].y),
                        (tri_proj[2].x, tri_proj[2].y),
                        couleur,
                    )
                    # ── Étape 5 : Mise à jour des buffers par triangle ────────
                    self._enregistrer_triangle_pixels(tri_proj)

                self.objets_rendus += 1
            return

        # ── Cas 3 : Cercle / Sphère ───────────────────────────────────────────
        if forme == Renderable.FORME_CERCLE:
            # Pour une sphère, un seul point + rayon suffit pour le frustum
            if frustum is not None and not self.objet_dans_frustum(frustum, [point], rayon):
                return

            segments = getattr(renderable, "segments", 16)
            anneaux  = getattr(renderable, "anneaux", 8)
            dessine  = False

            for tri in self._generer_sphere(point, rayon, segments, anneaux):
                tri_proj = [self.camera.project(p) for p in tri]

                if not all(tri_proj):
                    continue

                # Test pixel précis triangle par triangle
                if not self._tester_triangle_pixels(tri_proj):
                    continue

                self.draw_triangle(
                    (tri_proj[0].x, tri_proj[0].y),
                    (tri_proj[1].x, tri_proj[1].y),
                    (tri_proj[2].x, tri_proj[2].y),
                    couleur,
                )

                # ── Étape 5 : Mise à jour des buffers par triangle ────────────
                self._enregistrer_triangle_pixels(tri_proj)
                dessine = True

            if dessine:
                self.objets_rendus += 1
            else:
                self.objets_occlus += 1
                self.objets_occlus_pixels += 1
            return

    # ─────────────────────────────────────────────────────────────────────────

    def draw_sol(
        self,
        taille_case: float = 20.0,
        nb_cases: int = 20,
        couleur: tuple[int, int, int] = (80, 180, 80),
        frustum: list | None = None,
    ) -> None:
        """
        Dessine un sol en damier infini autour de la caméra.

        Le damier est généré dynamiquement depuis la position caméra.
        Chaque case est composée de deux triangles.
        Plus une case est éloignée, plus elle est sombre (distance shading).
        Le damier alterne entre la couleur donnée et une version plus sombre.

        Args:
            taille_case (float): Taille d'une case en unités monde. Par défaut 20.0.
            nb_cases (int): Nombre de cases dans chaque direction. Par défaut 20.
            couleur (tuple): Couleur RGB des cases paires. Par défaut vert (80,180,80).
            frustum (list | None): Plans du frustum pour le culling des cases.

        Returns:
            None
        """
        self._verifier_initialisation()

        # Couleur alternée : version plus sombre pour les cases impaires
        couleur_alternee = (
            int(couleur[0] * 0.6),
            int(couleur[1] * 0.6),
            int(couleur[2] * 0.6),
        )

        cam_x = self.camera.position.x
        cam_z = self.camera.position.z

        # Case de la caméra dans la grille
        cam_case_x = int(cam_x // taille_case)
        cam_case_z = int(cam_z // taille_case)

        distance_max = nb_cases * taille_case
        distance_max2 = distance_max * distance_max

        for ix in range(-nb_cases, nb_cases + 1):
            for iz in range(-nb_cases, nb_cases + 1):

                case_x = cam_case_x + ix
                case_z = cam_case_z + iz

                x0 = case_x * taille_case
                z0 = case_z * taille_case

                # ── Distance shading ──────────────────────────────────────────
                # Plus la case est loin, plus elle est sombre
                dx = (x0 + taille_case / 2) - cam_x
                dz = (z0 + taille_case / 2) - cam_z
                distance2 = dx * dx + dz * dz

                if distance2 > distance_max2:
                    continue

                shade = max(0.0, 1.0 - (distance2 / distance_max2))

                # Alternance des couleurs en damier
                base_couleur  = couleur if (case_x + case_z) % 2 == 0 else couleur_alternee
                couleur_case  = (
                    int(base_couleur[0] * shade),
                    int(base_couleur[1] * shade),
                    int(base_couleur[2] * shade),
                )

                # ── Définition des 4 coins de la case ─────────────────────────
                #   coin0 ── coin1
                #     |         |
                #   coin3 ── coin2
                origine = Point3D(x0, 0.0, z0)
                coins = [
                    origine,                                               # coin0 : haut-gauche
                    origine.add(Point3D(taille_case, 0.0, 0.0)),          # coin1 : haut-droit
                    origine.add(Point3D(taille_case, 0.0, taille_case)),  # coin2 : bas-droit
                    origine.add(Point3D(0.0,         0.0, taille_case)),  # coin3 : bas-gauche
                ]

                # ── Frustum culling par case ───────────────────────────────────
                # Évite de projeter des cases hors du champ de vision
                if frustum is not None and not self.objet_dans_frustum(frustum, coins, 0.0):
                    continue

                coins_2d = self.projeter_points(coins)
                if coins_2d is None:
                    continue

                # Chaque case = 2 triangles
                #   tri1 : coin0, coin1, coin2
                #   tri2 : coin0, coin2, coin3
                self.draw_triangle(coins_2d[0], coins_2d[1], coins_2d[2], couleur_case)
                self.draw_triangle(coins_2d[0], coins_2d[2], coins_2d[3], couleur_case)
