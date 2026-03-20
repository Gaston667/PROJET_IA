import pickle
import random
from collections import defaultdict

import config as cfg


class QLearningAgent:
    def __init__(
        self,
        action_count,
        alpha=cfg.ALPHA,
        gamma=cfg.GAMMA,
        epsilon=cfg.EPSILON_START,
        epsilon_min=cfg.EPSILON_MIN,
        epsilon_decay=cfg.EPSILON_DECAY,
    ):
        self.action_count = action_count
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.initial_epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.training_episodes = 0
        self.q_table = defaultdict(float)

    def q_values_for_state(self, state):
        return [self.q_table[(state, action)] for action in range(self.action_count)]

    def choose_action(self, state, explore=True):
        if explore and random.random() < self.epsilon:
            return random.randrange(self.action_count)

        q_values = self.q_values_for_state(state)
        best_value = max(q_values)
        best_actions = [idx for idx, value in enumerate(q_values) if value == best_value]
        return random.choice(best_actions)

    def learn(self, state, action, reward, next_state, done):
        old_value = self.q_table[(state, action)]
        if done:
            next_best = 0.0
        else:
            next_best = max(self.q_values_for_state(next_state))

        target = reward + self.gamma * next_best
        self.q_table[(state, action)] = old_value + self.alpha * (target - old_value)

    def end_episode(self):
        self.training_episodes += 1
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def reset_training(self):
        self.q_table = defaultdict(float)
        self.epsilon = self.initial_epsilon
        self.training_episodes = 0

    def save(self, path, metadata=None):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as file:
            pickle.dump(
                {
                    "q_table": dict(self.q_table),
                    "epsilon": self.epsilon,
                    "alpha": self.alpha,
                    "gamma": self.gamma,
                    "epsilon_min": self.epsilon_min,
                    "epsilon_decay": self.epsilon_decay,
                    "training_episodes": self.training_episodes,
                    "metadata": metadata or {},
                },
                file,
            )

    def load(self, path):
        with path.open("rb") as file:
            data = pickle.load(file)

        self.q_table = defaultdict(float, data.get("q_table", {}))
        self.epsilon = data.get("epsilon", self.epsilon)
        self.alpha = data.get("alpha", self.alpha)
        self.gamma = data.get("gamma", self.gamma)
        self.epsilon_min = data.get("epsilon_min", self.epsilon_min)
        self.epsilon_decay = data.get("epsilon_decay", self.epsilon_decay)
        self.training_episodes = data.get("training_episodes", 0)
        return data.get("metadata", {})
