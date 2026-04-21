from __future__ import annotations

import pygame

from src.Composant.Position import Position
from src.Composant.Renderable import Renderable
from src.Config import Config
from src.Monde.Monde import Monde
from src.Rendu.Point3D import Point3D


class SystemeRendu:
    """
    Système de rendu principal.

    Orchestre l'affichage d'une scène : sol, entités et overlay optionnel.
    Utilise un renderer (ex: Render3D) et une caméra pour projeter la scène.

    Attributes:
        renderer: Moteur de rendu (Render3D ou autre).
        overlay: Fonction optionnelle appelée après le rendu principal,
                 signature : overlay(renderer, monde).
    """

    def __init__(self, renderer, overlay=None) -> None:
        """
        Initialise le système de rendu.

        Args:
            renderer: Instance du moteur de rendu.
            overlay: Fonction optionnelle de surimpression (HUD, debug, etc.).
        """
        self.renderer = renderer
        self.overlay = overlay

    def render(self, monde: Monde) -> None:
        """
        Effectue le rendu complet d'une frame.

        Étapes :
        1. Initialise le renderer si nécessaire.
        2. Efface l'écran.
        3. Dessine le sol.
        4. Calcule le frustum une seule fois.
        5. Dessine toutes les entités visibles ayant Position + Renderable.
        6. Applique l'overlay si présent.
        7. Affiche la frame.

        Args:
            monde: Le monde contenant les entités à afficher.
        """
        if not self.renderer.initialise:
            self.renderer.initialiser()

        self.renderer.effacer()

        # ── Frustum calculé une seule fois par frame ─────────────────────────
        # La caméra est self.renderer.camera (unique source de vérité)
        frustum = self.renderer.extraire_plans_frustum()

        # Dessiner le sol
        self.renderer.draw_sol(taille_case=Config.taille_case_sol, nb_cases=Config.nb_cases_sol, frustum=frustum)

        # Dessiner les entités
        for entite in monde.entites:
            renderable = entite.get(Renderable)
            position   = entite.get(Position)

            if position is None or renderable is None:
                continue

            if not renderable.visible:
                continue

            point = Point3D(position.x, position.y, position.z)
            self.renderer.draw_entity(renderable, point, frustum)

        # Appliquer l'overlay si défini (HUD, debug, etc.)
        if self.overlay is not None:
            self.overlay(self.renderer, monde)

        self.renderer.afficher()
