# grid_world.py

from turtle import position


class GridWorld:
    def __init__(self):
       self.taille = 20
       self.pos_depart = (0, 0)
       self.pos_objectif = (19, 19)

       self.obstacles = [
            # Ligne 0
           (0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(0,9),(0,10),
           (0,11),(0,12),(0,13),(0,14),(0,15),(0,16),(0,17),(0,18),(0,19),
            # Ligne 1
            (1,0),(1,4),(1,6),(1,8),(1,10),(1,12),(1,16),(1,18),
            # Ligne 2
            (2,0),(2,2),(2,3),(2,4),(2,6),(2,8),(2,10),(2,12),(2,14),(2,16),(2,18),
            # Ligne 3
            (3,0),(3,6),(3,10),(3,14),(3,18),
            # Ligne 4
            (4,2),(4,4),(4,6),(4,8),(4,10),(4,12),(4,14),(4,16),(4,18),
            # Ligne 5
            (5,0),(5,2),(5,4),(5,6),(5,8),(5,10),(5,12),(5,14),(5,16),(5,18),
            # Ligne 6
            (6,2),(6,6),(6,10),(6,14),(6,18),
            # Ligne 7
            (7,0),(7,2),(7,4),(7,6),(7,8),(7,10),(7,12),(7,14),(7,16),(7,18),
            # Ligne 8
            (8,2),(8,6),(8,10),(8,14),(8,18),
            # Ligne 9
            (9,0),(9,2),(9,4),(9,6),(9,8),(9,10),(9,12),(9,14),(9,16),(9,18),
            # Ligne 10
            (10,2),(10,6),(10,10),(10,14),(10,18),
            # Ligne 11
            (11,0),(11,2),(11,4),(11,6),(11,8),(11,10),(11,12),(11,14),(11,16),(11,18),
            # Ligne 12
            (12,2),(12,6),(12,10),(12,14),(12,18),
            # Ligne 13
            (13,0),(13,2),(13,4),(13,6),(13,8),(13,10),(13,12),(13,14),(13,16),(13,18),
            # Ligne 14
            (14,2),(14,6),(14,14),(14,18),
            # Ligne 15
            (15,0),(15,2),(15,4),(15,6),(15,8),(15,10),(15,12),(15,14),(15,16),(15,18),
            # Ligne 16
            (16,2),(16,6),(16,10),(16,14),(16,18),
            # Ligne 17
            (17,0),(17,2),(17,4),(17,6),(17,8),(17,10),(17,12),(17,14),(17,16),(17,18),
            # Ligne 18
            (18,2),(18,6),(18,10),(18,14),
            # Ligne 19 (presque tout bloqué sauf sortie)
            (19,0),(19,1),(19,2),(19,3),(19,4),(19,8),
            (19,9),(19,10),(19,11),(19,12),(19,13),(19,14),(19,15),(19,16),(19,17)
        ]



       self.etats_possibles = [
            (i, j) for i in range(self.taille) for j in range(self.taille)
        ]
       self.agent_position = self.pos_depart  # Position actuelle

    def reset(self):
        self.agent_position = self.pos_depart
        return self.agent_position

    def get_actions_possibles(self):
        return ['haut', 'bas', 'gauche', 'droite']

    def appliquer_action(self, action):
        ligne, colonne = self.agent_position
        ancienne_position = self.agent_position

        
        if action == 'haut' and ligne > 0:
            ligne -= 1
        elif action == 'bas' and ligne < self.taille - 1:
            ligne += 1
        elif action == 'gauche' and colonne > 0:
            colonne -= 1
        elif action == 'droite' and colonne < self.taille - 1:
            colonne += 1

        nouvelle_position = (ligne, colonne)

        # Mise à jour de la position de l'agent
        self.agent_position = nouvelle_position

        # Récompense selon l’état atteint
        if nouvelle_position == self.pos_objectif:
            return nouvelle_position, 10, True
        elif nouvelle_position in self.obstacles:
            return nouvelle_position, -10, False
        elif nouvelle_position == ancienne_position:
            return nouvelle_position, -1, False
        else:
            return nouvelle_position, 0, False

    def est_terminal(self, etat):
        return etat == self.pos_objectif

    def afficher(self):
        for i in range(self.taille):
            ligne = ""
            for j in range(self.taille):
                pos = (i, j)
                if pos == self.agent_position:
                    ligne += " A "
                elif pos == self.pos_objectif:
                    ligne += " O "
                elif pos in self.obstacles:
                    ligne += " X "
                else:
                    ligne += " . "
            print(ligne)
        print()



