# Mini Projet Voiture RL

Mini-projet de reinforcement learning en Python avec `pygame`.

L'agent controle une petite voiture dans un environnement visuel.
Son but est d'atteindre la zone d'arrivee sans toucher les murs.

## Ce qui a ete muscle

- plusieurs circuits selectionnables (`slalom`, `corridor`, `chicanes`)
- sauvegarde du modele par circuit
- mode turbo pour entrainer sans affichage
- mode evaluation pour mesurer les performances sans exploration
- HUD plus riche avec vitesse, etat, succes recent et recompense moyenne
- plus de capteurs et plus d'actions pour une conduite plus fine
- trace visuelle de la voiture pendant un episode

## Idee

Le projet n'utilise pas des pixels bruts pour apprendre.
A la place, la voiture observe un etat discret compose de :

- cinq capteurs de distance
- l'orientation de la voiture par rapport a la cible
- un niveau de vitesse
- un niveau de distance vers l'arrivee

L'agent utilise ensuite un Q-learning classique pour choisir une action :

- accelerer
- accelerer en tournant a gauche
- accelerer en tournant a droite
- tourner a gauche
- tourner a droite
- laisser rouler
- freiner

## Installer la dependance

```powershell
python -m pip install -r requirements.txt
```

## Lancer le projet

Depuis le dossier `mini_projet` :

```powershell
python main.py
```

Si `python` ne marche pas sur ta machine :

```powershell
C:/Users/algas/AppData/Local/Microsoft/WindowsApps/python.exe main.py
```

## Menu

- `1` entrainement rapide sur le circuit courant
- `2` entrainement personnalise
- `3` demo visuelle du modele sauvegarde
- `4` evaluation du modele sans exploration
- `5` changement de circuit
- `6` suppression du modele du circuit courant
- `7` informations du circuit courant

## Parametres a modifier

Les reglages globaux se trouvent dans `config.py` :

- physique de la voiture
- capteurs
- recompenses
- epsilon / gamma / alpha
- vitesse de simulation

Le dessin des circuits se trouve dans `env.py`, dans `DrivingEnv.TRACKS`.

## Conseils d'usage

- pour apprendre vite : utilise l'entrainement personnalise avec `render_every = 0`
- pour observer l'agent : lance la demo visuelle
- pour comparer objectivement : utilise le mode evaluation sur plusieurs circuits
