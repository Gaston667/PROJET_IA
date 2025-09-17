from GrildWord import GridWorld
from QAgent import QAgent
from InterfaceGrille import InterfaceGrillePygame

def main():
    # Création de l'environnement
    env = GridWorld()
    agent = QAgent(env, epsilon=0.1, gamma=0.9, alpha=0.1)


    while True:
        print("\n==================== MENU Q-LEARNING ====================")
        print("0 - Quitter")
        print("1 - 1 épisode, affichage actif (démo)")
        print("2 - 100 épisodes, affichage désactivé (rapide)")
        print("3 - 1000 épisodes, affichage désactivé (rapide)")
        print("4 - 100 épisodes, affichage + détails (complet)")
        print("5 - Entrer manuellement le nombre d'épisodes")
        print("6 - Tester l'agent (sans exploration)")

        print("=========== MENU GRAPHIQUES ============")
        print("7 - Afficher les graphiques")
        print("8 - Afficher les graphiques regroupés")
        print("9 - Afficher Grphiques epsilon")
        print("10 - Afficher Grphiques etapes")
        print("11 - Afficher Grphiques recompenses")
        print("12 - Afficher Grphiques Trois en un")
        print("13 - Afficher Grphiques actions")
        

        print("=========== MENU INTERFACE ============")
        print("14 - Interface Grille")
        print("========================================================")

        choix = input("👉 Ton choix : ").strip()

        if choix == '1':
            nb_episodes = 1
            afficher = True
            pause = 0.5  # 2 secondes de pause pour l'option 1
        elif choix == '2':
            nb_episodes = 100
            afficher = False
            pause = 0    # Pas de pause pour les options rapides
        elif choix == '3':
            nb_episodes = 1000
            afficher = False
            pause = 0    # Pas de pause pour les options rapides
        elif choix == '4':
            nb_episodes = 100
            afficher = True
            pause = 2.0  # 2 secondes de pause pour l'option 4
        elif choix == '5':
            nb_episodes = int(input("Nombre d'épisodes : "))
            afficher = False
            pause = 2.0  # 2 secondes de pause pour l'option 5
        elif choix == '6':
            print("\n🎯 Test de l'agent (epsilon = 0.0, pas d'exploration)\n")
            agent.tester_agent(afficher=True, pause=2.0)  # 2 secondes de pause pour le test
            continue  # ne quitte pas le programme après le test
        elif choix == '7':
            agent.afficher_graphiques()
            continue
        elif choix == '8':
            agent.afficher_graphiques_regroupe()
            continue
        elif choix == '9':
            agent.afficher_graphiques(Graphiques=1)
            continue
        elif choix == '10':
            agent.afficher_graphiques(Graphiques=2)
            continue
        elif choix == '11':
            agent.afficher_graphiques(Graphiques=3)
            continue
        elif choix == '12':
            agent.afficher_graphiques(Graphiques=4)
            continue
        elif choix == '13':
            agent.afficher_graphiques(Graphiques=5)
            continue
        elif choix == '14':
            pause = 300
            nb_episodes = int(input("Nombre d'épisodes : "))

            interface = InterfaceGrillePygame(env, agent, cell_size=40)
            agent.boucle_dapprentissage(
                num_episodes=nb_episodes,
                afficher=True,
                pause=pause,  # Utilisation de la pause définie plus haut
                afficher_valeurs_finales=False,
                apprentissage=True,
                interface_graphique=interface
            )
            interface.fermer()
            continue
        elif choix == '0':
            print("👋 Fin du programme.")
            break
        else:
            print("❌ Choix invalide. Réessaie.")
            continue

        # Lancer apprentissage
        agent.boucle_dapprentissage(
            num_episodes=nb_episodes,
            afficher=afficher,
            pause=pause,  # Utilisation de la pause définie plus haut
            afficher_valeurs_finales=False,
            apprentissage=True
        )

       
if __name__ == "__main__":
    main()
