from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"


def model_path_for_track(track_name: str) -> Path:
    return MODEL_DIR / f"q_agent_{track_name}.pkl"


DEFAULT_TRACK = "slalom"
TRACK_NAMES = ("slalom", "corridor", "chicanes")

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 640
HUD_HEIGHT = 128

CAR_RADIUS = 16
MAX_SPEED = 8.5
ACCELERATION = 0.42
BRAKE_FORCE = 0.55
FRICTION = 0.965
TURN_RATE = 8

SENSOR_MAX_DISTANCE = 190
SENSOR_ANGLES = (-85, -40, 0, 40, 85)
SENSOR_STEP = 6

MAX_STEPS_PER_EPISODE = 900
FPS = 120
TRAIN_RENDER_EVERY = 25
TRAIN_PROGRESS_PRINT_EVERY = 25
EVAL_EPISODES = 25
STATS_WINDOW = 40

ACTIONS = (
    "accelerer",
    "accelerer_gauche",
    "accelerer_droite",
    "tourner_gauche",
    "tourner_droite",
    "laisser_rouler",
    "freiner",
)

REWARD_GOAL = 240.0
REWARD_CRASH = -140.0
REWARD_TIMEOUT = -45.0
REWARD_STEP = -0.30
REWARD_STILL = -0.70
PROGRESS_SCALE = 0.55
RISK_PENALTY_SCALE = 0.30
CENTER_BONUS = 0.08

ALPHA = 0.18
GAMMA = 0.96
EPSILON_START = 1.0
EPSILON_MIN = 0.02
EPSILON_DECAY = 0.995
