import sys

import pygame


class InterfaceGrillePygame:
    def __init__(self, env, agent, cell_size=100):
        pygame.init()
        self.env = env
        self.agent = agent
        self.taille = env.taille
        self.cell_size = cell_size
        self.info_height = 72

        width = cell_size * self.taille
        height = cell_size * self.taille + self.info_height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("GridWorld - Labyrinthe")

        # Palette plus douce et plus lisible qu'un noir/blanc brut.
        self.colors = {
            "fond_haut": (242, 236, 224),
            "fond_bas": (222, 214, 198),
            "panneau": (50, 60, 72),
            "texte_panneau": (245, 244, 239),
            "case": (248, 244, 236),
            "case_bord": (194, 182, 160),
            "obstacle": (67, 74, 84),
            "obstacle_lumiere": (98, 108, 120),
            "objectif": (226, 179, 53),
            "objectif_centre": (255, 237, 168),
            "agent": (50, 134, 222),
            "agent_lumiere": (147, 210, 255),
            "texte_case": (70, 78, 88),
            "ombre": (0, 0, 0, 28),
        }

        # Polices creees une seule fois pour garder l'affichage fluide.
        self.font = pygame.font.SysFont("Arial", max(14, cell_size // 4), bold=True)
        self.small_font = pygame.font.SysFont("Arial", max(12, cell_size // 5))
        self.info_font = pygame.font.SysFont("Arial", 22, bold=True)

        self.tile_padding = max(3, cell_size // 14)
        self.corner_radius = max(6, cell_size // 5)

        # ASCII pour eviter les problemes d'encodage tout en gardant l'idee
        # d'une direction conseillee par la politique.
        self.arrow_symbols = {
            "haut": "^",
            "bas": "v",
            "gauche": "<",
            "droite": ">",
        }

    def _draw_vertical_gradient(self):
        width = self.cell_size * self.taille
        height = self.cell_size * self.taille

        for y in range(height):
            ratio = y / max(1, height - 1)
            color = tuple(
                int(self.colors["fond_haut"][i] * (1 - ratio) + self.colors["fond_bas"][i] * ratio)
                for i in range(3)
            )
            pygame.draw.line(self.screen, color, (0, y), (width, y))

    def _cell_rect(self, i, j):
        x = j * self.cell_size + self.tile_padding
        y = i * self.cell_size + self.tile_padding
        size = self.cell_size - 2 * self.tile_padding
        return pygame.Rect(x, y, size, size)

    def _draw_shadow(self, rect):
        shadow_rect = rect.move(2, 3)
        shadow_surface = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            shadow_surface,
            self.colors["ombre"],
            shadow_surface.get_rect(),
            border_radius=self.corner_radius,
        )
        self.screen.blit(shadow_surface, shadow_rect.topleft)

    def _draw_base_cell(self, rect):
        self._draw_shadow(rect)
        pygame.draw.rect(self.screen, self.colors["case"], rect, border_radius=self.corner_radius)
        pygame.draw.rect(self.screen, self.colors["case_bord"], rect, width=1, border_radius=self.corner_radius)

    def _draw_obstacle(self, rect):
        self._draw_shadow(rect)
        pygame.draw.rect(self.screen, self.colors["obstacle"], rect, border_radius=self.corner_radius)

        inset = max(3, self.cell_size // 10)
        inner_rect = rect.inflate(-inset, -inset)
        pygame.draw.rect(
            self.screen,
            self.colors["obstacle_lumiere"],
            inner_rect,
            width=2,
            border_radius=max(4, self.corner_radius - 2),
        )

    def _draw_objectif(self, rect):
        self._draw_shadow(rect)
        pygame.draw.rect(self.screen, self.colors["objectif"], rect, border_radius=self.corner_radius)

        center = rect.center
        outer_radius = max(8, rect.width // 4)
        inner_radius = max(4, rect.width // 8)
        pygame.draw.circle(self.screen, self.colors["objectif_centre"], center, outer_radius)
        pygame.draw.circle(self.screen, self.colors["objectif"], center, inner_radius)

    def _draw_agent(self, rect):
        self._draw_shadow(rect)
        pygame.draw.rect(self.screen, self.colors["case"], rect, border_radius=self.corner_radius)
        pygame.draw.rect(self.screen, self.colors["case_bord"], rect, width=1, border_radius=self.corner_radius)

        center = rect.center
        glow_radius = max(10, rect.width // 3)
        body_radius = max(8, rect.width // 4)
        pygame.draw.circle(self.screen, self.colors["agent_lumiere"], center, glow_radius)
        pygame.draw.circle(self.screen, self.colors["agent"], center, body_radius)

    def _draw_policy_hint(self, etat, rect):
        q_vals = {
            action: self.agent.q_table.get((etat, action), 0)
            for action in self.agent.actions_possibles
        }

        meilleure_action = max(q_vals, key=q_vals.get)
        meilleure_q = q_vals[meilleure_action]
        fleche = self.arrow_symbols[meilleure_action]

        direction_text = self.font.render(fleche, True, self.colors["texte_case"])
        direction_rect = direction_text.get_rect(center=(rect.centerx, rect.centery - rect.height // 6))
        self.screen.blit(direction_text, direction_rect)

        value_text = self.small_font.render(f"{meilleure_q:.1f}", True, self.colors["texte_case"])
        value_rect = value_text.get_rect(center=(rect.centerx, rect.centery + rect.height // 5))
        self.screen.blit(value_text, value_rect)

    def _draw_status_bar(self, etape=None):
        top = self.cell_size * self.taille
        panel_rect = pygame.Rect(0, top, self.cell_size * self.taille, self.info_height)
        pygame.draw.rect(self.screen, self.colors["panneau"], panel_rect)

        episode_label = f"Episode : {etape}" if etape is not None else "Episode : -"
        goal_label = f"Objectif : {self.env.pos_objectif}"
        agent_label = f"Agent : {self.env.agent_position}"

        title = self.info_font.render(episode_label, True, self.colors["texte_panneau"])
        self.screen.blit(title, (16, top + 12))

        meta = self.small_font.render(goal_label, True, self.colors["texte_panneau"])
        self.screen.blit(meta, (16, top + 42))

        meta_agent = self.small_font.render(agent_label, True, self.colors["texte_panneau"])
        self.screen.blit(meta_agent, (220, top + 42))

    def dessiner(self, etape=None):
        # On redessine tout a chaque frame pour garder un affichage simple
        # et coherent avec les Q-values qui evoluent pendant l'apprentissage.
        self._draw_vertical_gradient()

        for i in range(self.taille):
            for j in range(self.taille):
                pos = (i, j)
                rect = self._cell_rect(i, j)

                if pos == self.env.agent_position:
                    self._draw_agent(rect)
                elif pos == self.env.pos_objectif:
                    self._draw_objectif(rect)
                elif pos in self.env.obstacles:
                    self._draw_obstacle(rect)
                else:
                    self._draw_base_cell(rect)

                if pos not in self.env.obstacles:
                    self._draw_policy_hint(pos, rect)

        self._draw_status_bar(etape)
        pygame.display.flip()

    def affichage_env(self, etape=None):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        self.dessiner(etape)

    def fermer(self):
        pygame.quit()
