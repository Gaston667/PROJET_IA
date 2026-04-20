from __future__ import annotations
import math


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

    
    def decaler(self, direction: Point3D, distance: float) -> Point3D:
        """
        Retourne un nouveau point décalé dans une direction donnée.

        Args:
            direction (Point3D): Vecteur de direction (Normalisé c'est a dire unitaire).
            distance (float): Distance à parcourir dans cette direction. (Distance decalage)

        Returns:
            Point3D: Nouveau point décalé.
        """
        return Point3D(
            self.x + direction.x * distance,
            self.y + direction.y * distance,
            self.z + direction.z * distance,
        )
    

    def combiner(self, autre: Point3D, facteur: float) -> Point3D:
        """
        Combine deux vecteurs : self + autre * facteur.
                              en multipliant l'un des deux par un facteur.

        Args:
            autre   : Vecteur à ajouter.
            facteur : Poids du second vecteur.

        Returns:
            Point3D: self + autre * facteur
        """

        return Point3D(
            self.x + autre.x * facteur,
            self.y + autre.y * facteur,
            self.z + autre.z * facteur,
        )
    
    def normaliser(self) -> Point3D:
        """
            Normalise le vecteur pour qu'est une longueur de 1.

        Returns:
            Point3D: Vecteur unitaire.
        """

        longueur = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        return Point3D(self.x/longueur, self.y / longueur, self.z / longueur,)

    def inverser(self) -> Point3D:
        """
        Inverse le vecteur (pointant dans la direction opposée).

        Returns:
            Point3D: Vecteur inversé.
        """
        return Point3D(-self.x, -self.y, -self.z)
    
    def __str__(self) -> str:
        return f"Point3D(x={self.x:.2f}, y={self.y:.2f}, z={self.z:.2f})"

    