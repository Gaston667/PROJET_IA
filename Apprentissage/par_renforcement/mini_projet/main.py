import sys
from collections import Counter

import pygame

import config as cfg
from agent import QLearningAgent
from env import DrivingEnv


def create_fonts():
    return {
        "title": pygame.font.SysFont("Arial", 25, bold=True),
        "body": pygame.font.SysFont("Arial", 18),
        "small": pygame.font.SysFont("Arial", 15),
    }


def handle_quit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit


def create_screen(title):
    pygame.init()
    screen = pygame.display.set_mode((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT + cfg.HUD_HEIGHT))
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()
    fonts = create_fonts()
    return screen, clock, fonts


def summarize_window(rewards, reasons):
    if not rewards:
        return {
            "average_reward": 0.0,
            "success_rate": 0.0,
            "crash_count": 0,
            "timeout_count": 0,
        }

    count = len(rewards)
    return {
        "average_reward": sum(rewards) / count,
        "success_rate": 100.0 * reasons.get("arrivee", 0) / count,
        "crash_count": reasons.get("crash", 0),
        "timeout_count": reasons.get("timeout", 0),
    }


def run_episode(env, agent, explore, render=False, screen=None, clock=None, fonts=None, episode_index=1, stats=None):
    state = env.reset()
    done = False
    total_reward = 0.0

    while not done:
        if render:
            handle_quit()

        action = agent.choose_action(state, explore=explore)
        next_state, reward, done, info = env.step(action)
        if explore:
            agent.learn(state, action, reward, next_state, done)
        state = next_state
        total_reward += reward

        if render:
            env.draw(screen, fonts, episode_index, total_reward, agent.epsilon, stats=stats, model_loaded=not explore)
            pygame.display.flip()
            clock.tick(cfg.FPS)

    return total_reward, info


def train_agent(track_name, episodes, render_every=cfg.TRAIN_RENDER_EVERY, continue_from_saved=True):
    env = DrivingEnv(track_name=track_name)
    agent = QLearningAgent(action_count=len(cfg.ACTIONS))
    model_path = cfg.model_path_for_track(track_name)

    if continue_from_saved and model_path.exists():
        metadata = agent.load(model_path)
        print(f"Modele charge pour le circuit '{track_name}' (episodes precedents: {agent.training_episodes}).")
        if metadata:
            print(f"Ancienne meilleure moyenne: {metadata.get('best_average_reward', 'n/a')}")

    render_enabled = render_every > 0
    if render_enabled:
        screen, clock, fonts = create_screen(f"Mini Voiture RL - Entrainement - {env.track_label}")
    else:
        screen = clock = fonts = None

    recent_rewards = []
    reason_history = []
    recent_reasons = Counter()
    best_average = float("-inf")

    for episode in range(1, episodes + 1):
        should_render = render_enabled and (episode == 1 or episode == episodes or episode % render_every == 0)
        window_stats = summarize_window(recent_rewards, recent_reasons)
        total_reward, info = run_episode(
            env,
            agent,
            explore=True,
            render=should_render,
            screen=screen,
            clock=clock,
            fonts=fonts,
            episode_index=episode,
            stats=window_stats,
        )

        reason = info["reason"]
        recent_rewards.append(total_reward)
        reason_history.append(reason)
        recent_reasons[reason] += 1

        if len(recent_rewards) > cfg.STATS_WINDOW:
            recent_rewards.pop(0)
        if len(reason_history) > cfg.STATS_WINDOW:
            removed_reason = reason_history.pop(0)
            recent_reasons[removed_reason] -= 1
            if recent_reasons[removed_reason] <= 0:
                del recent_reasons[removed_reason]

        agent.end_episode()

        average_reward = sum(recent_rewards) / len(recent_rewards)
        if average_reward > best_average:
            best_average = average_reward
            agent.save(
                model_path,
                metadata={
                    "track_name": track_name,
                    "best_average_reward": round(best_average, 3),
                    "episodes_in_current_run": episode,
                },
            )

        if episode % cfg.TRAIN_PROGRESS_PRINT_EVERY == 0 or episode == 1 or episode == episodes:
            success_rate = 100.0 * recent_reasons.get("arrivee", 0) / len(recent_rewards)
            print(
                f"[{track_name}] episode {episode:4d}/{episodes} | reward {total_reward:7.1f} | "
                f"moyenne{len(recent_rewards):02d} {average_reward:7.1f} | succes {success_rate:5.1f}% | "
                f"epsilon {agent.epsilon:.3f}"
            )

    agent.save(
        model_path,
        metadata={
            "track_name": track_name,
            "best_average_reward": round(best_average, 3),
            "episodes_in_current_run": episodes,
        },
    )

    if render_enabled:
        pygame.quit()

    print(f"Modele sauvegarde dans: {model_path}")


def evaluate_agent(track_name, episodes=cfg.EVAL_EPISODES, render=False):
    model_path = cfg.model_path_for_track(track_name)
    if not model_path.exists():
        print("Aucun modele sauvegarde pour ce circuit.")
        return

    env = DrivingEnv(track_name=track_name)
    agent = QLearningAgent(action_count=len(cfg.ACTIONS))
    agent.load(model_path)
    agent.epsilon = 0.0

    if render:
        screen, clock, fonts = create_screen(f"Mini Voiture RL - Evaluation - {env.track_label}")
    else:
        screen = clock = fonts = None

    rewards = []
    reasons = Counter()

    for episode in range(1, episodes + 1):
        stats = summarize_window(rewards[-cfg.STATS_WINDOW :], reasons)
        total_reward, info = run_episode(
            env,
            agent,
            explore=False,
            render=render,
            screen=screen,
            clock=clock,
            fonts=fonts,
            episode_index=episode,
            stats=stats,
        )
        rewards.append(total_reward)
        reasons[info["reason"]] += 1

    if render:
        pygame.quit()

    average_reward = sum(rewards) / len(rewards)
    success_rate = 100.0 * reasons.get("arrivee", 0) / len(rewards)
    print(f"Evaluation du circuit '{track_name}' sur {episodes} episodes")
    print(f"- recompense moyenne : {average_reward:.2f}")
    print(f"- succes : {success_rate:.1f}%")
    print(f"- crash : {reasons.get('crash', 0)}")
    print(f"- timeout : {reasons.get('timeout', 0)}")


def demo_agent(track_name):
    model_path = cfg.model_path_for_track(track_name)
    if not model_path.exists():
        print("Aucun modele sauvegarde pour ce circuit. Lance d'abord un entrainement.")
        return

    env = DrivingEnv(track_name=track_name)
    agent = QLearningAgent(action_count=len(cfg.ACTIONS))
    metadata = agent.load(model_path)
    agent.epsilon = 0.0

    screen, clock, fonts = create_screen(f"Mini Voiture RL - Demo - {env.track_label}")
    episode = 1
    rolling_rewards = []
    rolling_reason_history = []
    rolling_reasons = Counter()

    while True:
        stats = summarize_window(rolling_rewards, rolling_reasons)
        total_reward, info = run_episode(
            env,
            agent,
            explore=False,
            render=True,
            screen=screen,
            clock=clock,
            fonts=fonts,
            episode_index=episode,
            stats=stats,
        )

        rolling_rewards.append(total_reward)
        rolling_reason_history.append(info["reason"])
        rolling_reasons[info["reason"]] += 1

        if len(rolling_rewards) > cfg.STATS_WINDOW:
            rolling_rewards.pop(0)
        if len(rolling_reason_history) > cfg.STATS_WINDOW:
            removed_reason = rolling_reason_history.pop(0)
            rolling_reasons[removed_reason] -= 1
            if rolling_reasons[removed_reason] <= 0:
                del rolling_reasons[removed_reason]

        print(
            f"Demo {episode:03d} | reward {total_reward:7.1f} | fin {info['reason']} | "
            f"circuit {metadata.get('track_name', track_name)}"
        )
        episode += 1


def reset_model(track_name):
    model_path = cfg.model_path_for_track(track_name)
    if model_path.exists():
        model_path.unlink()
        print(f"Modele supprime: {model_path}")
    else:
        print("Aucun modele a supprimer pour ce circuit.")


def print_track_info(track_name):
    env = DrivingEnv(track_name=track_name)
    print(f"Circuit courant : {env.track_label} ({track_name})")
    print(f"- depart : ({int(env.start_pos.x)}, {int(env.start_pos.y)})")
    print(f"- arrivee : {tuple(env.goal_rect)}")
    print(f"- obstacles : {len(env.obstacles)}")
    print(f"- capteurs : {len(env.sensor_angles)}")
    print(f"- actions : {len(cfg.ACTIONS)}")
    print(f"- modele : {cfg.model_path_for_track(track_name)}")


def ask_int(label, default_value):
    raw = input(f"{label} [{default_value}] : ").strip()
    if not raw:
        return default_value
    return int(raw)


def ask_yes_no(label, default=True):
    suffix = "O/n" if default else "o/N"
    raw = input(f"{label} [{suffix}] : ").strip().lower()
    if not raw:
        return default
    return raw in {"o", "oui", "y", "yes"}


def choose_track(current_track):
    print("Circuits disponibles :")
    for idx, name in enumerate(DrivingEnv.available_tracks(), start=1):
        marker = "*" if name == current_track else " "
        print(f"{marker} {idx} - {name}")

    raw = input(f"Choisis un circuit [actuel: {current_track}] : ").strip()
    if not raw:
        return current_track

    if raw.isdigit():
        index = int(raw) - 1
        tracks = DrivingEnv.available_tracks()
        if 0 <= index < len(tracks):
            return tracks[index]

    if raw in DrivingEnv.available_tracks():
        return raw

    print("Choix invalide, circuit conserve.")
    return current_track


def main():
    current_track = cfg.DEFAULT_TRACK

    while True:
        print("\n========== MINI VOITURE RL ==========")
        print(f"Circuit courant : {current_track}")
        print("1 - Entrainement rapide")
        print("2 - Entrainement personnalise")
        print("3 - Demo visuelle")
        print("4 - Evaluer le modele")
        print("5 - Changer de circuit")
        print("6 - Reinitialiser le modele du circuit")
        print("7 - Infos du circuit")
        print("0 - Quitter")

        choice = input("Ton choix : ").strip()

        if choice == "1":
            train_agent(
                track_name=current_track,
                episodes=600,
                render_every=cfg.TRAIN_RENDER_EVERY,
                continue_from_saved=True,
            )
        elif choice == "2":
            episodes = ask_int("Nombre d'episodes d'entrainement", 800)
            render_every = ask_int("Afficher un episode sur combien (0 = mode turbo)", cfg.TRAIN_RENDER_EVERY)
            continue_from_saved = ask_yes_no("Continuer a partir du modele sauvegarde", True)
            train_agent(
                track_name=current_track,
                episodes=episodes,
                render_every=max(0, render_every),
                continue_from_saved=continue_from_saved,
            )
        elif choice == "3":
            demo_agent(current_track)
        elif choice == "4":
            episodes = ask_int("Nombre d'episodes d'evaluation", cfg.EVAL_EPISODES)
            render = ask_yes_no("Afficher l'evaluation a l'ecran", False)
            evaluate_agent(current_track, episodes=episodes, render=render)
        elif choice == "5":
            current_track = choose_track(current_track)
        elif choice == "6":
            if ask_yes_no("Supprimer le modele sauvegarde de ce circuit", False):
                reset_model(current_track)
        elif choice == "7":
            print_track_info(current_track)
        elif choice == "0":
            print("Fin du programme.")
            return
        else:
            print("Choix invalide.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)
