class Renderable:
    FORME_CERCLE = 0
    FORME_LIGNE = 1
    FORME_POLYGONE = 2

    def __init__(
        self,
        couleur: tuple[int, int, int] = (255, 255, 255),
        visible: bool = True,
        forme: int = FORME_CERCLE,
        rayon: float = 0.2,
        segments: int = 16,
        anneaux: int = 8
    ) -> None:
        self.couleur: tuple[int, int, int] = couleur
        self.visible: bool = visible
        self.forme: int = forme
        self.rayon: float = rayon # taille reele de l'objet, pas en pixels mais en mettre ici
        self.segments: int = segments # pour les cercles, nombre de segments pour l'approximation
        self.anneaux: int = anneaux
