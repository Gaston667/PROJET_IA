# interface_grille.py aa

import tkinter as tk
import matplotlib.pyplot as plt

class InterfaceGrille:
    def __init__(self, env, agent):
        self.env = env
        self.agent = agent
        self.root = tk.Tk()
        self.root.title("GridWorld RL")
        self.cell_size = 50
        self.num_etape = 0

        self.canvas = tk.Canvas(
            self.root,
            width=self.env.taille * self.cell_size,
            height=self.env.taille * self.cell_size
        )
        self.canvas.pack()

        self.btn_episode = tk.Button(self.root, text="▶️ Lancer un épisode", command=self.lancer_episode)
        self.btn_episode.pack()

        self.var_afficher = tk.BooleanVar(value=False)
        self.check_afficher = tk.Checkbutton(
            self.root, text="Afficher l'exécution", variable=self.var_afficher
        )
        self.check_afficher.pack()

        self.btn_entrainement = tk.Button(
            self.root, text="🏋️ Lancer 100 épisodes", command=lambda: self.lancer_entrainement(100)
        )
        self.btn_entrainement.pack()

        self.btn_suivant = tk.Button(self.root, text="➡️ Étape suivante", command=self.etape_suivante_manuel)
        self.btn_suivant.pack()

        self.btn_graph_v0 = tk.Button(self.root, text="📈 Graphique V[(0,0)]", command=self.afficher_graphique_v0)
        self.btn_graph_v0.pack()

        self.btn_graph_etapes = tk.Button(self.root, text="📉 Graphique étapes/épisode", command=self.afficher_graphique_etapes)
        self.btn_graph_etapes.pack()

        self.btn_graph_epsilons = tk.Button(self.root, text="📉 Graphique epsilon", command=self.afficher_graphique_epsilons)
        self.btn_graph_epsilons.pack()

        self.label_info = tk.Label(self.root, text="Récompense : 0")
        self.label_info.pack()

        self.episode_en_cours = False
        self.mode_manuel = False
        self.dessiner_grille()
        self.root.mainloop()

    def dessiner_grille(self):
        self.canvas.delete("all")
        for i in range(self.env.taille):
            for j in range(self.env.taille):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                case = (i, j)
                couleur = "white"
                if case == self.env.agent_position:
                    couleur = "blue"
                elif case in self.env.murs:
                    couleur = "red"
                elif case == self.env.pos_objectif:
                    couleur = "gold"

                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=couleur)

                if self.agent and case not in self.env.murs:
                    valeur = self.agent.V.get(case, 0)
                    self.canvas.create_text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        text=f"{valeur:.1f}",
                        font=("Helvetica", 12, "bold")
                    )

    def lancer_episode(self):
        if self.episode_en_cours:
            return
        self.mode_manuel = False
        self.episode_en_cours = True
        self.etat = self.env.reinitialiser()
        self.termine = False
        self.total_recompense = 0
        self.num_etape = 0
        self.etape_suivante()

    def lancer_entrainement(self, nb_episodes):
        afficher = self.var_afficher.get()
        if afficher:
            self.lancer_episode()  # avec affichage normal
        else:
            for _ in range(nb_episodes):
                self.agent.jouer_episode(afficher=False, pause=0.0)
            self.dessiner_grille()
            self.label_info.config(text=f"✅ {nb_episodes} épisodes terminés.")

    def etape_suivante(self):
        if self.termine:
            self.episode_en_cours = False
            return

        action = self.agent.choisir_action(self.etat, afficher=True)
        nouvel_etat, recompense, termine = self.env.appliquer(action)
        self.agent.mettre_a_jour(self.etat, recompense, nouvel_etat)
        self.total_recompense += recompense
        self.termine = termine
        self.etat = nouvel_etat

        self.dessiner_grille()
        self.agent.afficher_valeurs_intermediaires(self.num_etape)
        self.num_etape += 1

        self.label_info.config(text=f"Récompense : {self.total_recompense}")

        if not self.termine and not self.mode_manuel:
            self.root.after(500, self.etape_suivante)

    def etape_suivante_manuel(self):
        if not self.episode_en_cours:
            self.mode_manuel = True
            self.episode_en_cours = True
            self.etat = self.env.reinitialiser()
            self.termine = False
            self.total_recompense = 0
            self.num_etape = 0
        self.etape_suivante()

    def afficher_graphique_v0(self):
        if hasattr(self.agent, "historique_V0") and self.agent.historique_V0:
            plt.figure()
            plt.plot(self.agent.historique_V0)
            plt.title("Évolution de V[(0, 0)] au fil des épisodes")
            plt.xlabel("Épisode")
            plt.ylabel("Valeur estimée")
            plt.grid(True)
            plt.show()

    def afficher_graphique_etapes(self):
        if hasattr(self.agent, "historique_etapes") and self.agent.historique_etapes:
            plt.figure()
            plt.plot(self.agent.historique_etapes, color="black")
            plt.title("Nombre d'étapes pour atteindre l'objectif")
            plt.xlabel("Épisode")
            plt.ylabel("Nombre d'étapes")
            plt.grid(True)
            plt.show()
            
    
    def afficher_graphique_epsilons(self):
            if self.agent.historique_epsilons:
                plt.figure()
                plt.plot(self.agent.historique_epsilons)
                plt.title("Évolution de ε (alpha) au fil des épisodes")
                plt.xlabel("Épisode")
                plt.ylabel("ε / alpha")
                plt.grid(True)
                plt.show()
