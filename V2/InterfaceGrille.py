# PygameInterface.py

import pygame
import sys

class InterfaceGrillePygame:
    def __init__(self, env, agent, cell_size=100):
        pygame.init()
        self.env = env
        self.agent = agent
        self.taille = env.taille
        self.cell_size = cell_size
        # self.screen = pygame.display.set_mode((cell_size * self.taille, cell_size * self.taille))
        self.screen = pygame.display.set_mode((cell_size * self.taille, cell_size * self.taille + 40))
        pygame.display.set_caption("GridWorld - Pygame")

        self.colors = {
            "fond": (255, 255, 255),
            "grille": (0, 0, 0),
            "objectif": (0, 255, 0),
            "agent": (0, 0, 255),
            "obstacle": (0, 0, 0),
        }

        self.font = pygame.font.SysFont("Arial", 18)
        self.arrow_symbols = {
            "haut": "↑",
            "bas": "↓",
            "gauche": "←",
            "droite": "→"
        }

    def dessiner(self, etape=None):
        self.screen.fill(self.colors["fond"])

        # Grille
        for i in range(self.taille):
            for j in range(self.taille):
                x = j * self.cell_size
                y = i * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, self.colors["grille"], rect, 1)

                pos = (i, j)
                if pos == self.env.agent_position:
                    pygame.draw.rect(self.screen, self.colors["agent"], rect)
                elif pos == self.env.pos_objectif:
                    pygame.draw.rect(self.screen, self.colors["objectif"], rect)
                elif pos in self.env.obstacles:
                    pygame.draw.rect(self.screen, self.colors["obstacle"], rect)

        # self.dessiner_q_values()  # Ajout Q-values
        self.afficher_q_values_avec_fleches()
        if etape is not None:
            self.afficher_num_etape(etape) # Affichage de l'étape

        pygame.display.flip()

    def afficher_num_etape(self, etape):
        font = pygame.font.SysFont("Arial", 20)
        texte = font.render(f"Episode : {etape}", True, (0, 0, 0))
        self.screen.blit(texte, (10, self.cell_size * self.taille + 10))


    def dessiner_q_values(self):
        font = pygame.font.SysFont("Arial", 14)
        for etat in self.env.etats_possibles:
            # if etat in self.env.obstacles:
            #     continue  # on n'affiche pas sur les obstacles
            q_values = []
            for action in self.agent.actions_possibles:
                q_values.append(self.agent.q_table.get((etat, action), 0))

            max_q_value = max(q_values)
            min_q_value = min(q_values)
                

            x = etat[1] * self.cell_size
            y = etat[0] * self.cell_size


            if etat in self.env.obstacles:
                texte = font.render(f"{min_q_value:.2f}", True, (0, 0, 0))
            else:
                texte = font.render(f"{max_q_value:.2f}", True, (0, 0, 0))
            self.screen.blit(texte, (x + 5, y + 5))


    def afficher_q_values_avec_fleches(self):
        for etat in self.env.etats_possibles:
            if etat in self.env.obstacles:
                continue

            x = etat[1] * self.cell_size
            y = etat[0] * self.cell_size

            # Récupère toutes les Q-values pour cet état
            q_vals = {action: self.agent.q_table.get((etat, action), 0) for action in self.agent.actions_possibles}

            # Trouve la meilleure action (max Q-value)
            meilleure_action = max(q_vals, key=q_vals.get)
            meilleure_q = q_vals[meilleure_action]
            fleche = self.arrow_symbols[meilleure_action]

            # Position de la flèche selon direction
            if meilleure_action == "haut":
                pos = (x + self.cell_size // 2, y + 10)
            elif meilleure_action == "bas":
                pos = (x + self.cell_size // 2, y + self.cell_size - 10)
            elif meilleure_action == "gauche":
                pos = (x + 10, y + self.cell_size // 2)
            elif meilleure_action == "droite":
                pos = (x + self.cell_size - 10, y + self.cell_size // 2)

            # Affichage de la flèche et Q-value
            texte = self.font.render(f"{fleche}{meilleure_q:.1f}", True, (0, 0, 0))
            text_rect = texte.get_rect(center=pos)
            self.screen.blit(texte, text_rect)


            


    def affichage_env(self, etape=None):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        self.dessiner(etape)

    def fermer(self):
        pygame.quit()
