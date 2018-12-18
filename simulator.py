# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 19:15:50 2018

@author: Loic
"""

import pygame
from renderable import Renderable
import entity
from map_loader import MapLoader
from player_controller import PlayerController
from sensor import Sensor
from player_state import PlayerState
from enemy_behaviour import EnemyBehaviour


class DefaultSimulator:
    def __init__(self):
        self.dim = (0, 0)

    def step(self):
        return []


class MockSimulator(DefaultSimulator):
    def __init__(self):
        img = pygame.image.load("resources/image/star.png")
        # self.mockentity = entity.PlayerAgent(42)
        layer1_pred = lambda x, y: abs(x) + abs(y) <= 2
        layer2_pred = lambda x, y: ((x % 2, y % 2) == (0, 0) and abs(x) + abs(y) in range(4, 7, 2))
        layer3_pred = lambda x, y: ((x % 2, y % 2) == (0, 0) and abs(x) + abs(y) == 10)
        rotate_part = lambda l: [(y, -x) for x, y in l]

        food_sensor_l1 = [(x, y) for x in range(0, 11) for y in reversed(range(0, 11)) \
                           if (layer1_pred(x, y) or layer2_pred(x, y) or layer3_pred(x, y)) and not y == 0]
        food_sensor_l2 = rotate_part(food_sensor_l1)
        food_sensor_l3 = rotate_part(food_sensor_l2)
        food_sensor_l4 = rotate_part(food_sensor_l3)

        food_sensor_list = food_sensor_l1 + food_sensor_l2 + food_sensor_l3 + food_sensor_l4
        food_sensor_map = {
            'Y': [i for i, s in enumerate(food_sensor_list) if layer3_pred(s[0], s[1])],
            'X': [i for i, s in enumerate(food_sensor_list) if layer2_pred(s[0], s[1])],
            'O': [i for i, s in enumerate(food_sensor_list) if layer1_pred(s[0], s[1])]
        }
        food_sensor_aoe = {
            'Y': [(-1, 0), (1, 0), (0, -1), (0, 1), (1, -1), (-1, 1), (1, 1), (-1, -1), (0, 0), (2, 0), (0, 2), (-2, 0),
                  (0, -2)],
            'X': [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)],
            'O': [(-1, 0), (1, 0), (0, -1), (0, 1), (1, -1), (-1, 1), (1, 1), (-1, -1), (0, 0)]}

        enemy_sensor_l1 = [(x, y) for x in range(0, 7) for y in reversed(range(0, 7)) \
                           if (layer1_pred(x, y) or layer2_pred(x, y)) and not y == 0]
        enemy_sensor_l2 = rotate_part(enemy_sensor_l1)
        enemy_sensor_l3 = rotate_part(enemy_sensor_l2)
        enemy_sensor_l4 = rotate_part(enemy_sensor_l3)

        enemy_sensor_list = enemy_sensor_l1 + enemy_sensor_l2 + enemy_sensor_l3 + enemy_sensor_l4
        print(len(food_sensor_list))

        enemy_sensor_map = {
            'O': [i for i, s in enumerate(enemy_sensor_list) if layer1_pred(s[0], s[1])],
            'X': [i for i, s in enumerate(enemy_sensor_list) if layer2_pred(s[0], s[1])]
        }

        enemy_sensor_aoe = {
            'X': [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)],
            'O': [(-1, 0), (1, 0), (0, -1), (0, 1), (1, -1), (-1, 1), (1, 1), (-1, -1), (0, 0)]}

        obstacle_sensor_l1 = [(x, y) for x in range(0, 5) for y in reversed(range(0, 11)) \
                                if (x + y <= 4) and not y == 0]

        obstacle_sensor_l2 = rotate_part(obstacle_sensor_l1)
        obstacle_sensor_l3 = rotate_part(obstacle_sensor_l2)
        obstacle_sensor_l4 = rotate_part(obstacle_sensor_l3)

        obstacle_sensor_list = obstacle_sensor_l1 + obstacle_sensor_l2 + obstacle_sensor_l3 + obstacle_sensor_l4
        print(len(obstacle_sensor_list))
        obstacle_sensor_map = {
            'O': list(range(len(obstacle_sensor_list)))
        }

        obstacle_sensor_aoe = {
            'O': [(0, 0)]
        }

        self.sensor_list = [Sensor('food', food_sensor_list, food_sensor_map, food_sensor_aoe), \
                            Sensor('enemy', enemy_sensor_list, enemy_sensor_map, enemy_sensor_aoe), \
                            Sensor('obstacle', obstacle_sensor_list, obstacle_sensor_map, obstacle_sensor_aoe)]

        self.iter = 0
        self.piece_of_food_found = 0
        self.reset()

        self.nb_pieces_food = len([(j, i) for i, _ in enumerate(self.map) for j, e in enumerate(self.map[i]) if e.type == 'food'])
        self.cummulated_rewards = []
        self.pieces_of_food_found_history = []
        self.current_cummulated = 0


    def step(self, player_command_idx, player_command, evt_queue):
        if not self.player_state.alive or self.piece_of_food_found == self.nb_pieces_food:
            print("iter ", self.iter)
            print("pieces of food ", self.piece_of_food_found)
            self.pieces_of_food_found_history.append(self.piece_of_food_found)
            self.piece_of_food_found = 0
            self.iter += 1
            self.cummulated_rewards.append(self.current_cummulated)
            self.current_cummulated = 0
            self.reset()

        reward = self.apply_enemy_logic()

        if self.player_state.alive:
            reward = self.apply_player_logic(player_command, evt_queue)

        self.last_action = player_command_idx

        if not self.player_state.alive:
            reward = -0.9
        elif self.player_controller.collided:
            reward = -0.2

        self.current_cummulated += reward

        return self.get_state() + (reward,)

    def get_state(self):
         return self.map, tuple(s.current_perception for s in self.sensor_list), \
               self.player_state.get_health_level_one_hot(), \
               [1 if i == self.last_action else 0 for i in range(4)] + [int(self.player_controller.collided)]

    def apply_enemy_logic(self):
        reward = 0
        old_enemy_positions = list(self.enemy_behaviour.enemy_positions)
        new_enemy_positions = self.enemy_behaviour.step(self.player_state)

        for old_pos, new_pos in zip(old_enemy_positions, new_enemy_positions):
            if not old_pos == new_pos:  # TODO : maybe enemies should be able to step on food ?
                self.map[new_pos[1]][new_pos[0]] = self.map[old_pos[1]][old_pos[0]]
                self.map[old_pos[1]][old_pos[0]] = entity.EmptyEntity()
                if new_pos == self.player_controller.player_position:
                    reward = -0.9
                    self.player_state.take_damage(self.player_state.current_health)
                    self.player_state.alive = False

        return reward

    def apply_player_logic(self, player_command, evt_queue):
        reward = 0
        old_player_pos = self.player_controller.player_position

        self.player_controller.step(player_command, evt_queue)

        new_player_pos = self.player_controller.player_position

        if not new_player_pos == old_player_pos:
            if self.map[new_player_pos[1]][new_player_pos[0]].type == 'food':
                self.piece_of_food_found += 1
                reward = 0.6
                self.player_state.heal(15)

            if self.map[new_player_pos[1]][new_player_pos[0]].type == 'enemy':
                self.player_state.take_damage(self.player_state.current_health)
                reward = -0.9
                self.player_state.alive = False
                self.map[old_player_pos[1]][
                    old_player_pos[0]] = entity.EmptyEntity()  # TODO : replace by entity dead player ?
            else:
                self.map[new_player_pos[1]][new_player_pos[0]] = self.map[old_player_pos[1]][old_player_pos[0]]
                self.map[old_player_pos[1]][old_player_pos[0]] = entity.EmptyEntity()
                self.player_state.position = new_player_pos

            self.player_state.take_damage(1)

        if self.player_controller.collided:
            self.player_state.take_damage(1)

        for sensor in self.sensor_list:
            sensor.perception(new_player_pos, self.map)

        return reward

    def reset(self):
        self.map = MapLoader().parse_map('resources/map/map1.csv')
        self.dim = (len(self.map[0]), len(self.map))
        self.player_controller = PlayerController(self.map)
        self.player_state = PlayerState(speed=50, max_health=40, quantized_level_num=16,
                                        position=self.player_controller.player_position)

        self.enemy_behaviour = EnemyBehaviour(self.map)
        self.last_action = -1


class Simulator(DefaultSimulator):
    def __init__(self, map_file):
        pass

    def step(self):
        pass
