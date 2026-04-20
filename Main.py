# =============================================================================
# POINT D'ENTRÉE DE LA SIMULATION
# =============================================================================
# Ce fichier orchestre tous les systèmes :
#   - Le monde (contient les entités)
#   - La simulation (fait avancer la physique)
#   - Le rendu (affiche les entités à l'écran)
#   - La télémétrie (fenêtre de debug/stats)
# =============================================================================

from __future__ import annotations

from time import perf_counter

from src.Composant.ColliderPlane import ColliderPlane
from src.Composant.Materiau import Materiau
from src.Composant.Position import Position
from src.Composant.Renderable import Renderable
from src.Config import Config
from src.Environement.Simulation import Simulation
from src.Monde.Entite import Entite
from src.Monde.Monde import Monde
from src.Outils.Profiler import Profiler
from src.Rendu.Point3D import Point3D
from src.Rendu.Render3D import Render3D
from src.Rendu.SystemeRendu import SystemeRendu
from src.Rendu.Telemetrie import FenetreTelemetrie
from src.blueprints.BlueprintSol import BlueprintSol


# =============================================================================
# FABRIQUES D'ENTITÉS
# =============================================================================
# Chaque fonction "creer_xxx()" construit une entité complète.
# Une entité = un objet du monde, composé de plusieurs composants.
#
# Composants disponibles :
#   - Position   : où est l'objet dans l'espace 3D
#   - Vitesse    : vecteur de déplacement par seconde
#   - Force      : forces appliquées (gravité, impulsions...)
#   - Masse      : influence la physique (F = ma)
#   - Materiau   : restitution (rebond) et friction
#   - Renderable : comment l'objet est affiché (forme, couleur, taille)
#   - ColliderPlane : plan de collision infini (sol, mur...)
# =============================================================================


def creer_sphere_test(
    x: float,
    y: float,
    z: float,
    rayon: float,
    couleur: tuple[int, int, int],
) -> Entite:
    entite = Entite()
    position = Position(x, y, z)
    renderable = Renderable(
        couleur=couleur,
        visible=True,
        forme=Renderable.FORME_CERCLE,
        rayon=rayon,
        segments=24,
        anneaux=12,
    )

    entite.ajouter_composant(position)
    entite.ajouter_composant(renderable)

    entite.position = position
    entite.renderable = renderable

    return entite


def creer_panneau_occlusion() -> Entite:
    entite = Entite()
    position = Position(20.0, 10.0, -55.0)
    renderable = Renderable(
        couleur=(45, 95, 210),
        visible=True,
        forme=Renderable.FORME_POLYGONE,
        rayon=24.0,
    )
    renderable.points = [
        Point3D(-18.0, -12.0, 0.0),
        Point3D(18.0, -12.0, 0.0),
        Point3D(18.0, 12.0, 0.0),
        Point3D(-18.0, 12.0, 0.0),
    ]

    entite.ajouter_composant(position)
    entite.ajouter_composant(renderable)

    entite.position = position
    entite.renderable = renderable

    return entite


def creer_plan() -> Entite:
    """
    Crée le sol (plan de collision infini).
    
    Un ColliderPlane est défini par :
      - une normale (NX, NY, NZ) : direction perpendiculaire au plan
      - un offset : distance du plan par rapport à l'origine
    
    Exemple : normale (0, 1, 0) + offset 0 = sol horizontal à y=0
    
    Le rendu est désactivé (visible=False) car le sol
    est dessiné séparément via draw_sol() (damier dynamique).
    """
    plan = Entite()
    bp = BlueprintSol

    position       = Position(bp.POSITION_X, bp.POSITION_Y, bp.POSITION_Z)
    collider_plane = ColliderPlane(bp.NX, bp.NY, bp.NZ, bp.OFFSET)
    materiau       = Materiau(bp.RESTITUTION, bp.FRICTION)

    # visible=False → le plan n'est pas rendu comme entité
    renderable = Renderable(visible=False, forme=bp.FORME)

    plan.ajouter_composant(position)
    plan.ajouter_composant(collider_plane)
    plan.ajouter_composant(materiau)
    plan.ajouter_composant(renderable)

    plan.position      = position
    plan.collider_plane = collider_plane
    plan.materiau      = materiau

    return plan


def creer_objet_demo() -> Entite:
    """
    Objet de démonstration : un polygone 3D (quadrilatère).
    
    Contrairement aux balles (FORME_CERCLE), un polygone est défini
    par une liste de sommets 3D (renderable.points).
    
    Ces points sont en coordonnées LOCALES (relatives à la position).
    Le renderer les translate selon la position de l'entité au moment du rendu.
    """
    objet = Entite()

    position = Position(0.0, 2.0, 35.0)

    renderable = Renderable(
        couleur=(255, 120, 40),
        visible=True,
        forme=Renderable.FORME_POLYGONE,
    )

    # Les 4 sommets du polygone en coordonnées locales
    renderable.points = [
        Point3D(-4.0, 0.0, 0.0),
        Point3D( 4.0, 0.0, 0.0),
        Point3D( 3.0, 4.0, 6.0),
        Point3D(-3.0, 4.0, 6.0),
    ]

    objet.ajouter_composant(position)
    objet.ajouter_composant(renderable)

    objet.position   = position
    objet.renderable = renderable

    return objet


# =============================================================================
# BOUCLE PRINCIPALE
# =============================================================================

def main() -> None:
    """
    Point d'entrée de la simulation.

    Architecture générale :
    ┌─────────────────────────────────────────────────┐
    │  Monde                                          │
    │  ├── Entités (balles, sol, objets...)           │
    │  └── Systèmes (gravité, mouvement, collision)   │
    │                                                 │
    │  Simulation  → appelle les systèmes à chaque dt │
    │  Render3D    → affiche le monde en 3D           │
    │  SystemeRendu→ fait le lien Monde ↔ Render3D    │
    │  Telemetrie  → fenêtre de stats/debug           │
    └─────────────────────────────────────────────────┘
    """

    # --- Construction du monde ---
    monde = Monde()
    profiler = Profiler()

    # Ajout des entités
    monde.ajouter_entite(creer_plan())
    monde.ajouter_entite(creer_panneau_occlusion())
    monde.ajouter_entite(creer_sphere_test(20.0, 10.0, 15.0, 4.0, (255, 60, 60)))
    monde.ajouter_entite(creer_sphere_test(20.0, 2.0, 25.0, 3.0, (255, 180, 60)))
    monde.ajouter_entite(creer_sphere_test(180.0, 10.0, 20.0, 4.0, (80, 255, 120)))
    monde.ajouter_entite(creer_sphere_test(-140.0, 10.0, 20.0, 4.0, (80, 255, 255)))

    # Ajout des systèmes physiques (exécutés dans cet ordre à chaque step)

    # --- Initialisation des modules ---
    simulation    = Simulation(monde)
    rendu         = Render3D(Config.largeur_fenetre, Config.hauteur_fenetre, "Simulation 3D")
    systeme_rendu = SystemeRendu(rendu)

    rendu.initialiser()  # Crée la fenêtre pygame
    telemetrie    = FenetreTelemetrie(profiler)

    # --- Boucle de jeu avec pas de temps fixe (Fixed Timestep) ---
    #
    # Principe :
    #   La physique tourne à un pas fixe (Config.delta_t, ex: 1/60 s).
    #   Le rendu tourne aussi vite que possible.
    #   Un "accumulateur" stocke le temps écoulé non encore simulé.
    #
    #   Chaque frame :
    #     accumulateur += temps_ecoule_depuis_derniere_frame
    #     tant que accumulateur >= delta_t :
    #         simuler un step
    #         accumulateur -= delta_t
    #     afficher
    #
    #   Avantage : la physique est stable et indépendante du FPS.

    en_cours        = True
    accumulateur    = 0.0
    temps_precedent = perf_counter()

    while en_cours and not simulation.est_terminee():
        profiler.debut_frame()

        # --- Mesure du temps écoulé depuis la dernière frame ---
        temps_actuel = perf_counter()
        frame_time   = temps_actuel - temps_precedent
        temps_precedent = temps_actuel

        # Sécurité : si le PC rame (ex: breakpoint), on plafonne le frame_time
        # pour éviter une avalanche de steps physiques d'un coup
        frame_time = min(frame_time, Config.max_frame_time)

        accumulateur += frame_time

        # --- Gestion des événements clavier/souris/fermeture ---
        with profiler.mesurer("evenements"):
            en_cours = rendu.gerer_evenements()
        if not en_cours:
            profiler.fin_frame()
            break

        # --- Steps physiques (autant que nécessaire pour rattraper le temps) ---
        with profiler.mesurer("physique"):
            while accumulateur >= Config.delta_t and not simulation.est_terminee():
                simulation.step(Config.delta_t)
                accumulateur -= Config.delta_t

        # Partage l'accumulateur avec le monde (utile pour l'interpolation future)
        monde.accumulateur = accumulateur

        # --- Rendu de la frame ---
        with profiler.mesurer("rendu"):
            systeme_rendu.render(monde)

        # --- Mise à jour de la fenêtre de télémétrie (stats, debug) ---
        with profiler.mesurer("telemetrie"):
            telemetrie.mettre_a_jour(monde, rendu, profiler)

        profiler.fin_frame()

    # --- Nettoyage ---
    telemetrie.fermer()
    rendu.fermer()


if __name__ == "__main__":
    main()
