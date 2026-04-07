class Renderable:
    def __init__(
        self,
        couleur: tuple[int, int, int] = (255, 255, 255),
        visible: bool = True,
        forme: str = None,
    ) -> None:
        self.couleur: tuple[int, int, int] = couleur
        self.visible: bool = visible
        self.forme: str = forme
