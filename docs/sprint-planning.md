# Sprint planning

## Cadence

- Duree d'un sprint : 1 semaine
- Duree totale du premier cycle : 4 semaines
- Rythme conseille :
  - Jour 1 : planification
  - Jours 2 a 4 : implementation
  - Jour 5 : tests, demo, retrospective

## Definition of Done

- Le code compile ou s'execute.
- Les tests unitaires essentiels passent.
- Le scenario cible du sprint est demonstrable.
- La documentation minimale est mise a jour.

## Sprint 1 - Socle technique

### Objectif

Obtenir une base de projet capable d'executer une simulation vide de facon reproductible.

### Stories

- Mettre en place la structure du projet.
- Definir les classes coeur de domaine.
- Implementer une boucle de simulation a pas de temps fixe.
- Ajouter la configuration de scenario.
- Ajouter des tests de base.

### Tableau de suivi

| US | Fichier | Status |
| --- | --- | --- |
| US1 | `src/simulation/simulation.py` | A faire |
| US1 | `src/application/run_scenario.py` | A faire |
| US2 | `src/domain/rocket.py` | A faire |
| US4 | `src/domain/scenario.py` | A faire |
| US1 | `tests/simulation/test_simulation.py` | A faire |

### Livrable

Une simulation qui se lance, avance dans le temps et trace les etats.

## Sprint 2 - Physique et mission A vers B

### Objectif

Faire evoluer une fusee simple dans un plan 2D jusqu'a une cible fixe.

### Stories

- Implementer le vecteur 2D et l'etat de la fusee.
- Gerer poussee, carburant, masse et vitesse.
- Ajouter les bornes de carte et les conditions d'echec.
- Ajouter la cible fixe A vers B.

### Tableau de suivi

| US | Fichier | Status |
| --- | --- | --- |
| US2 | `src/domain/vector2d.py` | A faire |
| US2 | `src/domain/rocket_state.py` | A faire |
| US2 | `src/simulation/physics_engine.py` | A faire |
| US3 | `src/simulation/collision_detector.py` | A faire |
| US4 | `src/domain/target.py` | A faire |
| US4 | `tests/simulation/test_physics_engine.py` | A faire |

### Livrable

Une fusee peut etre simulee jusqu'a une cible fixe.

## Sprint 3 - Controleur baseline et mesures

### Objectif

Avoir un pilote automatique simple qui sache atteindre des cas faciles sans IA apprenante.

### Stories

- Creer une interface de controleur.
- Implementer un controleur heuristique baseline.
- Mesurer distance finale, temps et carburant.
- Evaluer plusieurs episodes.

### Tableau de suivi

| US | Fichier | Status |
| --- | --- | --- |
| US7 | `src/control/guidance_policy.py` | A faire |
| US7 | `src/control/heuristic_controller.py` | A faire |
| US8 | `src/infrastructure/metrics_logger.py` | A faire |
| US8 | `src/application/evaluate_agent.py` | A faire |
| US7 | `tests/control/test_heuristic_controller.py` | A faire |

### Livrable

Un baseline mesurable servant de reference pour l'IA.

## Sprint 4 - Environnement IA et visualisation minimale

### Objectif

Transformer la simulation en environnement exploitable par un agent avec un premier support de debug visuel.

### Stories

- Definir observations, actions et reward.
- Definir reset, step et done.
- Ajouter la seed et la reproductibilite.
- Journaliser les episodes.
- Afficher une trajectoire simple pour debug.

### Tableau de suivi

| US | Fichier | Status |
| --- | --- | --- |
| US9 | `src/application/train_agent.py` | A faire |
| US9 | `src/simulation/environment.py` | A faire |
| US10 | `src/simulation/reward_function.py` | A faire |
| US12 | `src/presentation/trajectory_renderer.py` | A faire |
| US13 | `src/infrastructure/episode_logger.py` | A faire |
| US9 | `tests/simulation/test_environment.py` | A faire |

### Livrable

Un environnement standardisable pour entrainement avec visualisation minimale.

## Risques principaux

- Vouloir faire du 3D trop tot.
- Introduire l'IA avant d'avoir un baseline deterministe.
- Melanger moteur de simulation, affichage et logique d'apprentissage.

## Scope du cycle 4 semaines

1. Faire voler une fusee avec regles simples.
2. Faire atteindre une cible fixe.
3. Ajouter un pilote baseline.
4. Exposer l'environnement a l'IA.

## Hors scope de ce premier cycle

- Entrainement complet d'un agent performant
- Interception d'une fusee mobile
- Obstacles avances
- Passage en 3D
