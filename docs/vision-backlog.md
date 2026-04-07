# Vision produit

## Objectif

Construire un agent IA capable de piloter une fusee dans un environnement simule.

Le produit sera developpe en deux etapes :

1. Navigation : aller d'un point A a un point B.
2. Interception : atteindre une autre fusee mobile.

## Hypotheses de depart

- Le MVP commence en 2D pour reduire la complexite.
- On se concentre d'abord sur une physique simple mais stable.
- Une politique de controle classique sert de baseline avant l'IA apprenante.
- L'entrainement IA arrive apres validation de la simulation.

## Utilisateur cible

- Developpeur : veut construire un moteur de simulation testable et un environnement exploitable par une IA.

## Product backlog

### Epic 1 - Socle simulation

**US1 - En tant que developpeur, je veux une boucle de simulation stable pour executer des scenarios reproductibles**

- Critere d'acceptation : la simulation avance par pas de temps fixes.
- Critere d'acceptation : une seed permet de reproduire les resultats.

**US2 - En tant que developpeur, je veux un modele de fusee avec position, vitesse, acceleration et carburant**

- Critere d'acceptation : l'etat de la fusee est serialisable.
- Critere d'acceptation : les commandes de poussee modifient l'etat de facon coherente.

**US3 - En tant que developpeur, je veux un moteur de collision pour detecter succes, echec et interception**

- Critere d'acceptation : collision cible detectee.
- Critere d'acceptation : sortie de zone detectee.
- Critere d'acceptation : crash detecte.

### Epic 2 - Environnement de mission

**US4 - En tant que developpeur, je veux definir un point de depart et un point d'arrivee pour parametrer une mission**

- Critere d'acceptation : un scenario charge A, B et les contraintes.

**US5 - En tant que developpeur, je veux des scenarios parametrables pour tester plusieurs conditions de mission**

- Critere d'acceptation : vitesse initiale, masse, carburant, taille de carte et cible sont configurables.

**US6 - En tant que developpeur, je veux ajouter des obstacles ou zones interdites pour enrichir la simulation**

- Critere d'acceptation : les collisions ou penalites sont appliquees.

### Epic 3 - Pilotage et baseline

**US7 - En tant que developpeur, je veux un pilote baseline non IA pour disposer d'une reference de controle**

- Critere d'acceptation : un controleur heuristique atteint la cible dans des cas simples.

**US8 - En tant que developpeur, je veux comparer plusieurs strategies de guidage pour evaluer leur efficacite**

- Critere d'acceptation : les resultats sont journalises par episode.

### Epic 4 - IA et apprentissage

**US9 - En tant que developpeur, je veux exposer l'etat de l'environnement a un agent IA**

- Critere d'acceptation : observations, actions, reward et done sont definis.

**US10 - En tant que developpeur, je veux une fonction de recompense pour apprendre a atteindre une cible**

- Critere d'acceptation : bonus de succes, penalite de crash, penalite de temps et de consommation.

**US11 - En tant que developpeur, je veux lancer un entrainement automatique pour produire un premier modele**

- Critere d'acceptation : un script demarre N episodes et sauve les metriques.

### Epic 5 - Visualisation et analyse

**US12 - En tant que developpeur, je veux visualiser la trajectoire pour comprendre le comportement de l'agent**

- Critere d'acceptation : la fusee, la cible et la trajectoire sont affichees.

**US13 - En tant que developpeur, je veux enregistrer les statistiques d'une simulation**

- Critere d'acceptation : distance finale, temps, carburant et resultat sont exportes.

### Epic 6 - Interception fusee contre fusee

**US14 - En tant que developpeur, je veux simuler une cible mobile pour preparer le mode interception**

- Critere d'acceptation : la cible suit une trajectoire propre.

**US15 - En tant que developpeur, je veux entrainer un agent a intercepter une fusee**

- Critere d'acceptation : la mission d'interception est disponible avec ses metriques.

## Priorisation

### Must have

- Boucle de simulation
- Modele physique minimal
- Scenario A vers B
- Controleur baseline
- API environnement pour l'IA
- Visualisation simple

### Should have

- Obstacles
- Metriques et rejouabilite
- Entrainement automatise

### Could have

- Multi-fusees
- Bruit capteurs
- Vent ou gravite variable
- Mode 3D
