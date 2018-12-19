# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 19:17:26 2018

@author: Loic
"""


import pygame
from pygame.locals import *
from simulator import DefaultSimulator
from color import DefaultColorManager
from event_handler import EventHandler
import entity
import strategy

class Renderer:
    def __init__(self, window_dimensions=(480, 480), window_name="Default Renderer", simulator=DefaultSimulator(), player_strategy=strategy.QCONStrategy(), max_steps=None, cell_margin=1):
        self.cell_margin = cell_margin
        self.window_dimensions = window_dimensions
        self.window_name = window_name
        self.simulator = simulator
        self.player_strategy = player_strategy
        self.cell_margin = 1
        self.running = False
        self.screen = None
        self.color_manager = DefaultColorManager()
        self.cell_dim = self.compute_cell_dimensions()
        self.draw_sensors = [False for _ in self.simulator.sensor_list]
        self.default_empty = entity.EmptyEntity()
        self.max_steps = max_steps

        keypress_handlers = {
            pygame.K_F1: lambda: self.set_render_sensors(not self.draw_sensors[0], 0),
            pygame.K_F2: lambda: self.set_render_sensors(not self.draw_sensors[1], 1),
            pygame.K_F3: lambda: self.set_render_sensors(not self.draw_sensors[2], 2),
            pygame.K_ESCAPE: lambda: self.stop()
        }
        event_handlers = {
            pygame.QUIT: lambda evt: self.stop(),
            pygame.VIDEORESIZE: lambda evt: self.set_screen_dimensions(evt.dict['size']),
            pygame.KEYDOWN: lambda evt: keypress_handlers[evt.key]() if evt.key in keypress_handlers else None
        }
        self.handler = EventHandler(event_handlers)

    def render(self):
        self.running = True
        pygame.init()
        self.screen = pygame.display.set_mode(self.window_dimensions, HWSURFACE | DOUBLEBUF | RESIZABLE)
        pygame.display.set_caption(self.window_name)
        
        clock = pygame.time.Clock()

        m, s, e, h = self.simulator.get_state()
        while self.running:
            evt_queue = pygame.event.get()
            self.handler.handle_events(evt_queue)
            player_command_idx, player_command = self.player_strategy.select_move(s, e, h)
            m, s, e, h, r = self.simulator.step(player_command_idx, player_command, evt_queue)

            if self.simulator.training_phase:
                self.player_strategy.update_strategy(s, e, h, r, player_command_idx)

            if not self.simulator.player_state.alive:
                self.player_strategy.reset_agent()

            self.draw_grid(m, self.cell_dim)
            clock.tick(600)
            pygame.display.flip()

            if not self.max_steps is None and self.simulator.iter >= self.max_steps:
                self.stop()

        pygame.quit()
        
    def stop(self):
        self.running = False
        
    def is_running(self):
        return self.running
    
    def compute_cell_dimensions(self):
        grid_width, grid_height = self.simulator.dim

        if grid_width == 0 or grid_height == 0:
            return self.window_dimensions
        else:
            return self.window_dimensions[0] // grid_width, self.window_dimensions[1] // grid_height
    
    def draw_grid(self, grid, cell_dim):
        cell_width, cell_height = cell_dim
        nb_col = 1 if len(grid) == 0 or len(grid[0]) == 0 else len(grid[0])
        nb_row = 1 if len(grid) == 0 else len(grid)

        self.screen.fill(self.color_manager.margin_color)

        for row in range(nb_row):
            for col in range(nb_col):
                self.screen.blit(pygame.transform.scale(self.default_empty.get_visual(), (cell_width - self.cell_margin, cell_height - self.cell_margin)),
                                 (cell_width * col + self.cell_margin, cell_height * row + self.cell_margin))
                if not grid[row][col].type == 'empty':
                    s = pygame.Surface((cell_width - self.cell_margin, cell_height - self.cell_margin), pygame.SRCALPHA)
                    s.blit(pygame.transform.scale(grid[row][col].get_visual(), (cell_width - self.cell_margin, cell_height - self.cell_margin)), (0, 0))
                    self.screen.blit(s, (cell_width * col + self.cell_margin, cell_height * row + self.cell_margin))

        player_pos_x, player_pos_y = self.simulator.player_controller.player_position
        for i, sensor in enumerate(self.simulator.sensor_list):
            if self.draw_sensors[i]:
                idx = 0
                for cell in sensor.sensor_list:
                    cell_x, cell_y =  player_pos_x + cell[0], player_pos_y + cell[1]
                    if sensor.current_perception[idx]:
                        pygame.draw.rect(self.screen, (255, 0, 0, 0.5), (cell_width * cell_x + cell_width // 2  - 5, cell_height * cell_y + cell_height // 2 - 5, 5, 5))
                    else:
                        pygame.draw.rect(self.screen, (0, 0, 0, 0.5), (cell_width * cell_x + cell_width // 2  - 5, cell_height * cell_y + cell_height // 2 - 5, 5, 5))

                    idx += 1

        for health_level in range(self.simulator.player_state.current_health_level):
            pygame.draw.rect(self.screen, (0, 128, 0, 1), (cell_width // 5 * (health_level + 1), cell_height * nb_row - (cell_height // 3), cell_height // 20, cell_height // 4))

    def set_screen_dimensions(self, dim):
        self.window_dimensions = dim
        self.cell_dim = self.compute_cell_dimensions()
        self.screen = pygame.display.set_mode(self.window_dimensions, HWSURFACE | DOUBLEBUF | RESIZABLE)

    def set_render_sensors(self, val, idx):
        print("hai")
        self.draw_sensors[idx] = val
