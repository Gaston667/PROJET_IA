from __future__ import annotations

import math


class Atmosphere:
    # Constantes de l'atmosphere standard.
    G0 = 9.80665
    R = 287.05287

    def __init__(self) -> None:
        # Couches principales de l'U.S. Standard Atmosphere 1976:
        # (altitude de base, temperature de base, pression de base, gradient thermique)
        self.couches = [
            (0.0, 288.15, 101325.0, -0.0065),
            (11000.0, 216.65, 22632.06, 0.0),
            (20000.0, 216.65, 5474.889, 0.001),
            (32000.0, 228.65, 868.0187, 0.0028),
            (47000.0, 270.65, 110.9063, 0.0),
            (51000.0, 270.65, 66.93887, -0.0028),
            (71000.0, 214.65, 3.956420, -0.002),
        ]

    def _trouver_couche(self, altitude: float):
        # On borne l'altitude a 0 pour eviter un comportement non physique sous le niveau de reference.
        altitude = max(0.0, altitude)
        couche = self.couches[0]

        # On prend la derniere couche dont l'altitude de base est inferieure ou egale a l'altitude demandee.
        for candidate in self.couches:
            if altitude >= candidate[0]:
                couche = candidate
            else:
                break

        return couche

    def pression(self, altitude: float) -> float:
        altitude = max(0.0, altitude)
        hb, tb, pb, gradient = self._trouver_couche(altitude)

        # Cas isotherme: temperature constante dans la couche.
        if gradient == 0.0:
            exponent = (-self.G0 * (altitude - hb)) / (self.R * tb)
            return pb * math.exp(exponent)

        # Cas general: temperature qui varie lineairement avec l'altitude.
        temperature = tb + gradient * (altitude - hb)
        exponent = -self.G0 / (gradient * self.R)
        return pb * (temperature / tb) ** exponent
