import random
import time

class TDAgent:
    def __init__(self, environnement, alpha=0.2, decay_rate=0.01, gamma=0.9):
        self.env = environnement
        self.actions_possibles = ['haut', 'bas', 'gauche', 'droite']
        self.alpha_initial = alpha
        self.decay_rate = decay_rate
        self.alpha = alpha
        self.gamma = gamma
        self.num_episode = 0  # compteur d’épisodes
        self.historique_etapes = []  # Pour suivre l'évolution des étapes
        self.historique_V0 = []  # Pour suivre l'évolution de V[(0, 0)]
        self.V = {}  # Valeurs d'état sorti de la value function
        self.historique_epsilons = []  # Pour suivre l'évolution de epsilon

        self.V[self.env.pos_objectif] = 100
        for mur in self.env.murs:
            self.V[mur] = -10

    def ajuster_alpha(self):
        self.alpha = self.alpha_initial / (1 + self.decay_rate * self.num_episode)


    def choisir_action(self, etat, afficher):
        e = random.random()
        if e < self.alpha:
            if afficher:
                print(f"\n🌟 [Exploration] État actuel : {etat}")
                print("    → Choix d'une action aléatoire.")
            return random.choice(self.actions_possibles)
        else:
            meilleure_actions = []
            meilleure_valeur = float('-inf')

            if afficher:
                print(f"\n🧠 [Exploitation] État actuel : {etat}")
                print("    → Recherche de l'action menant au meilleur état suivant.")
                print("--------------------------------------------------------------")

            for action in self.actions_possibles:
                ligne, colonne = etat
                etat_suivant = etat  # Valeur par défaut si action invalide

                # Simuler l'état suivant
                if action == 'haut' and ligne > 0:
                    etat_suivant = (ligne - 1, colonne)
                elif action == 'bas' and ligne < self.env.taille - 1:
                    etat_suivant = (ligne + 1, colonne)
                elif action == 'gauche' and colonne > 0:
                    etat_suivant = (ligne, colonne - 1)
                elif action == 'droite' and colonne < self.env.taille - 1:
                    etat_suivant = (ligne, colonne + 1)

                if etat_suivant == etat:
                    if afficher:
                        print(f"❌ Action '{action}' ignorée : elle ne change pas l'état.")
                    continue

                valeur = self.V.get(etat_suivant, 0)

                if afficher:
                    print(f"➡️  Action '{action}' → État {etat_suivant} | Valeur estimée : V(s') = {valeur:.2f}")

                if valeur > meilleure_valeur:
                    meilleure_valeur = valeur
                    meilleure_actions = [action]
                elif valeur == meilleure_valeur:
                    meilleure_actions.append(action)

                if afficher:
                    print(f"    🔹 Actions les plus prometteuses jusqu'ici : {meilleure_actions}")
                    print("--------------------------------------------------------------")

            if afficher:
                print(f"\n🏁 Fin de l'évaluation.")
                print(f"    ✔️  Meilleure valeur rencontrée : {meilleure_valeur:.2f}")
                print(f"    🎯 Action sélectionnée : {random.choice(meilleure_actions) if meilleure_actions else 'aléatoire'}")
                print("==============================================================\n")

            return random.choice(meilleure_actions) if meilleure_actions else random.choice(self.actions_possibles)


            
    def mettre_a_jour(self, etat, recompense, nouvel_etat, afficher=False):
        ancienne_valeur = self.V.get(etat, 0)
        valeur_suivante = self.V.get(nouvel_etat, 0)

        if afficher:
            print(f"Formule TD simplifiée : V({etat}) = V({etat}) + α * (R + V({nouvel_etat}) - V({etat}))")

        cible = recompense + valeur_suivante
        #nouvelle_valeur = self.alpha * (cible - ancienne_valeur)
        nouvelle_valeur = ancienne_valeur + self.alpha * (cible - ancienne_valeur)

        if afficher:
            print(f"Nouvelle valeur de V({etat}) : {nouvelle_valeur}")

        self.V[etat] = nouvelle_valeur


    def jouer_episode(self, afficher=True, pause=1.0, afficher_valeurs_intermediaires=False, afficher_valeurs_finales=True,
        apprentissage=True,
        afficher_detail=False
    ):
        etat = self.env.reinitialiser()
        termine = False
        total_recompense = 0
        etape = 0
        self.num_episode += 1
        self.ajuster_alpha()

        if afficher:
            print("\n🎬 ===================== DÉBUT DE L'ÉPISODE =====================\n")
            print(f"🎯 Épisode n°{self.num_episode} | Alpha actuel : {self.alpha:.4f}")
            print("📍 Position initiale :")
            self.env.afficher()

        while not termine:
            print(f"\n🔁 ÉTAPE {etape + 1}")
            print(f"📍 État actuel : {etat}")

            action = self.choisir_action(etat, afficher=afficher_detail)
            nouvel_etat, recompense, termine = self.env.appliquer(action)

            if apprentissage:
                self.mettre_a_jour(etat, recompense, nouvel_etat, afficher=afficher_detail)

            total_recompense += recompense
            etat = nouvel_etat

            if afficher:
                print(f"\n➡️  Action choisie : {action}")
                print("🗺️  Grille après l'action :")
                self.env.afficher()

                if afficher_valeurs_intermediaires:
                    print("📈 Valeurs estimées intermédiaires :")
                    self.afficher_valeurs_intermediaires(etape)

                time.sleep(pause)

            etape += 1

        print(f"\n✅ ÉPISODE TERMINÉ | Récompense totale : {total_recompense}")
        print("📌 Nombre d'étapes : ", etape)

        if afficher_valeurs_finales:
            print("\n📊 Valeurs finales V(s) après l'épisode :")
            self.afficher_valeurs_finales()


        self.historique_V0.append(self.V.get((2, 1), 0))

        print("🧠 Apprentissage terminé pour cet épisode.")
        print("===================================================\n")

        self.historique_etapes.append(etape)
        if hasattr(self, "historique_epsilons"):
            self.historique_epsilons.append(self.alpha)  # ou epsilon si tu le calcules ailleurs

        return total_recompense


    def afficher_valeurs_intermediaires(self, etape):
        print(f"\n🌀 Valeurs estimées V(s) à l'étape {etape} :")
        for i in range(self.env.taille):
            ligne = ""
            for j in range(self.env.taille):
                pos = (i, j)
                val = self.V.get(pos, 0)
                ligne += f"{val:5.1f} ".center(7)
            print(ligne)
        print("-" * 40)
        
    def afficher_valeurs_finales(self):
        print("\n✅ Valeurs finales V(s) après l'épisode :")
        for i in range(self.env.taille):
            ligne = ""
            for j in range(self.env.taille):
                pos = (i, j)
                if pos in self.env.murs:
                    ligne += " MUR ".center(7)
                else:
                    val = self.V.get(pos, 0)
                    ligne += f"{val:5.1f} ".center(7)
            print(ligne)
        print("=" * 40)


