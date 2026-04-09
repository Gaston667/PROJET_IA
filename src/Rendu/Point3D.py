from __future__ import annotations


class Point3D:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        self.x = x
        self.y = y
        self.z = z

    def position_relative_a(self, autre_point: Point3D) -> Point3D:
        dx = self.x - autre_point.x
        dy = self.y - autre_point.y
        dz = self.z - autre_point.z
        return Point3D(dx, dy, dz)

    def add(self, autre_point: Point3D) -> Point3D:
        return Point3D(self.x + autre_point.x, self.y + autre_point.y, self.z + autre_point.z)

    def sub(self, autre_point: Point3D) -> Point3D:
        return Point3D(self.x - autre_point.x, self.y - autre_point.y, self.z - autre_point.z)

    def distance(self, autre_point: Point3D) -> float:
        dx = self.x - autre_point.x
        dy = self.y - autre_point.y
        dz = self.z - autre_point.z
        return (dx**2 + dy**2 + dz**2) ** 0.5

    def copy(self) -> Point3D:
        return Point3D(self.x, self.y, self.z)

    def deplacer(self, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> None:
        self.x += dx
        self.y += dy
        self.z += dz

    def __str__(self) -> str:
        return f"Point3D(x={self.x:.2f}, y={self.y:.2f}, z={self.z:.2f})"
