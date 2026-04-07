class Moteur:
    def __init__(
        self,
        puissance_max: float = 0.0,
        thrust: float = 0.0,
        orientation: float = 0.0,
        debit_massique: float = 0.0,
        vitesse_ejection: float = 0.0,
        pression_sortie: float = 0.0,
        surface_sortie: float = 0.0,
        throttle: float = 0.0,
    ):
        self.puissance_max: float = puissance_max
        self.thrust: float = thrust
        self.orientation: float = orientation
        self.debit_massique: float = debit_massique
        self.vitesse_ejection: float = vitesse_ejection
        self.pression_sortie: float = pression_sortie
        self.surface_sortie: float = surface_sortie
        self.throttle: float = throttle
