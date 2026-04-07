from __future__ import annotations

import math

from src.Composant.Force import Force
from src.Composant.Masse import Masse
from src.Composant.Moteur import Moteur
from src.Composant.Position import Position
from src.Monde.Monde import Monde
from src.Systeme.Atmosphere import Atmosphere


class SystemePhysique_Propulsion:
    def __init__(self, atmosphere: Atmosphere | None = None) -> None:
        # Atmosphère utilisée pour calculer la poussée dépendante de la pression
        self.atmosphere = atmosphere if atmosphere is not None else Atmosphere()

    def update(self, monde: Monde, dt: float) -> None:
        # dt doit être strictement positif pour avancer la simulation
        if dt <= 0:
            return

        for entite in monde.entites:
            # Ne traiter que les entités avec moteur, force, masse et position
            if not (
                entite.a(Moteur)
                and entite.a(Force)
                and entite.a(Masse)
                and entite.a(Position)
            ):
                continue

            moteur = entite.get(Moteur)
            force = entite.get(Force)
            masse = entite.get(Masse)
            position = entite.get(Position)

            if moteur is None or force is None or masse is None or position is None:
                continue

            # La masse doit être positive pour que la propulsion soit valide
            if masse.valeur <= 0.0:
                continue

            # Clamp du throttle entre 0 et 1
            throttle = max(0.0, min(1.0, moteur.throttle))
            if throttle == 0.0:
                moteur.thrust = 0.0
                continue

            # Calcul de la pression ambiante en fonction de l'altitude
            altitude = position.y
            pression_ambiante = self.atmosphere.pression(altitude)

            # Paramètres moteur ajustés par le throttle qui est la vitesse de poussée
            debit_massique = moteur.debit_massique * throttle
            vitesse_ejection = moteur.vitesse_ejection
            pression_sortie = moteur.pression_sortie
            surface_sortie = moteur.surface_sortie

            # Poussée = débit massique * vitesse d'éjection + correction pression
            poussee = debit_massique * vitesse_ejection + surface_sortie * (pression_sortie - pression_ambiante)
            poussee = max(0.0, poussee)
            moteur.thrust = poussee

            # Direction de la poussée à partir de l'orientation du moteur
            angle_rad = math.radians(moteur.orientation)
            direction_x = math.cos(angle_rad)
            direction_y = math.sin(angle_rad)

            # Application de la force au composant Force
            force.fx += poussee * direction_x
            force.fy += poussee * direction_y

            # Consommation de masse du réservoir
            masse.valeur -= debit_massique * dt
            if masse.valeur < 0.0:
                masse.valeur = 0.0
