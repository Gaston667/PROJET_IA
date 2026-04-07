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
    max_simulation_time: float = 100.0

    # Pixels par metre pour le rendu.
    pixels_par_metre: float = 20.0
