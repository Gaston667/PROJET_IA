from __future__ import annotations

import math

from src.Config import Config
from src.Rendu.Point3D import Point3D


class Camera:
    def __init__(
        self,
        largeur: int = 800,
        hauteur: int = 600,
        x: float = -90.0,
        y: float = 20.0,
        z: float = -20.0,
        yaw: float = 0.0,
        pitch: float = 0.0,
        fov: float = 90.0,
    ) -> None:
        self.position = Point3D(x, y, z)
        self.yaw = yaw
        self.pitch = pitch
        self.largeur = largeur
        self.hauteur = hauteur
        self.cx = largeur / 2
        self.cy = hauteur / 2
        self.plan_proche = 0.1
        self.plan_loin = 1000.0
        self.fov = fov
        self.cos_yaw = 0.0
        self.sin_yaw = 0.0
        self.cos_pitch = 0.0
        self.sin_pitch = 0.0
        self.distance_projection = 0.0

        self.update_cache()
        self.update_distance_projection()

    def redimensionner(self, largeur: int, hauteur: int) -> None:
        self.largeur = largeur
        self.hauteur = hauteur
        self.cx = largeur / 2
        self.cy = hauteur / 2
        self.update_distance_projection()

    def deplacer(self, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> None:
        self.position.deplacer(dx, dy, dz)

    def orienter(self, delta_yaw: float = 0.0, delta_pitch: float = 0.0) -> None:
        self.yaw += delta_yaw
        self.pitch = max(-89.0, min(89.0, self.pitch + delta_pitch))
        self.update_cache()

    def set_orientation(self, yaw: float, pitch: float) -> None:
        self.yaw = yaw
        self.pitch = max(-89.0, min(89.0, pitch))
        self.update_cache()

    def vecteur_avant(self) -> Point3D:
        return Point3D(
            self.sin_yaw * self.cos_pitch,
            self.sin_pitch,
            self.cos_yaw * self.cos_pitch,
        )

    def vecteur_droite(self) -> Point3D:
        return Point3D(self.cos_yaw, 0.0, -self.sin_yaw)

    def update_cache(self) -> None:
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)
        self.cos_yaw = math.cos(yaw_rad)
        self.sin_yaw = math.sin(yaw_rad)
        self.cos_pitch = math.cos(pitch_rad)
        self.sin_pitch = math.sin(pitch_rad)

    def update_distance_projection(self) -> None:
        fov_rad = math.radians(self.fov)
        self.distance_projection = self.hauteur / (2 * math.tan(fov_rad / 2))

    def project(self, point: Point3D) -> Point3D | None:
        point_transforme = self.vers_camera(point)
        return self.projeter(point_transforme)

    def vers_camera(self, point: Point3D) -> Point3D:
        point_transforme = self.appliquer_translation(point)
        point_transforme = self.rotation_yaw(point_transforme)
        point_transforme = self.rotation_pitch(point_transforme)
        return point_transforme

    def projeter(self, point_transforme: Point3D) -> Point3D | None:
        z = point_transforme.z
        if z <= self.plan_proche or z >= self.plan_loin:
            return None

        facteur_projection = self.distance_projection / z
        x_projete = point_transforme.x * facteur_projection
        y_projete = point_transforme.y * facteur_projection
        x_screen = self.cx + x_projete
        y_screen = self.cy - y_projete
        return Point3D(x_screen, y_screen, z)

    def appliquer_translation(self, point: Point3D) -> Point3D:
        return point.position_relative_a(self.position)

    def appliquer_tranlation(self, point: Point3D) -> Point3D:
        return self.appliquer_translation(point)

    def rotation_yaw(self, point: Point3D) -> Point3D:
        x1 = self.cos_yaw * point.x - self.sin_yaw * point.z
        z1 = self.sin_yaw * point.x + self.cos_yaw * point.z
        return Point3D(x1, point.y, z1)

    def rotation_pitch(self, point: Point3D) -> Point3D:
        y1 = self.cos_pitch * point.y - self.sin_pitch * point.z
        z2 = self.sin_pitch * point.y + self.cos_pitch * point.z
        return Point3D(point.x, y1, z2)

    def __str__(self) -> str:
        return (
            f"Camera(x={self.position.x:.2f}, y={self.position.y:.2f}, z={self.position.z:.2f}, "
            f"yaw={self.yaw:.2f}, pitch={self.pitch:.2f}, distance_projection={self.distance_projection:.2f})"
        )
