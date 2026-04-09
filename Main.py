from src.Composant import ColliderPlane
from time import perf_counter

from src.Composant.Force import Force
from src.Composant.Masse import Masse
from src.Composant.Materiau import Materiau
from src.Composant.Position import Position
from src.Composant.Renderable import Renderable
from src.Composant.Vitesse import Vitesse
from src.Config import Config
from src.Environement.Simulation import Simulation
from src.Monde.Entite import Entite
from src.Monde.Monde import Monde
from src.Rendu.Render2D import Render2D
from src.Rendu.Render3D import Render3D
from src.Rendu.SystemeRendu import SystemeRendu
from src.Rendu.Telemetrie import FenetreTelemetrie
from src.Systeme.SystemePhysique_Collision import SystemePhysique_Collision
from src.Systeme.SystemePhysique_Gravite import SystemePhysique_Gravite
from src.Systeme.SystemePhysique_Mouvement import SystemePhysique_Mouvement
import src.blueprints as Bp



def creer_balle() -> Entite:
    balle = Entite()
    blueprint = Bp.BlueprintBalle

    position = Position(
        blueprint.POSITION_X,
        blueprint.POSITION_Y,
        blueprint.POSITION_Z,
    )
    vitesse = Vitesse(
        blueprint.VITESSE_X,
        blueprint.VITESSE_Y,
        blueprint.VITESSE_Z,
    )
    force = Force(
        blueprint.FORCE_X,
        blueprint.FORCE_Y,
        blueprint.FORCE_Z,
    )
    masse = Masse(blueprint.MASSE)
    materiau = Materiau(blueprint.RESTITUTION, blueprint.FRICTION)
    renderable = Renderable(
        couleur=(0, 0, 255),
        visible=True,
        forme="cercle",
    )

    balle.ajouter_composant(position)
    balle.ajouter_composant(vitesse)
    balle.ajouter_composant(force)
    balle.ajouter_composant(masse)
    balle.ajouter_composant(materiau)
    balle.ajouter_composant(renderable)

    balle.position = position
    balle.materiau = materiau
    balle.renderable = renderable

    return balle


def creer_plan() -> Entite:
    plan = Entite()
    blueprint = Bp.BlueprintSol

    position = Position(
        blueprint.POSITION_X,
        blueprint.POSITION_Y,
        blueprint.POSITION_Z,
    )
    collider_plane = ColliderPlane(
        blueprint.NX,
        blueprint.NY,
        blueprint.NZ,
        blueprint.OFFSET,
    )
    materiau = Materiau(blueprint.RESTITUTION, blueprint.FRICTION)
    renderable = Renderable(
        couleur=(90, 180, 90),
        visible=False,
        forme=None,
    )

    plan.ajouter_composant(position)
    plan.ajouter_composant(collider_plane)
    plan.ajouter_composant(materiau)
    plan.ajouter_composant(renderable)

    plan.position = position
    plan.collider_plane = collider_plane
    plan.materiau = materiau

    return plan

def creer_balle2() -> Entite:
    balle = Entite()
    blueprint = Bp.BlueprintBalle2

    position = Position(
        blueprint.POSITION_X,
        blueprint.POSITION_Y,
        blueprint.POSITION_Z,
    )
    vitesse = Vitesse(
        blueprint.VITESSE_X,
        blueprint.VITESSE_Y,
        blueprint.VITESSE_Z,
    )
    force = Force(
        blueprint.FORCE_X,
        blueprint.FORCE_Y,
        blueprint.FORCE_Z,
    )
    masse = Masse(blueprint.MASSE)
    materiau = Materiau(blueprint.RESTITUTION, blueprint.FRICTION)
    renderable = Renderable(
        couleur=(90, 180, 90),
        visible=True,
        forme="cercle",
    )

    balle.ajouter_composant(position)
    balle.ajouter_composant(vitesse)
    balle.ajouter_composant(force)
    balle.ajouter_composant(masse)
    balle.ajouter_composant(materiau)
    balle.ajouter_composant(renderable)

    balle.position = position
    balle.materiau = materiau
    balle.renderable = renderable

    return balle

def creer_balle4() -> Entite:
    balle = Entite()
    blueprint = Bp.BlueprintBalle4

    position = Position(
        blueprint.POSITION_X,
        blueprint.POSITION_Y,
        blueprint.POSITION_Z,
    )
    vitesse = Vitesse(
        blueprint.VITESSE_X,
        blueprint.VITESSE_Y,
        blueprint.VITESSE_Z,
    )
    force = Force(
        blueprint.FORCE_X,
        blueprint.FORCE_Y,
        blueprint.FORCE_Z,
    )
    masse = Masse(blueprint.MASSE)
    materiau = Materiau(blueprint.RESTITUTION, blueprint.FRICTION)
    renderable = Renderable(
        couleur=(255, 255, 0),
        visible=True,
        forme="cercle",
    )

    balle.ajouter_composant(position)
    balle.ajouter_composant(vitesse)
    balle.ajouter_composant(force)
    balle.ajouter_composant(masse)
    balle.ajouter_composant(materiau)
    balle.ajouter_composant(renderable)

    balle.position = position
    balle.materiau = materiau
    balle.renderable = renderable

    return balle


def main() -> None:
    monde = Monde()
    monde.ajouter_entite(creer_balle())
    monde.ajouter_entite(creer_plan())
    monde.ajouter_entite(creer_balle2())
    monde.ajouter_entite(creer_balle4())

    monde.ajouter_systeme(SystemePhysique_Gravite())
    monde.ajouter_systeme(SystemePhysique_Mouvement())
    monde.ajouter_systeme(SystemePhysique_Collision())

    simulation = Simulation(monde)
    #rendu = Render2D(800, 600, "Test balle")
    rendu = Render3D(900, 700, "Test balle 3D")
    systeme_rendu = SystemeRendu(rendu)
    telemetrie = FenetreTelemetrie()

    rendu.initialiser()

    en_cours = True
    accumulateur = 0.0
    monde.accumulateur = accumulateur
    temps_precedent = perf_counter()
    while en_cours and not simulation.est_terminee():
        temps_actuel = perf_counter()
        frame_time = min(temps_actuel - temps_precedent, Config.max_frame_time)
        temps_precedent = temps_actuel
        accumulateur += frame_time

        en_cours = rendu.gerer_evenements()
        while accumulateur >= Config.delta_t and en_cours and not simulation.est_terminee():
            simulation.step(Config.delta_t)
            accumulateur -= Config.delta_t

        monde.accumulateur = accumulateur

        if not en_cours:
            break

        systeme_rendu.render(monde)
        telemetrie.mettre_a_jour(monde, rendu)

    telemetrie.fermer()
    rendu.fermer()


if __name__ == "__main__":
    main()


