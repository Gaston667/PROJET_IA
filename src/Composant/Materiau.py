class Materiau:
    def __init__(self, restitution: float = 0.0, friction: float = 0.0) -> None:
        self.restitution = restitution
        self.friction = friction
