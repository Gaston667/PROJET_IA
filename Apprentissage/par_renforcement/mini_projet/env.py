from math import sin

import pygame

import config as cfg


class DrivingEnv:
    TRACKS = {
        "slalom": {
            "label": "Slalom",
            "start_pos": (78, 560),
            "start_angle": 0,
            "goal_rect": (782, 56, 80, 80),
            "obstacles": [
                (180, 0, 70, 430),
                (345, 210, 72, 430),
                (510, 0, 72, 430),
                (675, 210, 70, 430),
            ],
            "accent": (84, 166, 255),
        },
        "corridor": {
            "label": "Corridor",
            "start_pos": (88, 570),
            "start_angle": -10,
            "goal_rect": (770, 54, 90, 90),
            "obstacles": [
                (0, 120, 680, 60),
                (220, 260, 680, 60),
                (0, 400, 680, 60),
                (120, 520, 60, 120),
            ],
            "accent": (108, 217, 170),
        },
        "chicanes": {
            "label": "Chicanes",
            "start_pos": (92, 565),
            "start_angle": -8,
            "goal_rect": (770, 58, 92, 82),
            "obstacles": [
                (170, 0, 60, 250),
                (170, 360, 60, 280),
                (350, 160, 60, 480),
                (530, 0, 60, 260),
                (530, 360, 60, 280),
                (700, 170, 60, 470),
            ],
            "accent": (243, 182, 76),
        },
    }

    def __init__(self, track_name=cfg.DEFAULT_TRACK):
        self.width = cfg.WINDOW_WIDTH
        self.height = cfg.WINDOW_HEIGHT
        self.sensor_angles = cfg.SENSOR_ANGLES
        self.max_steps = cfg.MAX_STEPS_PER_EPISODE
        self.action_names = cfg.ACTIONS
        self.track_name = track_name if track_name in self.TRACKS else cfg.DEFAULT_TRACK
        self.last_reason = "pret"
        self.trail = []
        self.set_track(self.track_name)

    @classmethod
    def available_tracks(cls):
        return tuple(cls.TRACKS.keys())

    def set_track(self, track_name):
        data = self.TRACKS[track_name]
        self.track_name = track_name
        self.track_label = data["label"]
        self.start_pos = pygame.Vector2(data["start_pos"])
        self.start_angle = data["start_angle"]
        self.goal_rect = pygame.Rect(data["goal_rect"])
        self.obstacles = [pygame.Rect(rect) for rect in data["obstacles"]]
        self.track_accent = data["accent"]
        self.max_goal_distance = self.start_pos.distance_to(pygame.Vector2(self.goal_rect.center))
        self.reset()

    def reset(self):
        self.car_pos = self.start_pos.copy()
        self.car_angle = self.start_angle
        self.car_speed = 0.0
        self.step_count = 0
        self.last_reason = "en_cours"
        self.trail = [self.car_pos.copy()]
        self.previous_goal_distance = self._distance_to_goal(self.car_pos)
        return self.get_state()

    def get_state(self):
        sensor_values = [self._sensor_distance(offset) for offset in self.sensor_angles]
        sensor_buckets = tuple(self._distance_bucket(value) for value in sensor_values)
        orientation_bucket = self._orientation_bucket()
        speed_bucket = self._speed_bucket()
        goal_bucket = self._goal_distance_bucket()
        return sensor_buckets + (orientation_bucket, speed_bucket, goal_bucket)

    def step(self, action):
        self.step_count += 1
        old_pos = self.car_pos.copy()
        self._apply_action(action)

        heading = pygame.Vector2(1, 0).rotate(-self.car_angle)
        new_pos = self.car_pos + heading * self.car_speed

        reward = cfg.REWARD_STEP
        done = False
        reason = "en_cours"

        if self._is_collision(new_pos):
            self.car_pos = new_pos
            reward += cfg.REWARD_CRASH
            done = True
            reason = "crash"
        else:
            self.car_pos = new_pos
            self._push_trail(new_pos)

            old_distance = self.previous_goal_distance
            new_distance = self._distance_to_goal(self.car_pos)
            progress = old_distance - new_distance
            reward += progress * cfg.PROGRESS_SCALE
            self.previous_goal_distance = new_distance

            min_sensor = min(self._sensor_distance(offset) for offset in self.sensor_angles)
            risk_ratio = 1.0 - min_sensor / cfg.SENSOR_MAX_DISTANCE
            reward -= max(0.0, risk_ratio) * cfg.RISK_PENALTY_SCALE
            reward += self._heading_bonus() * cfg.CENTER_BONUS

            if self.goal_rect.collidepoint(self.car_pos.x, self.car_pos.y):
                reward += cfg.REWARD_GOAL
                done = True
                reason = "arrivee"

        if old_pos.distance_to(self.car_pos) < 0.3:
            reward += cfg.REWARD_STILL

        if not done and self.step_count >= self.max_steps:
            reward += cfg.REWARD_TIMEOUT
            done = True
            reason = "timeout"

        self.last_reason = reason
        info = {
            "reason": reason,
            "distance_to_goal": self._distance_to_goal(self.car_pos),
            "speed": self.car_speed,
            "track": self.track_name,
            "steps": self.step_count,
        }
        return self.get_state(), reward, done, info

    def _apply_action(self, action):
        if action == 0:
            self._accelerate(cfg.ACCELERATION)
        elif action == 1:
            self._turn(-1)
            self._accelerate(cfg.ACCELERATION * 0.9)
        elif action == 2:
            self._turn(1)
            self._accelerate(cfg.ACCELERATION * 0.9)
        elif action == 3:
            self._turn(-1)
        elif action == 4:
            self._turn(1)
        elif action == 6:
            self.car_speed = max(0.0, self.car_speed - cfg.BRAKE_FORCE)

        self.car_speed *= cfg.FRICTION
        if self.car_speed < 0.03:
            self.car_speed = 0.0

    def _accelerate(self, amount):
        self.car_speed = min(cfg.MAX_SPEED, self.car_speed + amount)

    def _turn(self, direction):
        steer_strength = 1.0 if self.car_speed > 1.2 else 0.7
        self.car_angle += direction * cfg.TURN_RATE * steer_strength

    def _push_trail(self, pos):
        self.trail.append(pos.copy())
        if len(self.trail) > 40:
            self.trail.pop(0)

    def _distance_to_goal(self, pos):
        goal_center = pygame.Vector2(self.goal_rect.center)
        return pos.distance_to(goal_center)

    def _distance_bucket(self, value):
        if value < cfg.SENSOR_MAX_DISTANCE * 0.18:
            return 0
        if value < cfg.SENSOR_MAX_DISTANCE * 0.38:
            return 1
        if value < cfg.SENSOR_MAX_DISTANCE * 0.62:
            return 2
        if value < cfg.SENSOR_MAX_DISTANCE * 0.85:
            return 3
        return 4

    def _speed_bucket(self):
        if self.car_speed < 1.2:
            return 0
        if self.car_speed < 3.0:
            return 1
        if self.car_speed < 5.2:
            return 2
        return 3

    def _goal_distance_bucket(self):
        ratio = self._distance_to_goal(self.car_pos) / max(1.0, self.max_goal_distance)
        if ratio < 0.20:
            return 0
        if ratio < 0.40:
            return 1
        if ratio < 0.60:
            return 2
        if ratio < 0.80:
            return 3
        return 4

    def _orientation_bucket(self):
        goal_vector = pygame.Vector2(self.goal_rect.center) - self.car_pos
        if goal_vector.length_squared() == 0:
            return 3

        heading = pygame.Vector2(1, 0).rotate(-self.car_angle)
        angle = heading.angle_to(goal_vector)

        if angle < -110:
            return 0
        if angle < -50:
            return 1
        if angle < -12:
            return 2
        if angle <= 12:
            return 3
        if angle <= 50:
            return 4
        if angle <= 110:
            return 5
        return 6

    def _heading_bonus(self):
        goal_vector = pygame.Vector2(self.goal_rect.center) - self.car_pos
        if goal_vector.length_squared() == 0:
            return 1.0

        heading = pygame.Vector2(1, 0).rotate(-self.car_angle)
        angle = abs(heading.angle_to(goal_vector))
        return max(0.0, 1.0 - angle / 180.0)

    def _sensor_distance(self, relative_angle):
        direction = pygame.Vector2(1, 0).rotate(-(self.car_angle + relative_angle))
        for distance in range(0, cfg.SENSOR_MAX_DISTANCE + cfg.SENSOR_STEP, cfg.SENSOR_STEP):
            point = self.car_pos + direction * distance
            if self._point_hits_wall(point):
                return float(distance)
        return float(cfg.SENSOR_MAX_DISTANCE)

    def _point_hits_wall(self, point):
        if point.x < 0 or point.x >= self.width or point.y < 0 or point.y >= self.height:
            return True
        return any(obstacle.collidepoint(point.x, point.y) for obstacle in self.obstacles)

    def _is_collision(self, pos):
        radius = cfg.CAR_RADIUS
        if pos.x - radius < 0 or pos.x + radius > self.width or pos.y - radius < 0 or pos.y + radius > self.height:
            return True
        return any(self._circle_rect_collision(pos, radius, obstacle) for obstacle in self.obstacles)

    @staticmethod
    def _circle_rect_collision(center, radius, rect):
        closest_x = max(rect.left, min(center.x, rect.right))
        closest_y = max(rect.top, min(center.y, rect.bottom))
        dx = center.x - closest_x
        dy = center.y - closest_y
        return dx * dx + dy * dy <= radius * radius

    def draw(self, screen, fonts, episode, total_reward, epsilon, stats=None, model_loaded=False):
        self._draw_background(screen)
        self._draw_start_zone(screen)
        self._draw_goal(screen)
        self._draw_obstacles(screen)
        self._draw_trail(screen)
        self._draw_sensors(screen)
        self._draw_car(screen)
        self._draw_hud(screen, fonts, episode, total_reward, epsilon, stats or {}, model_loaded)

    def _draw_background(self, screen):
        for y in range(self.height):
            ratio = y / max(1, self.height - 1)
            color = (
                int(38 * (1 - ratio) + 24 * ratio),
                int(44 * (1 - ratio) + 29 * ratio),
                int(52 * (1 - ratio) + 36 * ratio),
            )
            pygame.draw.line(screen, color, (0, y), (self.width, y))

        road_rect = pygame.Rect(28, 28, self.width - 56, self.height - 56)
        pygame.draw.rect(screen, (215, 218, 220), road_rect, border_radius=20)
        pygame.draw.rect(screen, (244, 245, 246), road_rect.inflate(-18, -18), width=2, border_radius=18)

        for x in range(60, self.width - 60, 55):
            pygame.draw.line(screen, (235, 237, 238), (x, 30), (x, self.height - 30), 1)
        for y in range(60, self.height - 60, 55):
            pygame.draw.line(screen, (235, 237, 238), (30, y), (self.width - 30, y), 1)

    def _draw_start_zone(self, screen):
        start_rect = pygame.Rect(int(self.start_pos.x) - 35, int(self.start_pos.y) - 35, 70, 70)
        pygame.draw.rect(screen, (68, 181, 137), start_rect, border_radius=12)
        pygame.draw.rect(screen, (196, 245, 220), start_rect, width=2, border_radius=12)

    def _draw_goal(self, screen):
        pulse = 6 * (1 + sin(pygame.time.get_ticks() / 240))
        glow_rect = self.goal_rect.inflate(int(pulse), int(pulse))
        pygame.draw.rect(screen, (248, 207, 109), glow_rect, border_radius=18)
        pygame.draw.rect(screen, (227, 179, 69), self.goal_rect, border_radius=14)
        pygame.draw.rect(screen, (255, 240, 180), self.goal_rect.inflate(-20, -20), border_radius=8)

    def _draw_obstacles(self, screen):
        for obstacle in self.obstacles:
            shadow = obstacle.move(4, 4)
            pygame.draw.rect(screen, (16, 20, 27), shadow, border_radius=12)
            pygame.draw.rect(screen, (58, 66, 82), obstacle, border_radius=12)
            pygame.draw.rect(screen, self.track_accent, obstacle.inflate(-16, -16), width=2, border_radius=8)

    def _draw_trail(self, screen):
        if len(self.trail) < 2:
            return

        for idx in range(1, len(self.trail)):
            alpha = idx / len(self.trail)
            color = (
                int(self.track_accent[0] * alpha),
                int(self.track_accent[1] * alpha),
                int(self.track_accent[2] * alpha),
            )
            pygame.draw.line(screen, color, self.trail[idx - 1], self.trail[idx], 3)

    def _draw_sensors(self, screen):
        sensor_colors = [
            (245, 113, 113),
            (255, 171, 87),
            (104, 182, 255),
            (118, 224, 181),
            (191, 145, 255),
        ]
        for idx, relative_angle in enumerate(self.sensor_angles):
            direction = pygame.Vector2(1, 0).rotate(-(self.car_angle + relative_angle))
            distance = self._sensor_distance(relative_angle)
            end_point = self.car_pos + direction * distance
            pygame.draw.line(screen, sensor_colors[idx], self.car_pos, end_point, 2)
            pygame.draw.circle(screen, sensor_colors[idx], (int(end_point.x), int(end_point.y)), 4)

    def _draw_car(self, screen):
        forward = pygame.Vector2(1, 0).rotate(-self.car_angle)
        left = forward.rotate(140)
        right = forward.rotate(-140)

        nose = self.car_pos + forward * (cfg.CAR_RADIUS + 8)
        back_left = self.car_pos + left * cfg.CAR_RADIUS
        back_right = self.car_pos + right * cfg.CAR_RADIUS

        shadow_points = [point + pygame.Vector2(3, 4) for point in (nose, back_left, back_right)]
        pygame.draw.polygon(screen, (17, 22, 29), shadow_points)
        pygame.draw.polygon(screen, self.track_accent, [nose, back_left, back_right])
        pygame.draw.polygon(screen, (232, 243, 255), [nose, back_left, back_right], width=2)
        pygame.draw.circle(screen, (19, 27, 39), (int(self.car_pos.x), int(self.car_pos.y)), 5)

    def _draw_hud(self, screen, fonts, episode, total_reward, epsilon, stats, model_loaded):
        panel = pygame.Rect(0, self.height, self.width, cfg.HUD_HEIGHT)
        pygame.draw.rect(screen, (16, 20, 28), panel)
        pygame.draw.line(screen, self.track_accent, (0, self.height), (self.width, self.height), 3)

        title = fonts["title"].render(f"Mini Voiture RL - {self.track_label}", True, (245, 246, 248))
        screen.blit(title, (18, self.height + 10))

        line1 = (
            f"Episode: {episode}   Reward: {total_reward:7.1f}   Epsilon: {epsilon:.3f}   "
            f"Speed: {self.car_speed:4.1f}"
        )
        screen.blit(fonts["body"].render(line1, True, (227, 229, 233)), (18, self.height + 44))

        line2 = f"Etat: {self.last_reason}   Steps: {self.step_count}/{self.max_steps}   Position: ({int(self.car_pos.x)}, {int(self.car_pos.y)})"
        if model_loaded:
            line2 += "   Modele charge"
        screen.blit(fonts["small"].render(line2, True, (196, 200, 208)), (18, self.height + 74))

        if stats:
            stat_line = (
                f"Succes: {stats.get('success_rate', 0.0):5.1f}%   "
                f"Moyenne: {stats.get('average_reward', 0.0):7.1f}   "
                f"Crash: {stats.get('crash_count', 0)}   Timeout: {stats.get('timeout_count', 0)}"
            )
            screen.blit(fonts["small"].render(stat_line, True, self.track_accent), (18, self.height + 100))
