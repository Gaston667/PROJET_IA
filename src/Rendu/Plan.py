class Plan:
    __slots__ = ('nx', 'ny', 'nz', 'd')

    def __init__(self, nx: float, ny: float, nz: float, d: float) -> None:
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.d  = d

    def distance_point(self, x: float, y: float, z: float) -> float:
        return self.nx*x + self.ny*y + self.nz*z + self.d
