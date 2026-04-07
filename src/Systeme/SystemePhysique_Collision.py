from __future__ import annotations

from src.Composant import Materiau
from src.Composant.ColliderPlane import ColliderPlane
from src.Composant.Position import Position
from src.Composant.Vitesse import Vitesse
from src.Monde.Monde import Monde


class SystemePhysique_Collision:
    def __init__(self, restitution: float = 0.0) -> None:
        self.restitution = restitution

    def update(self, monde: Monde, dt: float) -> None:
        _ = dt

        plans: list[tuple[ColliderPlane, Position, Materiau | None]] = []
        mobiles: list[tuple[Position, Vitesse, Materiau | None]] = []

        for entite in monde.entites:
            position = entite.get(Position)
            if position is None:
                continue

            materiau = entite.get(Materiau)
            collider_plane = entite.get(ColliderPlane)
            if collider_plane is not None:
                plans.append((collider_plane, position, materiau))
                continue

            vitesse = entite.get(Vitesse)
            if vitesse is not None:
                mobiles.append((position, vitesse, materiau))

        for position, vitesse, materiau_mobile in mobiles:
            for collider_plane, position_plan, materiau_plan in plans:
                self._resoudre_collision_plan(
                    position,
                    vitesse,
                    collider_plane,
                    position_plan,
                    materiau_mobile,
                    materiau_plan,
                )

    def _resoudre_collision_plan(
        self,
        position: Position,
        vitesse: Vitesse,
        collider_plane: ColliderPlane,
        position_plan: Position,
        materiau_mobile: Materiau | None,
        materiau_plan: Materiau | None,
    ) -> None:
        nx = collider_plane.nx
        ny = collider_plane.ny
        nz = collider_plane.nz

        norme_carre = nx * nx + ny * ny + nz * nz
        if norme_carre <= 0.0:
            return

        offset_effectif = (
            collider_plane.offset
            + nx * position_plan.x
            + ny * position_plan.y
            + nz * position_plan.z
        )

        distance_signee = (
            nx * position.x
            + ny * position.y
            + nz * position.z
            - offset_effectif
        )

        if distance_signee >= 0.0:
            return

        correction = -distance_signee / norme_carre
        position.x += correction * nx
        position.y += correction * ny
        position.z += correction * nz

        vitesse_normale = nx * vitesse.vx + ny * vitesse.vy + nz * vitesse.vz
        if vitesse_normale >= 0.0:
            return

        restitution = self._calculer_restitution(materiau_mobile, materiau_plan)
        facteur = (1.0 + restitution) * vitesse_normale / norme_carre
        vitesse.vx -= facteur * nx
        vitesse.vy -= facteur * ny
        vitesse.vz -= facteur * nz

        friction = self._calculer_friction(materiau_mobile, materiau_plan)
        if friction <= 0.0:
            return

        projection_normale = (
            nx * vitesse.vx + ny * vitesse.vy + nz * vitesse.vz
        ) / norme_carre

        vitesse_tangentielle_x = vitesse.vx - projection_normale * nx
        vitesse_tangentielle_y = vitesse.vy - projection_normale * ny
        vitesse_tangentielle_z = vitesse.vz - projection_normale * nz

        vitesse.vx -= vitesse_tangentielle_x * friction
        vitesse.vy -= vitesse_tangentielle_y * friction
        vitesse.vz -= vitesse_tangentielle_z * friction

    def _calculer_restitution(
        self,
        materiau_mobile: Materiau | None,
        materiau_plan: Materiau | None,
    ) -> float:
        if materiau_mobile is None and materiau_plan is None:
            return self.restitution
        if materiau_mobile is None:
            return materiau_plan.restitution
        if materiau_plan is None:
            return materiau_mobile.restitution
        return (materiau_mobile.restitution + materiau_plan.restitution) * 0.5

    def _calculer_friction(
        self,
        materiau_mobile: Materiau | None,
        materiau_plan: Materiau | None,
    ) -> float:
        if materiau_mobile is None and materiau_plan is None:
            return 0.0
        if materiau_mobile is None:
            return materiau_plan.friction
        if materiau_plan is None:
            return materiau_mobile.friction
        return (materiau_mobile.friction + materiau_plan.friction) * 0.5
