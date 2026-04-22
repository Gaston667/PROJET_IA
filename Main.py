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
from src.Outils.Profiler import Profiler
from src.Rendu.Render3D import Render3D
from src.Rendu.SystemeRendu import SystemeRendu
from src.Systeme import SystemePhysique_Collision, SystemePhysique_Mouvement
from src.Systeme.SystemePhysique_Gravite import SystemePhysique_Gravite
from src.Telemetrie import FenetreTelemetrie, HistoriqueFPS
from src.blueprints.Blueprintanceur import BlueprintLanceur
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


def creer_lanceur() -> Entite:
    """
    Crée un lanceur de missile.
    
    Véhicule lourd blindé avec tourelle.
    Propriétés :
      - Masse importante (stabilité)
      - Friction élevée (simulation chenilles/chenilles)
      - Peu de rebond (construction rigide)
    """
    bp = BlueprintLanceur
    entite = Entite()
    
    # Position et transformation
    position = Position(bp.POSITION_X, bp.POSITION_Y, bp.POSITION_Z)
    
    # Renderable - Polygone 3D du corps
    renderable = Renderable(
        couleur=bp.COULEUR,
        visible=True,
        forme=Renderable.FORME_POLYGONE,
    )
    renderable.points = bp.POINTS
    
    # Composants physiques
    masse = Masse(bp.MASSE)
    materiau = Materiau(bp.RESTITUTION, bp.FRICTION)
    vitesse = Vitesse(bp.VITESSE_X, bp.VITESSE_Y, bp.VITESSE_Z)
    force = Force(bp.FORCE_X, bp.FORCE_Y, bp.FORCE_Z)
    
    # Construction de l'entité
    entite.ajouter_composant(position)
    entite.ajouter_composant(renderable)
    entite.ajouter_composant(masse)
    entite.ajouter_composant(materiau)
    entite.ajouter_composant(vitesse)
    entite.ajouter_composant(force)
    
    # Raccourcis pour accès facile
    entite.position = position
    entite.renderable = renderable
    entite.masse = masse
    entite.materiau = materiau
    entite.vitesse = vitesse
    entite.force = force
    
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

def creer_scene_test_occlusion(monde: Monde) -> None:
    monde.ajouter_entite(creer_plan())
    monde.ajouter_entite(creer_lanceur())

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
    creer_scene_test_occlusion(monde)

    # Ajout des systèmes physiques (exécutés dans cet ordre à chaque step)
    monde.ajouter_systeme(SystemePhysique_Gravite())
    monde.ajouter_systeme(SystemePhysique_Collision()) 
    monde.ajouter_systeme(SystemePhysique_Mouvement())

    # --- Initialisation des modules ---
    simulation    = Simulation(monde)
    rendu         = Render3D(Config.largeur_fenetre, Config.hauteur_fenetre, "Test Occlusion Pixel")
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
    HistoriqueFPS().enregistrer_execution(profiler.fps_moyen(), profiler.frame_index)
    telemetrie.fermer()
    rendu.fermer()


if __name__ == "__main__":
    main()
