class Radar:
    def __init__(
        self,
        puissance: float = 0.0,
        gain: float = 0.0,
        frequence: float = 0.0,
        seuil: float = 0.0,
    ):
        self.puissance: float = puissance
        self.gain: float = gain
        self.frequence: float = frequence
        self.seuil: float = seuil
