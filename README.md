# Projet_AI

## Présentation
Dans ce projet, j’ai développé un environnement GridWorld personnalisé ainsi qu’un agent utilisant un algorithme d’apprentissage par renforcement. J’ai implémenté le Q-learning, un algorithme permettant à un agent d’apprendre une politique optimale grâce à l’exploration et à l’exploitation.

L’objectif de ce projet est de montrer ma capacité à concevoir et programmer un système d’intelligence artificielle complet, depuis la modélisation de l’environnement jusqu’à l’entraînement de l’agent.

## Objectifs du projet
Ce projet m’a permis de :
- implémenter moi-même l’algorithme de Q-learning ;
- concevoir un environnement d’apprentissage ;
- mettre en place un agent capable d’apprendre par essais et erreurs ;
- analyser la progression de l’agent et ajuster les hyperparamètres ;
- structurer un projet IA de manière propre et réutilisable.

## Compétences mobilisées
- Python  
- Intelligence artificielle  
- Apprentissage par renforcement (Q-learning)  
- Conception d’un environnement simulé  
- Analyse de données et optimisation  
- Organisation d’un projet logiciel

## Description technique
J’ai créé un environnement GridWorld composé d’un état initial, d’un objectif à atteindre, d’obstacles et d’un système de récompenses.  
L’agent explore cet environnement en suivant une politique ε-greedy afin de trouver un compromis entre exploration et exploitation.

J’ai implémenté l’algorithme de Q-learning, qui repose sur la mise à jour de la Q-table selon la formule :
  Q(s, a) ← Q(s, a) + α [r + γ max(Q(s'), a') – Q(s, a)]


Le projet comprend :
- la définition des états et actions ;
- la boucle d’apprentissage ;
- la mise à jour de la Q-table ;
- la gestion de l’exploration ;
- l’enregistrement et l’analyse des récompenses.

## Installation
```bash
git clone https://github.com/Gaston667/Projet_AI.git
cd Projet_AI
```

## Exécution
```bash
python main.py
```

