# main.py

from GrildWord import GridWorld
from TDAgent import TDAgent
from InterfaceGrille import InterfaceGrille
import matplotlib.pyplot as plt

def boucle_dentrainement_terminal(agent):
    while True:
        print("\n=== MENU D'ENTRAÎNEMENT ===")
        print("1. Lancer 1 épisode")
        print("2. Lancer 10 épisodes")
        print("3. Lancer 100 épisodes")
        print("4. Lancer 1000 épisodes")
        print("5. Lancer 10000 épisodes")
        print("6. Afficher les valeurs actuelles de V(s)")
        print("7. Lancer 1 épisode en mode affichage (étape par étape)")
        print("8. 📈 Afficher graphique V[(0,0)]")
        print("9. 📉 Afficher graphique étapes par épisode")
        print("10. 🧪 Afficher graphique ε (alpha) par épisode")
        
        print("0. Quitter")

        choix = input("👉 Que veux-tu faire ? ")

        if choix == "1":
            agent.jouer_episode(afficher=True, afficher_valeurs_finales=True, afficher_detail=True)

        elif choix == "2":
            for _ in range(10):
                agent.jouer_episode(afficher=False, afficher_valeurs_finales=False)

        elif choix == "3":
            for _ in range(100):
                agent.jouer_episode(afficher=False, pause=0.0, afficher_valeurs_finales=False)

        elif choix == "4":
            for _ in range(1000):
                agent.jouer_episode(afficher=False, pause=0.0, afficher_valeurs_finales=False)

        elif choix == "5":
            for _ in range(10000):
                agent.jouer_episode(afficher=False, pause=0.0, afficher_valeurs_finales=False)

        elif choix == "6":
            agent.afficher_valeurs_finales()

        elif choix == "7":
            print("\n🎯 TEST FINAL (ce que l'agent a appris)")
            agent.jouer_episode(
                afficher=True,
                pause=1.0,
                afficher_valeurs_finales=True,
                afficher_detail=True,
                apprentissage=False
            )

        elif choix == "8":
            if agent.historique_V0:
                plt.figure()
                plt.plot(agent.historique_V0)
                plt.title("Évolution de V[(0, 0)] au fil des épisodes")
                plt.xlabel("Épisode")
                plt.ylabel("Valeur estimée")
                plt.grid(True)
                plt.show()
            else:
                print("⚠️ Pas encore de données disponibles pour V[(0,0)]")

        elif choix == "9":
            if agent.historique_etapes:
                plt.figure()
                plt.plot(agent.historique_etapes)
                plt.title("Nombre d'étapes pour atteindre la sortie")
                plt.xlabel("Épisode")
                plt.ylabel("Nombre d'étapes")
                plt.grid(True)
                plt.show()
            else:
                print("⚠️ Pas encore d'épisodes joués pour tracer les étapes.")


        elif choix == "10":
            if agent.historique_epsilons:
                plt.figure()
                plt.plot(agent.historique_epsilons)
                plt.title("Évolution de ε (alpha) au fil des épisodes")
                plt.xlabel("Épisode")
                plt.ylabel("ε / alpha")
                plt.grid(True)
                plt.show()
            else:
                print("⚠️ Pas encore d'épisodes joués pour tracer epsilon.")



        elif choix == "0":
            print("👋 Fin de l'entraînement.")
            break

        else:
            print("⛔ Option invalide. Essaie encore.")

  

def main():
    print("=== Choisissez le mode d'exécution ===")
    print("1 - Mode terminal (console)")
    print("2 - Mode interface graphique (Tkinter)")
    choix = input("Votre choix (1 ou 2) : ").strip()

    env = GridWorld()
    agent = TDAgent(env, alpha=0.5)

    if choix == "1":
        boucle_dentrainement_terminal(agent)

        # # 🔍 Afficher une courbe de l'évolution si V0 a été suivi
        # if hasattr(agent, "historique_V0"):
        #     plt.plot(agent.historique_V0)
        #     plt.title("Évolution de V[(0, 0)] au fil des épisodes")
        #     plt.xlabel("Épisode")
        #     plt.ylabel("Valeur estimée")
        #     plt.grid(True)
        #     plt.show()
    
        # ➕ Affichage du nombre d'étapes pour atteindre le but
        if hasattr(agent, "historique_etapes"):
            plt.figure()
            plt.plot(agent.historique_etapes, color="black")
            plt.title("Q-Learning – nombre d’itérations pour atteindre la sortie")
            plt.xlabel("Épisode")
            plt.ylabel("Nombre d’itérations")
            plt.grid(True)
            plt.show()


    elif choix == "2":
        InterfaceGrille(env, agent)

    else:
        print("Choix invalide. Veuillez entrer 1 ou 2.")

if __name__ == "__main__":
    main()
