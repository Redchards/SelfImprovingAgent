import entity
import numpy as np
import numpy.random as random
import math

class EnemyBehaviour:
    def __init__(self, map):
        self.speed = 0
        self.current_step = 0
        self.map = map
        self.dim = (len(self.map[0]), len(self.map))

        self.choices = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.enemy_positions = list((j, i) for i, _ in enumerate(map) for j, e in enumerate(map[i]) if e.type == 'enemy')

    def step(self, player_state):
        self.speed = player_state.speed * 0.8
        self.current_step += 1

        if self.current_step >= 60 / self.speed:
            for i in range(len(self.enemy_positions)):
                pos = self.enemy_positions[i]
                r = random.choice(2, p=[0.2, 0.8])
                if r == 0:
                    continue
                m = self.choices[random.choice(len(self.choices), p=self.evaluate_policy_probability(pos, player_state.position))]

                self.enemy_positions[i] = (pos[0] + m[0], pos[1] + m[1])

            self.current_step = 0

        return self.enemy_positions

    def evaluate_policy_probability(self, enemy_pos, player_pos):
        x_player_pos, y_player_pos = player_pos
        x_enemy_pos, y_enemy_pos = enemy_pos
        probas = []

        print("enemy pos {}".format(enemy_pos))
        for choice in self.choices:
            resulting_pos = (x_enemy_pos + choice[0], y_enemy_pos + choice[1])
            if resulting_pos[0] < 0 or resulting_pos[0] >= self.dim[0] \
                or resulting_pos[1] < 0 or resulting_pos[1] >= self.dim[1]\
                or (not self.map[resulting_pos[1]][resulting_pos[0]].type == 'empty')\
                and (not self.map[resulting_pos[1]][resulting_pos[0]].type == 'player')\
                or resulting_pos in self.enemy_positions:
                probas.append(0)
                continue

            enemy_player_vec = (x_player_pos - resulting_pos[0], y_player_pos - resulting_pos[1])
            dist = abs(enemy_player_vec[0]) + abs(enemy_player_vec[1])
            angle = math.atan2(enemy_player_vec[0], enemy_player_vec[1]) * 180 / math.pi
            w_angle = (180 - abs(angle)) / 180
            t_dist = 1
            if dist <= 4:
                t_dist = 15 - dist
            elif dist <= 15:
                t_dist = 9 - dist / 2

            print("resulting pos {}".format(resulting_pos))
            probas.append(np.exp(0.33 * w_angle * t_dist))

        return [p / sum(probas) for p in probas] if sum(probas) > 0 else [1/4, 1/4, 1/4, 1/4]
