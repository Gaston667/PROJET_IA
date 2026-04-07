from __future__ import annotations

import math

from src.Config import Config


class Camera:
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = -10.0,
        yaw: float = 0.0,
        pitch: float = 0.0,
    ) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.pitch = pitch
        self.pixels_par_metre = Config.pixels_par_metre

    def deplacer(self, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> None:
        self.x += dx
        self.y += dy
        self.z += dz

        

    def position(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)

    # On limite le pitch pour eviter que la camera se retourne completement.
    def orienter(self, delta_yaw: float = 0.0, delta_pitch: float = 0.0) -> None:
        self.yaw += delta_yaw
        self.pitch += delta_pitch
        self.pitch = max(-89.0, min(89.0, self.pitch))

    # Le vecteur avant est la direction dans laquelle la camera regarde.
    def vecteur_avant(self) -> tuple[float, float, float]:
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)
        cos_pitch = math.cos(pitch_rad)
        return (
            math.sin(yaw_rad) * cos_pitch,
            math.sin(pitch_rad),
            math.cos(yaw_rad) * cos_pitch,
        )

    # Le vecteur de droite est perpendiculaire au vecteur avant et au vecteur up (0, 1, 0).
    def vecteur_droite(self) -> tuple[float, float, float]:
        yaw_rad = math.radians(self.yaw)
        return (
            math.cos(yaw_rad),
            0.0,
            -math.sin(yaw_rad),
        )

    # On exprime le point dans le repere local de la camera avant la projection.
    def vers_camera(self, x: float, y: float, z: float) -> tuple[float, float, float]:
        dx = x - self.x
        dy = y - self.y
        dz = z - self.z

        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)
        cos_yaw = math.cos(yaw_rad)
        sin_yaw = math.sin(yaw_rad)
        cos_pitch = math.cos(pitch_rad)
        sin_pitch = math.sin(pitch_rad)

        # On exprime le point dans le repere local de la camera avant la projection.
        x_camera = cos_yaw * dx - sin_yaw * dz
        z_apres_yaw = sin_yaw * dx + cos_yaw * dz
        y_camera = cos_pitch * dy - sin_pitch * z_apres_yaw
        z_camera = sin_pitch * dy + cos_pitch * z_apres_yaw
        return (x_camera, y_camera, z_camera)

    # On projette le point dans le plan de projection pour obtenir les coordonnees ecran.
    def projeter_camera(
        self,
        x_camera: float,
        y_camera: float,
        z_camera: float,
        largeur_ecran: int,
        hauteur_ecran: int,
        distance_projection: float,
    ) -> tuple[int, int] | None:
        if z_camera <= 0:
            return None

        # Plus z_camera est grand, plus l'objet parait loin donc petit.
        facteur = distance_projection / z_camera
        x_ecran = int(largeur_ecran / 2 + x_camera * facteur)
        y_ecran = int(hauteur_ecran / 2 - y_camera * facteur)
        return (x_ecran, y_ecran)

    # Cette methode combine les deux et peut etre utilisee pour les objets statiques sans orientation.
    def conversion(
        self,
        x: float,
        y: float,
        z: float,
        largeur_ecran: int,
        hauteur_ecran: int,
        distance_projection: float | None = None,
    ) -> tuple[int, int] | None:
        if distance_projection is None:
            x_ecran = int(largeur_ecran / 2 + (x - self.x) * self.pixels_par_metre)
            y_ecran = int(hauteur_ecran / 2 - (y - self.y) * self.pixels_par_metre)
            return (x_ecran, y_ecran)

        x_camera, y_camera, z_camera = self.vers_camera(x, y, z)
        return self.projeter_camera(
            x_camera,
            y_camera,
            z_camera,
            largeur_ecran,
            hauteur_ecran,
            distance_projection,
        )

    def __str__(self) -> str:
        return (
            f"Camera(x={self.x}, y={self.y}, z={self.z}, "
            f"yaw={self.yaw}, pitch={self.pitch}, "
            f"pixels_par_metre={self.pixels_par_metre})"
        )
