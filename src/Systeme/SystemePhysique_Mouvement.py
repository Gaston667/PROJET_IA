from __future__ import annotations

from src.Composant.Force import Force
from src.Composant.Masse import Masse
from src.Composant.Position import Position
from src.Composant.Vitesse import Vitesse
from src.Monde.Monde import Monde


class SystemePhysique_Mouvement:
    def update(self, monde: Monde, dt: float) -> None:
        if dt <= 0:
            return

        for entite in monde.entites:
            position = entite.get(Position)
            vitesse = entite.get(Vitesse)
            force = entite.get(Force)
            masse = entite.get(Masse)

            if position is None or vitesse is None or force is None or masse is None:
                continue

            if masse.valeur <= 0:
                continue

            
            ax = force.fx / masse.valeur
            ay = force.fy / masse.valeur
            az = force.fz / masse.valeur

            # Mise a jour de la vitesse et de la position en utilisant une integration d'Euler.
            """vitesse.vx += ax * dt
            vitesse.vy += ay * dt
            vitesse.vz += az * dt

            position.x += vitesse.vx * dt
            position.y += vitesse.vy * dt
            position.z += vitesse.vz * dt"""

            # Mise a jour de la vitesse et de la position en utilisant Verlet.
            position.x += vitesse.vx * dt + 0.5 * ax * dt * dt
            position.y += vitesse.vy * dt + 0.5 * ay * dt * dt
            position.z += vitesse.vz * dt + 0.5 * az * dt * dt

            """ pour le momment j'ai sauter recalcul des forces apres deplacement,
                nouvelle acceleration, moyeenne des accelerations, mon systeme devien faudra quand je plecerai la trainee de laire et une graviter variable et aussi une propulsion variable """

            # Calcul de l'acceleration a la nouvelle position (en supposant que les forces sont recalculées apres le mouvement).
            vitesse.vx += ax * dt
            vitesse.vy += ay * dt
            vitesse.vz += az * dt

            # Reinitialise les forces pour le prochain tour de simulation. Les forces seront recalculées par les autres systemes (comme la gravite) avant le prochain update.
            force.fx = 0.0
            force.fy = 0.0
            force.fz = 0.0
