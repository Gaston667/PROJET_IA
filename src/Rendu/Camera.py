from __future__ import annotations

import math

from src import Config
from src.Rendu.Point3D import Point3D


class Camera:
    """
    Caméra 3D perspective utilisée pour projeter des points 3D en 2D.

    La caméra supporte les rotations yaw (horizontal) et pitch (vertical),
    le déplacement dans l'espace, et la projection perspective avec plan
    proche et plan lointain.

    Attributes:
        position (Point3D): Position de la caméra dans l'espace monde.
        yaw (float): Rotation horizontale en degrés.
        pitch (float): Rotation verticale en degrés, clampée à [-89, 89].
        largeur (int): Largeur de la fenêtre en pixels.
        hauteur (int): Hauteur de la fenêtre en pixels.
        fov (float): Champ de vision en degrés.
        plan_proche (float): Distance minimale de projection.
        plan_loin (float): Distance maximale de projection.

    Example:
        >>> cam = Camera(800, 600, x=0, y=5, z=-10)
        >>> point_2d = cam.project(Point3D(0, 0, 10))
    """

    PITCH_MIN = -89.0
    PITCH_MAX = 89.0

    def __init__(
        self,
        largeur: int = 800,
        hauteur: int = 600,
        x: float = -90.0,
        y: float = 20.0,
        z: float = -20.0,
        yaw: float = 0.0,
        pitch: float = 0.0,
        fov: float = Config.fov,
        plan_proche: float = Config.near_plane,
        plan_loin: float = Config.far_plane,
    ) -> None:
        """
        Initialise la caméra.

        Args:
            largeur (int): Largeur de la fenêtre en pixels.
            hauteur (int): Hauteur de la fenêtre en pixels.
            x (float): Position initiale X.
            y (float): Position initiale Y.
            z (float): Position initiale Z.
            yaw (float): Rotation horizontale initiale en degrés.
            pitch (float): Rotation verticale initiale en degrés.
            fov (float): Champ de vision en degrés.
            plan_proche (float): Distance minimale de projection.
            plan_loin (float): Distance maximale de projection.
        """
        self.position = Point3D(x, y, z)
        self.yaw = yaw
        self.pitch = pitch
        self.largeur = largeur
        self.hauteur = hauteur
        self.fov = fov
        self.plan_proche = plan_proche
        self.plan_loin = plan_loin

        # Centre de l'écran (mis à jour si redimensionnement)
        self.cx = largeur / 2.0
        self.cy = hauteur / 2.0

        # Cache trigonométrique (recalculé à chaque changement d'orientation)
        self._cos_yaw = 0.0
        self._sin_yaw = 0.0
        self._cos_pitch = 0.0
        self._sin_pitch = 0.0

        # Distance de projection (recalculée si fov ou hauteur changent)
        self._distance_projection = 0.0

        self._update_cache()
        self._update_distance_projection()

    # =========================================================================
    # SECTION 1 : Mise à jour interne
    # =========================================================================

    def _update_cache(self) -> None:
        """Recalcule le cache trigonométrique après un changement d'orientation."""
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)
        self._cos_yaw = math.cos(yaw_rad)
        self._sin_yaw = math.sin(yaw_rad)
        self._cos_pitch = math.cos(pitch_rad)
        self._sin_pitch = math.sin(pitch_rad)

    def _update_distance_projection(self) -> None:
        """Recalcule la distance de projection selon le FOV et la hauteur."""
        fov_rad = math.radians(self.fov)
        self._distance_projection = self.hauteur / (2.0 * math.tan(fov_rad / 2.0))

    # =========================================================================
    # SECTION 2 : Déplacement et orientation
    # =========================================================================

    def deplacer(self, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> None:
        """
        Déplace la caméra dans l'espace monde.

        Args:
            dx (float): Déplacement sur l'axe X.
            dy (float): Déplacement sur l'axe Y.
            dz (float): Déplacement sur l'axe Z.
        """
        self.position.deplacer(dx, dy, dz)

    def orienter(self, delta_yaw: float = 0.0, delta_pitch: float = 0.0) -> None:
        """
        Modifie l'orientation de la caméra par des deltas.

        Args:
            delta_yaw (float): Variation de rotation horizontale en degrés.
            delta_pitch (float): Variation de rotation verticale en degrés.
        """
        self.yaw += delta_yaw
        self.pitch = max(self.PITCH_MIN, min(self.PITCH_MAX, self.pitch + delta_pitch))
        self._update_cache()

    def set_orientation(self, yaw: float, pitch: float) -> None:
        """
        Définit l'orientation absolue de la caméra.

        Args:
            yaw (float): Rotation horizontale en degrés.
            pitch (float): Rotation verticale en degrés.
        """
        self.yaw = yaw
        self.pitch = max(self.PITCH_MIN, min(self.PITCH_MAX, pitch))
        self._update_cache()

    def redimensionner(self, largeur: int, hauteur: int) -> None:
        """
        Met à jour la résolution de la caméra après redimensionnement.

        Args:
            largeur (int): Nouvelle largeur en pixels.
            hauteur (int): Nouvelle hauteur en pixels.
        """
        self.largeur = largeur
        self.hauteur = hauteur
        self.cx = largeur / 2.0
        self.cy = hauteur / 2.0
        self._update_distance_projection()

    # =========================================================================
    # SECTION 3 : Vecteurs directionnels
    # =========================================================================

    def vecteur_avant(self) -> Point3D:
        """
        Retourne le vecteur unitaire pointant vers l'avant de la caméra.

        Returns:
            Point3D: Vecteur avant dans l'espace monde.
        """
        return Point3D(
            self._sin_yaw * self._cos_pitch,
            self._sin_pitch,
            self._cos_yaw * self._cos_pitch,
        )

    def vecteur_droite(self) -> Point3D:
        """
        Retourne le vecteur unitaire pointant vers la droite de la caméra.

        Returns:
            Point3D: Vecteur droite dans l'espace monde.
        """
        return Point3D(self._cos_yaw, 0.0, -self._sin_yaw)
    
    def vecteur_haut(self) -> Point3D:
        """
        Retourne le vecteur unitaire pointant vers le haut de la caméra.

        Returns:
            Point3D: Vecteur haut dans l'espace monde.
        """
        return Point3D(
            -self._sin_pitch * self._sin_yaw,
            self._cos_pitch,
            -self._sin_pitch * self._cos_yaw,
        )





    # =========================================================================
    # SECTION 4 : Projection
    # =========================================================================

    def project(self, point: Point3D) -> Point3D | None:
        """
        Projette un point 3D monde en coordonnées écran 2D.

        Args:
            point (Point3D): Point dans l'espace monde.

        Returns:
            Point3D | None: Point projeté (x, y = écran, z = profondeur),
                ou None si le point est hors des plans proche/lointain.
        """
        point_camera = self._vers_espace_camera(point)
        return self._projeter(point_camera)

    def _vers_espace_camera(self, point: Point3D) -> Point3D:
        """
        Transforme un point monde en espace caméra (translation + rotations).

        Args:
            point (Point3D): Point dans l'espace monde.

        Returns:
            Point3D: Point dans l'espace caméra.
        """
        # Translation : position relative à la caméra
        p = point.position_relative_a(self.position)

        # Rotation yaw (axe Y)
        x1 = self._cos_yaw * p.x - self._sin_yaw * p.z
        z1 = self._sin_yaw * p.x + self._cos_yaw * p.z

        # Rotation pitch (axe X)
        y2 = self._cos_pitch * p.y - self._sin_pitch * z1
        z2 = self._sin_pitch * p.y + self._cos_pitch * z1

        return Point3D(x1, y2, z2)

    def _projeter(self, point: Point3D) -> Point3D | None:
        """
        Applique la projection perspective sur un point en espace caméra.

        Args:
            point (Point3D): Point dans l'espace caméra.

        Returns:
            Point3D | None: Coordonnées écran, ou None si hors champ.
        """
        z = point.z

        if z <= self.plan_proche or z >= self.plan_loin:
            return None

        facteur = self._distance_projection / z
        x_screen = self.cx + point.x * facteur
        y_screen = self.cy - point.y * facteur

        return Point3D(x_screen, y_screen, z)

    # =========================================================================
    # SECTION 5 : Affichage
    # =========================================================================

    def __str__(self) -> str:
        return (
            f"Camera("
            f"x={self.position.x:.2f}, "
            f"y={self.position.y:.2f}, "
            f"z={self.position.z:.2f}, "
            f"yaw={self.yaw:.2f}, "
            f"pitch={self.pitch:.2f}, "
            f"fov={self.fov:.1f}, "
            f"dist_proj={self._distance_projection:.2f}"
            f")"
        )

    def __repr__(self) -> str:
        return (
            f"Camera(largeur={self.largeur}, hauteur={self.hauteur}, "
            f"x={self.position.x}, y={self.position.y}, z={self.position.z}, "
            f"yaw={self.yaw}, pitch={self.pitch}, fov={self.fov})"
        )
