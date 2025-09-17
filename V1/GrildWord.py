# grid_world.py

class GridWorld:
    def __init__(self):
        self.taille = 3  # Grille 10x10
        self.murs = {(1, 1)}

        self.pos_depart = (2, 1)   # Position orange dans ton image
        self.pos_objectif = (1, 2)         # Objectif
        self.agent_position = self.pos_depart
        





    def reinitialiser(self):
        self.agent_position = self.pos_depart
        return self.agent_position

    def appliquer(self, action):
        ligne, colonne = self.agent_position

        if action == 'haut' and ligne > 0:
            ligne -= 1
        elif action == 'bas' and ligne < self.taille - 1:
            ligne += 1
        elif action == 'gauche' and colonne > 0:
            colonne -= 1
        elif action == 'droite' and colonne < self.taille - 1:
            colonne += 1

        nouvelle_position = (ligne, colonne)
        self.agent_position = nouvelle_position

        if nouvelle_position == self.pos_objectif:
            return nouvelle_position, 10, True
        elif nouvelle_position in self.murs:
            return nouvelle_position, -10, True
        else:
            return nouvelle_position, 0, False

    def afficher(self):
        for i in range(self.taille):
            ligne = ""
            for j in range(self.taille):
                pos = (i, j)
                if pos == self.agent_position:
                    ligne += " A "
                elif pos == self.pos_objectif:
                    ligne += " O "
                elif pos in self.murs:
                    ligne += " M "
                else:
                    ligne += " . "
            print(ligne)
        print()
