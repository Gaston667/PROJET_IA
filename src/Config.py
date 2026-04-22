from __future__ import annotations


class Config:
    # Acceleration due a la gravite (m/s^2).
    gravite: float = 9.81

    # Frequence cible du rendu.
    fps: int = 60

    # Pas de temps fixe de la physique (s).
    delta_t: float = 1.0 / 60.0

    # Temps reel maximum absorbe par frame pour eviter un gros rattrapage.
    max_frame_time: float = 0.25

    # Duree maximale de la simulation (s).
    max_simulation_time: float = 1000.0

    # Pixels par metre pour le rendu.
    pixels_par_metre: float = 20.0

    # Distance maximale pour le culling des objets (en metres). c'est a dire que les objets plus loin que cette distance ne seront pas rendus.
    distance_culling: float = 150.0

    # plan proche et plan lointain pour la projection perspective de la caméra (en metres).
    near_plane: float = 0.001
    far_plane: float = 1000.0

    fov: float = 90.0

    largeur_fenetre: int = 800
    hauteur_fenetre: int = 600


    #Sol taille et nombre de cases en metre
    taille_case_sol: float = 1.25
    nb_cases_sol: int = 30

    #HI-z params
    HIZ_COLS = 20   # Nombre de colonnes de tuiles
    HIZ_ROWS = 15   # Nombre de lignes de tuiles

