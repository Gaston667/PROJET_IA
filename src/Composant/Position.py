from __future__ import annotations

from src.Rendu.Point3D import Point3D


class Position(Point3D):
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        super().__init__(x, y, z)
