class ColliderPlane:
    def __init__(
        self,
        nx: float,
        ny: float,
        nz: float,
        offset: float = 0.0, # La distance du plan a l'origine le long de sa normale.
    ) -> None:
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.offset = offset
