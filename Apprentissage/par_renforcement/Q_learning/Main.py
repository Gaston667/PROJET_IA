from GrildWord import GridWorld
from QAgent import QAgent


def menu_graphiques(agent):
    print("\n=========== MENU GRAPHIQUES ===========")
    print("1 - Tous les graphiques")
    print("2 - Graphiques regroupes")
    print("3 - Epsilon")
    print("4 - Etapes")
    print("5 - Recompenses")
    print("6 - Trois en un")
    print("7 - Actions")
    print("0 - Retour")

    choix = input("Ton choix graphique : ").strip()

    if choix == "1":
        agent.afficher_graphiques()
    elif choix == "2":
        agent.afficher_graphiques_regroupe()
    elif choix == "3":
        agent.afficher_graphiques(graphiques=1)
    elif choix == "4":
        agent.afficher_graphiques(graphiques=2)
    elif choix == "5":
        agent.afficher_graphiques(graphiques=3)
    elif choix == "6":
        agent.afficher_graphiques(graphiques=4)
    elif choix == "7":
        agent.afficher_graphiques(graphiques=5)
    elif choix != "0":
        print("Choix invalide. Reessaie.")


def main():
    print("Mode obstacle : 0 = penalite simple | 1 = fin d'episode | 2 = retour au depart")
    mode_obstacle = input("Choisis le mode obstacle (defaut 1) : ").strip()
    if mode_obstacle not in {"0", "1", "2"}:
        mode_obstacle = "1"

    # L'environnement definit les regles du monde,
    # l'agent apprend a y agir.
    env = GridWorld(mode_obstacle=int(mode_obstacle))
    agent = QAgent(env, epsilon=0.1, gamma=0.9, alpha=0.1)

    while True:
        print("\n================ MENU Q-LEARNING ================")
        print("0 - Quitter")
        print("1 - Demo (1 episode, affichage actif)")
        print("2 - Entrainement rapide (100 episodes)")
        print("3 - Entrainement long (1000 episodes)")
        print("4 - Entrainement personnalise")
        print("5 - Tester l'agent")
        print("6 - Graphiques")
        print("7 - Interface grille")
        print("=================================================")

        choix = input("Ton choix : ").strip()

        # Le menu principal:
        # apprendre, tester, visualiser, ou quitter.
        if choix == "1":
            nb_episodes = 1
            afficher = True
            pause = 0.5
        elif choix == "2":
            nb_episodes = 100
            afficher = False
            pause = 0
        elif choix == "3":
            nb_episodes = 1000
            afficher = False
            pause = 0
        elif choix == "4":
            nb_episodes = int(input("Nombre d'episodes : "))
            mode_affichage = input("Afficher les details ? (o/n) : ").strip().lower()
            afficher = mode_affichage == "o"
            pause = 0.5 if afficher else 0
        elif choix == "5":
            print("\nTest de l'agent (epsilon = 0.0, pas d'exploration)\n")
            agent.tester_agent(afficher=True, pause=2.0)
            continue
        elif choix == "6":
            menu_graphiques(agent)
            continue
        elif choix == "7":
            nb_episodes = int(input("Nombre d'episodes : "))

            # L'import de pygame reste local a l'option interface pour que
            # le mode console fonctionne meme si pygame n'est pas installe.
            try:
                from InterfaceGrille import InterfaceGrillePygame
            except ModuleNotFoundError as exc:
                raise ModuleNotFoundError(
                    "pygame n'est pas installe. Execute: py -3.13 -m pip install pygame"
                ) from exc

            interface = InterfaceGrillePygame(env, agent, cell_size=40)
            agent.boucle_dapprentissage(
                num_episodes=nb_episodes,
                afficher=False,
                pause=300,  # milliseconds pour l'interface pygame
                afficher_valeurs_finales=False,
                apprentissage=True,
                interface_graphique=interface,
            )
            interface.fermer()
            continue
        elif choix == "0":
            print("Fin du programme.")
            break
        else:
            print("Choix invalide. Reessaie.")
            continue

        agent.boucle_dapprentissage(
            num_episodes=nb_episodes,
            afficher=afficher,
            pause=pause,
            afficher_valeurs_finales=False,
            apprentissage=True,
        )


if __name__ == "__main__":
    main()
