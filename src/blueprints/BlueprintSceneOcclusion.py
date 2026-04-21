class BlueprintSceneOcclusion:
    PANNEAU_POSITION_X = 20.0
    PANNEAU_POSITION_Y = 10.0
    PANNEAU_POSITION_Z = 8.0
    PANNEAU_COULEUR = (45, 95, 210)
    PANNEAU_RAYON = 45.0
    PANNEAU_POINTS = [
        (-36.0, -20.0, 0.0),
        (36.0, -20.0, 0.0),
        (36.0, 20.0, 0.0),
        (-36.0, 20.0, 0.0),
    ]

    LIGNE_POSITION_X = 20.0
    LIGNE_POSITION_Y = 35.0
    LIGNE_POSITION_Z = 7.0
    LIGNE_TAG = "ligne_occlusion"
    LIGNE_AMPLITUDE_Y = 8.0
    LIGNE_VITESSE = 1.4
    LIGNE_COULEUR = (255, 230, 40)
    LIGNE_RAYON = 1.0
    LIGNE_TAG = "ligne_occlusion"
    LIGNE_POINTS = [
        (-45.0, 0.0, 0.0),
        (45.0, 0.0, 0.0),
    ]

    BALLE_TAG = "balle_occlusion"
    BALLE_POSITION_Y = 10.0
    BALLE_POSITION_Z = 35.0
    BALLE_X_CENTRE = 20.0
    BALLE_AMPLITUDE_X = 85.0
    BALLE_VITESSE = 0.9
    BALLE_RAYON = 12.0
    BALLE_COULEUR = (255, 20, 20)

    SPHERE_SEGMENTS = 40
    SPHERE_ANNEAUX = 20
