from src.Rendu.Point3D import Point3D


class BlueprintLanceur:
    """
    Lanceur de missile lourd.
    Forme : parallélépipède (véhicule blindé avec tourelle).
    """
    
    # --- POSITION ET ROTATION ---
    POSITION_X = 0.0
    POSITION_Y = 300        # Légèrement au-dessus du sol
    POSITION_Z = 0.0

    # --- PHYSIQUE ---
    VITESSE_X = 0.0
    VITESSE_Y = 0.0
    VITESSE_Z = 0.0

    ACCELERATION_X = 0.0
    ACCELERATION_Y = 0.0
    ACCELERATION_Z = 0.0

    FORCE_X = 0.0
    FORCE_Y = 0.0
    FORCE_Z = 0.0

    MASSE = 10000.0         # Véhicule lourd
    RESTITUTION = 0.05      # Très peu de rebond
    FRICTION = 1.2          # Beaucoup de friction (chenilles)
    
    # --- RENDU ---
    COULEUR = (64, 64, 64)  # Gris foncé (blindage)
    COULEUR_TOURELLE = (80, 80, 80)
    
    # --- GÉOMÉTRIE (Boîte 3D) ---
    # Corps du véhicule (parallélépipède)
    CORPS_LARGEUR = 3.0     # X
    CORPS_LONGUEUR = 5.0    # Z
    CORPS_HAUTEUR = 2.0     # Y
    
    # Points du corps (8 sommets d'une boîte)
    # Relative à la position du véhicule
    POINTS = [
            Point3D(-4.0, 0.0, -2.0),
            Point3D( 4.0, 0.0, -2.0),
            Point3D( 4.0, 1.5,  2.0),
            Point3D(-4.0, 1.5,  2.0),

            Point3D(-3.0, -1.0, -1.5),
            Point3D(-2.0, -1.0, -1.5),
            Point3D(-2.0, -0.5, -1.5),
            Point3D(-3.0, -0.5, -1.5),

            Point3D(2.0, -1.0, -1.5),
            Point3D(3.0, -1.0, -1.5),
            Point3D(3.0, -0.5, -1.5),
            Point3D(2.0, -0.5, -1.5),

            Point3D(-3.0, -1.0, 1.5),
            Point3D(-2.0, -1.0, 1.5),
            Point3D(-2.0, -0.5, 1.5),
            Point3D(-3.0, -0.5, 1.5),

            Point3D(2.0, -1.0, 1.5),
            Point3D(3.0, -1.0, 1.5),
            Point3D(3.0, -0.5, 1.5),
            Point3D(2.0, -0.5, 1.5),
        
    ]

   
   
    