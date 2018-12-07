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
        img = pygame.image.load("resources/star.png")
        # self.mockentity = entity.PlayerAgent(42)
        self.map = MapLoader().parse_map('resources/map/map_test.csv')
        self.dim = (len(self.map[0]), len(self.map))
        self.player_controller = PlayerController(self.map)
        self.player_state = PlayerState(speed=1, max_health=40, quantized_level_num=16,
                                        position=self.player_controller.player_position)
        food_sensor_map = {
            'O': [(-4, 0), (-6, 0), (4, 0), (6, 0), (-2, -2), (-4, -2), (2, -2), (4, -2), (0, -4), (-2, -4), (2, -4),
                  (0, -6), (-2, 2), (-4, 2), (2, 2), (4, 2), (0, 4), (-2, 4), (2, 4), (0, 6)],
            'X': [(-1, 0), (-2, 0), (1, 0), (2, 0), (-1, -1), (0, -1), (1, -1), (0, -2), (-1, 1), (0, 1), (1, 1),
                  (0, 2)]}

        food_sensor_aoe = {
            'X': [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)],
            'O': [(-1, 0), (1, 0), (0, -1), (0, 1), (1, -1), (-1, 1), (1, 1), (-1, -1), (0, 0)]}

        enemy_sensor_map = {
            'Y': [(-10, 0), (10, 0), (-8, -2), (8, -2), (-6, -4), (6, -4), (-4, -6), (4, -6), (-2, -8), (2, -8),
                  (0, -10),
                  (-8, 2), (8, 2), (-6, 4), (6, 4), (-4, 6), (4, 6), (-2, 8), (2, 8), (0, 10)],
            'O': [(-4, 0), (-6, 0), (4, 0), (6, 0), (-2, -2), (-4, -2), (2, -2), (4, -2), (0, -4), (-2, -4), (2, -4),
                  (0, -6), (-2, 2), (-4, 2), (2, 2), (4, 2), (0, 4), (-2, 4), (2, 4), (0, 6)],
            'X': [(-1, 0), (-2, 0), (1, 0), (2, 0), (-1, -1), (0, -1), (1, -1), (0, -2), (-1, 1), (0, 1), (1, 1),
                  (0, 2)]
        }
        enemy_sensor_aoe = {
            'Y': [(-1, 0), (1, 0), (0, -1), (0, 1), (1, -1), (-1, 1), (1, 1), (-1, -1), (0, 0), (2, 0), (0, 2), (-2, 0),
                  (0, -2)],
            'X': [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)],
            'O': [(-1, 0), (1, 0), (0, -1), (0, 1), (1, -1), (-1, 1), (1, 1), (-1, -1), (0, 0)]}

        obstacle_sensor_map = {
            'O': [(i, j) for i in range(-4, 5) for j in range(-4, 5) if abs(i) + abs(j) <= 4 and not (i, j) == (0, 0)]
        }

        obstacle_sensor_aoe = {
            'O': [(0, 0)]
        }

        self.sensor_list = [Sensor('food', food_sensor_map, food_sensor_aoe),\
                            Sensor('enemy', enemy_sensor_map, enemy_sensor_aoe),\
                            Sensor('obstacle', obstacle_sensor_map, obstacle_sensor_aoe)]
        self.enemy_behaviour = EnemyBehaviour(self.map)

    def step(self, evt_queue):
        old_enemy_positions = list(self.enemy_behaviour.enemy_positions)
        new_enemy_positions = self.enemy_behaviour.step(self.player_state)

        for old_pos, new_pos in zip(old_enemy_positions, new_enemy_positions):
            print(new_pos)
            print(self.map[new_pos[1]][new_pos[0]].type)
            if not old_pos == new_pos:  # TODO : maybe enemies should be able to step on food ?
                self.map[new_pos[1]][new_pos[0]] = self.map[old_pos[1]][old_pos[0]]
                self.map[old_pos[1]][old_pos[0]] = entity.EmptyEntity()
                if new_pos == self.player_controller.player_position:
                    self.player_state.take_damage(self.player_state.current_health)
                    self.player_state.alive = False

        if not self.player_state.alive:
            return self.map

        old_player_pos = self.player_controller.player_position

        self.player_controller.step(evt_queue)

        new_player_pos = self.player_controller.player_position

        if not new_player_pos == old_player_pos:
            if self.map[new_player_pos[1]][new_player_pos[0]].type == 'food':
                self.player_state.heal(15)

            if self.map[new_player_pos[1]][new_player_pos[0]].type == 'enemy':
                self.player_state.take_damage(self.player_state.current_health)
                self.player_state.alive = False
                self.map[old_player_pos[1]][
                    old_player_pos[0]] = entity.EmptyEntity()  # TODO : replace by entity dead player ?
                return self.map

            self.map[new_player_pos[1]][new_player_pos[0]] = self.map[old_player_pos[1]][old_player_pos[0]]
            self.map[old_player_pos[1]][old_player_pos[0]] = entity.EmptyEntity()
            self.player_state.position = new_player_pos
            self.player_state.take_damage(1)
            print(self.map[old_player_pos[1]][old_player_pos[0]])
            print(self.map[new_player_pos[1]][new_player_pos[0]])

        for sensor in self.sensor_list:
            sensor.perception(new_player_pos, self.map)

        return self.map


class Simulator(DefaultSimulator):
    def __init__(self, map_file):
        pass

    def step(self):
        pass
