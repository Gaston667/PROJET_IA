import random
import time
import numpy as np
import matplotlib.pyplot as plt
import pygame

class QAgent:
    def __init__(self, env, epsilon=0.5, gamma=0.9, alpha=0.01):
        # Parti des parametres
        self.gamma = gamma
        self.epsilon_depart = epsilon
        self.alpha = alpha
        self.epsilon = epsilon

        # Parti de l'environnement
        self.env = env
        self.position_agent = env.pos_depart
        self.actions_possibles = env.get_actions_possibles()

        # Parti des compteurs
        self.num_episode_total = 0
        self.num_episode = 0 
        self.historique_epsilons = []
        self.historique_etapes = []
        self.historique_recompenses = []
        self.compteur_actions = {action: 0 for action in self.actions_possibles}


        # Initialisation de la Q-table
        self.q_table = {}
        for etat in self.env.etats_possibles:
            for action in self.actions_possibles:
                self.q_table[(etat, action)] = 0
           
    # Fonction pour ajuster epsilon
    def ajuster_epsilon(self):
        self.epsilon = self.epsilon_depart / (1+self.alpha * self.num_episode)

    # Fonction pour reinitialiser la position de l'agent
    def reset_position(self):
        self.position_agent = self.env.pos_depart

   
    # Fonction pour choisir une action
    def choisir_action(self, etat, afficher=False):
        e = random.random()
        if e < self.epsilon:
            if afficher:
                print("\n🌟 [Exploration] État actuel : ", etat)
            action = random.choice(self.actions_possibles)
        else:
            if afficher:
                print("\n🧠 [Exploitation] État actuel : ", etat)
                
            q_values_actions = {}
            for action in self.actions_possibles:
                if afficher:
                    print(f"\nAction {action} : {self.q_table[(etat, action)]}")
                # On stocke les q_values dans le dictionnaire
                q_values_actions[action] = self.q_table[(etat, action)]
                
            # On trouve la valeur max
            valeur_max = max(q_values_actions.values())
            if afficher:
                print(f"Valeur max : {valeur_max}")
                
            meilleure_actions = []
            # On recupere toutes les actions ayant la valeur max
            for action in self.actions_possibles:
                # Si la q_value de l'action est egale a la valeur max
                if q_values_actions[action] == valeur_max:
                   # On ajoute l'action a la liste des meilleures actions
                   meilleure_actions.append(action)
                if afficher:
                    print(f"Meilleure action : {meilleure_actions}")
            # On choisit une action au hasard parmi les meilleures actions
            action = random.choice(meilleure_actions)
            if afficher:
                print(f"Action selectionnée : {action}")

            # On incremente le compteur d'actions
            self.compteur_actions[action] += 1

        return action


    # Fonction pour mettre à jour la Q-table
    def mise_a_jour_q_table(self, etat, action, recompense, nouvel_etat, terminal, afficher=False):
        # Étape 1 : calculer la valeur max Q(s', a') si ce n'est pas un état terminal
        if terminal:
            q_value_max = 0
        else:
            # On cherche la meilleure action possible depuis le nouvel état
            # q_values_actions = {}
            # for action in self.actions_possibles:
            #     # On stocke les q_values de chque action de nouvel_etat dans le dictionnaire
            #     q_values_actions[action] = self.q_table[(nouvel_etat, action)]
            # # On trouve la valeur max
            # q_value_max = max(q_values_actions.values())
            q_value_max = max([self.q_table[(nouvel_etat, a)] for a in self.actions_possibles])

        # Étape 2 : récupérer l'ancienne valeur Q(s, a)
        ancienne_q_value = self.q_table[(etat, action)]

        # Étape 3 : appliquer la formule de Q-Learning
        nouvelle_q_value = ancienne_q_value + self.alpha * (recompense + self.gamma * q_value_max - ancienne_q_value)

        # Étape 4 : mettre à jour la Q-table
        self.q_table[(etat, action)] = nouvelle_q_value

        # Affichage si demandé
        if afficher:
            print(f"\n🔄 Mise à jour de Q({etat}, {action})")
            print(f"Ancienne Q : {ancienne_q_value:.4f}")
            print(f"Recompense r : {recompense}")
            print(f"Max Q({nouvel_etat}, a') = {q_value_max:.4f}")
            print(f"Nouvelle Q : {nouvelle_q_value:.4f}")

            

    # Boucle d'apprentissage
    def boucle_dapprentissage(self, num_episodes, afficher=False, pause=1.0,
                            afficher_valeurs_finales=True, apprentissage=True, interface_graphique=None):

        for episode in range(num_episodes):
            # Réinitialisation de l'environnement
            etat = self.env.reset()
            self.position_agent = etat  # synchroniser avec agent si besoin
            compteur_etape = 0
            termine = False
            total_recompense = 0

            if afficher:
                print(f"\n🎬 ===================== DÉBUT DE L'ÉPISODE {episode + 1} =====================\n")
                print(f"🎯 Épisode n°{episode + 1} | Alpha actuel : {self.alpha:.4f}")
                print("📍 Position initiale :")
                self.env.afficher()

            while not termine:
                # Choix de l'action (epsilon-greedy)
                action = self.choisir_action(etat, afficher=afficher)

                # Application de l'action dans l'environnement
                nouvel_etat, recompense, termine = self.env.appliquer_action(action)

                
                # Mise à jour de la Q-table
                if apprentissage:
                    self.mise_a_jour_q_table(etat, action, recompense, nouvel_etat, termine, afficher=afficher)

                # Passage à l'état suivant
                etat = nouvel_etat
                compteur_etape += 1
                total_recompense += recompense

                # Affichage si activé
                if afficher:
                    self.env.afficher()
                
                if not interface_graphique:
                    time.sleep(pause)

                if interface_graphique:
                    interface_graphique.affichage_env(etape=num_episodes)
                    pygame.event.pump()
                    pygame.time.delay(pause)

                



            # Fin de l’épisode : mise à jour des compteurs
            self.num_episode += 1
            self.ajuster_epsilon()
            self.historique_epsilons.append(self.epsilon)
            self.historique_etapes.append(compteur_etape)
            self.historique_recompenses.append(total_recompense)

            if afficher:
                print("\n🎬  FIN DE L'ÉPISODE n")
                print(f"Episode {episode} est  terminé")
                print(f"\n✅ ÉPISODE SUIVANT {episode + 1}")
                print(f"🎯 Récompense totale : {total_recompense}")
                print(f"📉 Épsilon suivant : {self.epsilon:.4f}")
                print(f"🔁 Nombre d'étapes : {compteur_etape}")
                print("============================================================\n")

            print(f"Episode terminé")

        if afficher_valeurs_finales:
            print("\n📊 APPRENTISSAGE TERMINÉ")
            print(f"Épisodes totaux : {self.num_episode}")
            print(f"Dernier epsilon : {self.epsilon:.4f}")
            print("\nQ-table finale : ")
            for etat in self.env.etats_possibles:
                for action in self.actions_possibles:
                    print(f"Q({etat}, {action}) = {self.q_table[(etat, action)]:.4f}")


    def tester_agent(self, afficher=True, pause=0.5):
        etat = self.env.reset()
        self.position_agent = etat
        termine = False
        nb_etapes = 0
        total_recompense = 0

        if afficher:
            print("\n🎯 DÉBUT DU TEST")

        while not termine:
            # Pas d'exploration : on prend toujours la meilleure action
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
                time.sleep(pause)

        print(f"✅ TEST TERMINÉ en {nb_etapes} étapes | Récompense : {total_recompense}")
            
   
    def moyenne_glissante(self,data, window=10):
       resultat = []
       for i in range(len(data)):
            # Début de la fenêtre (ne pas dépasser le début de la liste)
            debut = max(0, i - window + 1)
            fenetre = data[debut:i+1]
            moyenne = sum(fenetre) / len(fenetre)
            resultat.append(moyenne)
       return resultat

        
    # EN TROIS GRAPHIQUES

    def afficher_graphiques(self, Graphiques=0):
        episodes = list(range(1, self.num_episode + 1))

        if Graphiques == 0:
            # Graphe 1 : évolution de l’epsilon
            plt.figure()
            plt.plot(episodes, self.historique_epsilons, label="Épsilon")
            plt.xlabel("Épisode")
            plt.ylabel("Valeur de l'épsilon")
            plt.title("Évolution de l'épsilon")
            plt.grid(True)
            plt.show()

            #Graphe 2 : nombre d'étapes
            plt.figure()
            plt.plot(episodes, self.historique_etapes, label="Nombre d'étapes", color="orange")
            plt.xlabel("Épisode")
            plt.ylabel("Étapes")
            plt.title("Étapes par épisode")
            plt.grid(True)
            plt.show()

            # Graphe 3 : récompense
            plt.figure()
            plt.plot(episodes, self.historique_recompenses, label="Récompense", color="green")
            plt.xlabel("Épisode")
            plt.ylabel("Récompense")
            plt.title("Récompense par épisode")
            plt.grid(True)
            plt.show()
        
        elif Graphiques == 1:
            # Graphe 1 : évolution de l’epsilon
            plt.figure()
            plt.plot(episodes, self.historique_epsilons, label="Épsilon")
            plt.xlabel("Épisode")
            plt.ylabel("Valeur de l'épsilon")
            plt.title("Évolution de l'épsilon")
            plt.grid(True)
            plt.show()
        
        elif Graphiques == 2:
            # Graphe 2 : nombre d'étapes
            plt.figure()
            plt.plot(episodes, self.historique_etapes, label="Nombre d'étapes", color="orange")
            plt.xlabel("Épisode")
            plt.ylabel("Étapes")
            plt.title("Étapes par épisode")
            plt.grid(True)
            plt.show()
        
        elif Graphiques == 3:
            # Graphe 3 : récompense
            # plt.figure()
            # plt.plot(episodes, self.historique_recompenses, label="Récompense", color="green")
            # plt.xlabel("Épisode")
            # plt.ylabel("Récompense")
            # plt.title("Récompense par épisode")
            # plt.grid(True)
            # plt.show()
            # Graphe 3 : récompense + moyenne glissante
            plt.figure()
            plt.plot(episodes, self.historique_recompenses, label="Récompense", color="green")
            
            moy_glissante = self.moyenne_glissante(self.historique_recompenses, window=10)
            plt.plot(episodes, moy_glissante, label="Moyenne glissante (10)", color="red")
                
            plt.xlabel("Épisode")
            plt.ylabel("Récompense")
            plt.title("Récompense par épisode (+ moyenne glissante)")
            plt.legend()
            plt.grid(True)
            plt.show()


        elif Graphiques == 4:
            plt.figure(figsize=(12, 6))

            # Epsilon
            plt.subplot(1, 3, 1)
            plt.plot(episodes, self.historique_epsilons, label="Épsilon")
            plt.xlabel("Épisode")
            plt.ylabel("Valeur")
            plt.title("Évolution de l'épsilon")
            plt.grid(True)

            # Étapes
            plt.subplot(1, 3, 2)
            plt.plot(episodes, self.historique_etapes, label="Étapes", color="orange")
            plt.xlabel("Épisode")
            plt.ylabel("Nombre d'étapes")
            plt.title("Étapes par épisode")
            plt.grid(True)

            # Récompense
            plt.subplot(1, 3, 3)
            plt.plot(episodes, self.historique_recompenses, label="Récompense", color="green")
            plt.xlabel("Épisode")
            plt.ylabel("Récompense")
            plt.title("Récompense par épisode")
            plt.grid(True)

            plt.tight_layout()
            plt.show()

        elif Graphiques == 5:
            # Graphe 5 : nombre de fois que chaque action a été choisie
            plt.figure()
            plt.bar(self.compteur_actions.keys(), self.compteur_actions.values(), color="purple")
            plt.xlabel("Action")
            plt.ylabel("Nombre de fois choisie")
            plt.title("Fréquence des actions choisies")
            plt.grid(True, axis='y')
            plt.show()

    
    def afficher_graphiques_regroupe(self):
        episodes = list(range(1, self.num_episode + 1))

        plt.figure(figsize=(10, 6))
        
        # Courbe de l'épsilon
        plt.plot(episodes, self.historique_epsilons, label="Épsilon", color="blue", linestyle='-')

        # Courbe des étapes
        plt.plot(episodes, self.historique_etapes, label="Étapes", color="orange", linestyle='--')

        # Courbe des récompenses
        plt.plot(episodes, self.historique_recompenses, label="Récompense", color="green", linestyle='-.')

        plt.xlabel("Épisode")
        plt.ylabel("Valeurs")
        plt.title("Évolution de l'épsilon, des étapes et des récompenses")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

