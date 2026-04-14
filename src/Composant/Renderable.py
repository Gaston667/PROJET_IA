class Renderable:
    def __init__(
        self,
        couleur: tuple[int, int, int] = (255, 255, 255),
        visible: bool = True,
        forme: str = None,
        rayon: float = 0.2,
    ) -> None:
        self.couleur: tuple[int, int, int] = couleur
        self.visible: bool = visible
        self.forme: str = forme
        self.rayon: float = rayon # taille reele de l'objet, pas en pixels mais en mettre ici
