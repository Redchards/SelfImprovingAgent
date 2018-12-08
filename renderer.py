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

class Renderer:
    def __init__(self, window_dimensions=(480, 480), window_name="Default Renderer", simulator=DefaultSimulator(), cell_margin=1):
        self.window_dimensions = window_dimensions
        self.window_name = window_name
        self.simulator = simulator
        self.cell_margin = 1
        self.running = False
        self.screen = None
        self.color_manager = DefaultColorManager()
        self.cell_dim = self.compute_cell_dimensions()
        self.draw_sensors = [False for _ in self.simulator.sensor_list]
        self.default_empty = entity.EmptyEntity()

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
        
        while self.running:
            evt_queue = pygame.event.get()
            self.handler.handle_events(evt_queue)

            self.draw_grid(self.simulator.step(evt_queue), self.cell_dim)
            clock.tick(60)
            pygame.display.flip()

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
                for _, l in sensor.sensor_map.items():
                    for cell in l:
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
