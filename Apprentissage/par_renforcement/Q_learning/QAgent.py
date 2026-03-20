import random
import time


class QAgent:
    def __init__(self, env, epsilon=0.5, gamma=0.9, alpha=0.01):
        # gamma mesure l'importance des recompenses futures.
        # Plus gamma est grand, plus l'agent "pense long terme".
        self.gamma = gamma

        # epsilon pilote l'exploration aleatoire.
        # Au debut, on explore plus. Ensuite, on reduit progressivement.
        self.epsilon_depart = epsilon
        self.alpha = alpha
        self.epsilon = epsilon

        self.env = env
        self.position_agent = env.pos_depart
        self.actions_possibles = env.get_actions_possibles()

        self.num_episode_total = 0
        self.num_episode = 0
        self.historique_epsilons = []
        self.historique_etapes = []
        self.historique_recompenses = []
        self.compteur_actions = {action: 0 for action in self.actions_possibles}

        # La Q-table stocke la "qualite" d'une action dans un etat donne.
        # Ici, la cle est un couple : (etat, action).
        self.q_table = {}
        for etat in self.env.etats_possibles:
            for action in self.actions_possibles:
                self.q_table[(etat, action)] = 0.0

    def _import_matplotlib(self):
        # matplotlib n'est charge que quand on veut vraiment tracer un graphe.
        try:
            import matplotlib.pyplot as plt
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "matplotlib n'est pas installe. Execute: py -3.13 -m pip install matplotlib"
            ) from exc
        return plt

    def ajuster_epsilon(self):
        # On diminue epsilon au fil du temps pour passer petit a petit
        # d'un comportement exploratoire a un comportement plus stable.
        self.epsilon = self.epsilon_depart / (1 + self.alpha * self.num_episode)

    def reset_position(self):
        self.position_agent = self.env.pos_depart

    def choisir_action(self, etat, afficher=False):
        # Strategie epsilon-greedy :
        # - avec probabilite epsilon : exploration
        # - sinon : exploitation de la meilleure action connue
        if random.random() < self.epsilon:
            if afficher:
                print("\n[Exploration] Etat actuel :", etat)
            action = random.choice(self.actions_possibles)
        else:
            if afficher:
                print("\n[Exploitation] Etat actuel :", etat)

            q_values_actions = {
                action: self.q_table[(etat, action)]
                for action in self.actions_possibles
            }

            if afficher:
                for action, valeur in q_values_actions.items():
                    print(f"Action {action} : {valeur}")

            # On recupere la meilleure valeur connue pour cet etat.
            valeur_max = max(q_values_actions.values())

            # S'il y a plusieurs meilleures actions, on en choisit une
            # aleatoirement pour eviter de figer l'agent trop tot.
            meilleures_actions = [
                action
                for action, valeur in q_values_actions.items()
                if valeur == valeur_max
            ]
            action = random.choice(meilleures_actions)

            if afficher:
                print(f"Valeur max : {valeur_max}")
                print(f"Action selectionnee : {action}")

        # Le compteur suit maintenant toutes les actions choisies,
        # y compris pendant l'exploration.
        self.compteur_actions[action] += 1
        return action

    def mise_a_jour_q_table(self, etat, action, recompense, nouvel_etat, terminal, afficher=False):
        if terminal:
            q_value_max = 0
        else:
            # On estime la meilleure valeur atteignable depuis le nouvel etat.
            q_value_max = max(
                self.q_table[(nouvel_etat, action_possible)]
                for action_possible in self.actions_possibles
            )

        ancienne_q_value = self.q_table[(etat, action)]

        # Formule classique du Q-learning :
        # nouvelle_Q = ancienne_Q + alpha * (cible - ancienne_Q)
        # avec cible = recompense immediate + valeur future estimee
        nouvelle_q_value = ancienne_q_value + self.alpha * (
            recompense + self.gamma * q_value_max - ancienne_q_value
        )
        self.q_table[(etat, action)] = nouvelle_q_value

        if afficher:
            print(f"\nMise a jour de Q({etat}, {action})")
            print(f"Ancienne Q : {ancienne_q_value:.4f}")
            print(f"Recompense r : {recompense}")
            print(f"Max Q({nouvel_etat}, a') = {q_value_max:.4f}")
            print(f"Nouvelle Q : {nouvelle_q_value:.4f}")

    def boucle_dapprentissage(
        self,
        num_episodes,
        afficher=False,
        pause=1.0,
        afficher_valeurs_finales=True,
        apprentissage=True,
        interface_graphique=None,
        max_steps=None,
    ):
        if max_steps is None:
            # On recupere la limite definie par l'environnement.
            # Cette protection evite les episodes qui tournent trop longtemps.
            max_steps = getattr(self.env, "max_steps_par_episode", self.env.taille * self.env.taille * 4)

        for episode in range(num_episodes):
            # Chaque episode repart de l'etat initial.
            etat = self.env.reset()
            self.position_agent = etat
            compteur_etape = 0
            termine = False
            total_recompense = 0

            if afficher:
                print(f"\n===================== DEBUT DE L'EPISODE {episode + 1} =====================\n")
                print(f"Episode n°{episode + 1} | Alpha actuel : {self.alpha:.4f}")
                print("Position initiale :")
                self.env.afficher()

            while not termine and compteur_etape < max_steps:
                action = self.choisir_action(etat, afficher=afficher)
                nouvel_etat, recompense, termine = self.env.appliquer_action(action)

                if apprentissage:
                    # Pendant l'apprentissage, on met a jour ce que l'agent
                    # a appris apres chaque transition.
                    self.mise_a_jour_q_table(
                        etat,
                        action,
                        recompense,
                        nouvel_etat,
                        termine,
                        afficher=afficher,
                    )

                etat = nouvel_etat
                compteur_etape += 1
                total_recompense += recompense

                if afficher:
                    self.env.afficher()

                if interface_graphique:
                    import pygame

                    interface_graphique.affichage_env(etape=episode + 1)
                    pygame.event.pump()
                    if pause > 0:
                        pygame.time.delay(int(pause))
                elif pause > 0:
                    time.sleep(pause)

            if not termine and afficher:
                print(f"Episode interrompu apres {max_steps} etapes pour eviter une boucle trop longue.")

            self.num_episode += 1
            self.ajuster_epsilon()

            # On garde un historique pour visualiser la progression
            # de l'entrainement dans les graphes.
            self.historique_epsilons.append(self.epsilon)
            self.historique_etapes.append(compteur_etape)
            self.historique_recompenses.append(total_recompense)

            if afficher:
                print("\nFIN DE L'EPISODE")
                print(f"Episode {episode + 1} termine")
                print(f"Recompense totale : {total_recompense}")
                print(f"Epsilon suivant : {self.epsilon:.4f}")
                print(f"Nombre d'etapes : {compteur_etape}")
                print("============================================================\n")

        if afficher_valeurs_finales:
            print("\nAPPRENTISSAGE TERMINE")
            print(f"Episodes totaux : {self.num_episode}")
            print(f"Dernier epsilon : {self.epsilon:.4f}")
            print("\nQ-table finale :")
            for etat in self.env.etats_possibles:
                for action in self.actions_possibles:
                    print(f"Q({etat}, {action}) = {self.q_table[(etat, action)]:.4f}")

    def tester_agent(self, afficher=True, pause=0.5, max_steps=None):
        if max_steps is None:
            max_steps = getattr(self.env, "max_steps_par_episode", self.env.taille * self.env.taille * 4)

        etat = self.env.reset()
        self.position_agent = etat
        termine = False
        nb_etapes = 0
        total_recompense = 0

        if afficher:
            print("\nDEBUT DU TEST")

        while not termine and nb_etapes < max_steps:
            # En phase de test, on coupe l'exploration pour observer
            # le comportement "reel" de la politique apprise.
            ancienne_epsilon = self.epsilon
            self.epsilon = 0.0
            action = self.choisir_action(etat, afficher=afficher)
            self.epsilon = ancienne_epsilon

            nouvel_etat, recompense, termine = self.env.appliquer_action(action)
            etat = nouvel_etat
            nb_etapes += 1
            total_recompense += recompense

            if afficher:
                self.env.afficher()
                if pause > 0:
                    time.sleep(pause)

        if not termine and afficher:
            print(f"Test interrompu apres {max_steps} etapes pour eviter une boucle trop longue.")

        print(f"TEST TERMINE en {nb_etapes} etapes | Recompense : {total_recompense}")

    def moyenne_glissante(self, data, window=10):
        # La moyenne glissante lisse les courbes pour mieux voir
        # la tendance generale sans le bruit episode par episode.
        resultat = []
        for i in range(len(data)):
            debut = max(0, i - window + 1)
            fenetre = data[debut:i + 1]
            moyenne = sum(fenetre) / len(fenetre)
            resultat.append(moyenne)
        return resultat

    def afficher_graphiques(self, graphiques=0, **kwargs):
        # Compatibilite avec l'ancien appel Graphiques=...
        if "Graphiques" in kwargs:
            graphiques = kwargs["Graphiques"]

        if self.num_episode == 0:
            print("Aucun episode n'a encore ete lance.")
            return

        plt = self._import_matplotlib()
        episodes = list(range(1, self.num_episode + 1))

        if graphiques == 0:
            # Affichage separe des trois indicateurs principaux.
            plt.figure()
            plt.plot(episodes, self.historique_epsilons, label="Epsilon")
            plt.xlabel("Episode")
            plt.ylabel("Valeur de l'epsilon")
            plt.title("Evolution de l'epsilon")
            plt.grid(True)
            plt.show()

            plt.figure()
            plt.plot(episodes, self.historique_etapes, label="Nombre d'etapes", color="orange")
            plt.xlabel("Episode")
            plt.ylabel("Etapes")
            plt.title("Etapes par episode")
            plt.grid(True)
            plt.show()

            plt.figure()
            plt.plot(episodes, self.historique_recompenses, label="Recompense", color="green")
            plt.xlabel("Episode")
            plt.ylabel("Recompense")
            plt.title("Recompense par episode")
            plt.grid(True)
            plt.show()
        elif graphiques == 1:
            plt.figure()
            plt.plot(episodes, self.historique_epsilons, label="Epsilon")
            plt.xlabel("Episode")
            plt.ylabel("Valeur de l'epsilon")
            plt.title("Evolution de l'epsilon")
            plt.grid(True)
            plt.show()
        elif graphiques == 2:
            plt.figure()
            plt.plot(episodes, self.historique_etapes, label="Nombre d'etapes", color="orange")
            plt.xlabel("Episode")
            plt.ylabel("Etapes")
            plt.title("Etapes par episode")
            plt.grid(True)
            plt.show()
        elif graphiques == 3:
            plt.figure()
            plt.plot(episodes, self.historique_recompenses, label="Recompense", color="green")

            # La courbe lissee aide a juger si l'agent apprend vraiment,
            # meme si certaines recompenses varient beaucoup.
            moyenne = self.moyenne_glissante(self.historique_recompenses, window=10)
            plt.plot(episodes, moyenne, label="Moyenne glissante (10)", color="red")
            plt.xlabel("Episode")
            plt.ylabel("Recompense")
            plt.title("Recompense par episode (+ moyenne glissante)")
            plt.legend()
            plt.grid(True)
            plt.show()
        elif graphiques == 4:
            plt.figure(figsize=(12, 6))

            plt.subplot(1, 3, 1)
            plt.plot(episodes, self.historique_epsilons, label="Epsilon")
            plt.xlabel("Episode")
            plt.ylabel("Valeur")
            plt.title("Evolution de l'epsilon")
            plt.grid(True)

            plt.subplot(1, 3, 2)
            plt.plot(episodes, self.historique_etapes, label="Etapes", color="orange")
            plt.xlabel("Episode")
            plt.ylabel("Nombre d'etapes")
            plt.title("Etapes par episode")
            plt.grid(True)

            plt.subplot(1, 3, 3)
            plt.plot(episodes, self.historique_recompenses, label="Recompense", color="green")
            plt.xlabel("Episode")
            plt.ylabel("Recompense")
            plt.title("Recompense par episode")
            plt.grid(True)

            plt.tight_layout()
            plt.show()
        elif graphiques == 5:
            plt.figure()
            plt.bar(self.compteur_actions.keys(), self.compteur_actions.values(), color="purple")
            plt.xlabel("Action")
            plt.ylabel("Nombre de fois choisie")
            plt.title("Frequence des actions choisies")
            plt.grid(True, axis="y")
            plt.show()

    def afficher_graphiques_regroupe(self):
        if self.num_episode == 0:
            print("Aucun episode n'a encore ete lance.")
            return

        plt = self._import_matplotlib()
        episodes = list(range(1, self.num_episode + 1))

        # Ce graphe permet de comparer rapidement l'evolution
        # des trois mesures sur une seule figure.
        plt.figure(figsize=(10, 6))
        plt.plot(episodes, self.historique_epsilons, label="Epsilon", color="blue", linestyle="-")
        plt.plot(episodes, self.historique_etapes, label="Etapes", color="orange", linestyle="--")
        plt.plot(episodes, self.historique_recompenses, label="Recompense", color="green", linestyle="-.")
        plt.xlabel("Episode")
        plt.ylabel("Valeurs")
        plt.title("Evolution de l'epsilon, des etapes et des recompenses")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
