from src.Composant.Renderable import Renderable


class BlueprintBoule:
    POSITION_X = 20.0
    POSITION_Y = 200.0
    POSITION_Z = 20.0

    VITESSE_X = 0.0
    VITESSE_Y = 0.0
    VITESSE_Z = 0.0

    FORCE_X = 0.0
    FORCE_Y = 0.0
    FORCE_Z = 0.0

    MASSE = 50.0
    RESTITUTION = 0.25
    FRICTION = 0.85

    COULEUR = (220, 45, 45)
    FORME = Renderable.FORME_CERCLE
    RAYON = 2.0
    SEGMENTS = 22
    ANNEAUX = 6
    TAG = "boule_principale"
