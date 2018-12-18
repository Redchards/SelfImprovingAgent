import pygame
from event_handler import EventHandler

class PlayerController:
    def __init__(self, map):
        self.map = map
        self.player_position = next((j, i) for i, _ in enumerate(map) for j, e in enumerate(map[i]) if e.type == 'player')
        self.dim = (len(map[0]), len(map))

        self.keymap = {
            'up': [pygame.K_UP, pygame.K_z],
            'right': [pygame.K_RIGHT, pygame.K_d],
            'down': [pygame.K_DOWN, pygame.K_s],
            'left': [pygame.K_LEFT, pygame.K_q],
            'manual_control': [pygame.K_m]
        }

        event_handlers = {
            pygame.KEYDOWN: lambda evt: self.set_manual_control(not self.manual_control) if evt.key in self.keymap['manual_control'] else self.handle_manual_command(evt)
        }

        self.handler = EventHandler(event_handlers)
        self.collided = False
        self.manual_control = False


    def step(self, player_command, evt_queue):
        self.handler.handle_events(evt_queue)
        self.move(player_command, evt_queue)

    def set_manual_control(self, value):
        self.manual_control = value

    def move(self, player_command, evt):
        self.collided = False
        old_x, old_y = self.player_position

        if not self.manual_control:
            move = player_command
            self.player_position = (old_x + move[0], old_y + move[1])
        else:
            return self.player_position

        pos_x, pos_y = self.player_position

        if self.player_position[0] < 0:
            self.collided = True
            self.player_position = (0, pos_y)

        elif self.player_position[1] < 0:
            self.collided = True
            self.player_position = (pos_x, 0)

        elif self.player_position[0] >= self.dim[0]:
            self.collided = True
            self.player_position = (self.dim[0] - 1, pos_y)

        elif self.player_position[1] >= self.dim[1]:
            self.collided = True
            self.player_position = (pos_x, self.dim[1] - 1)

        pos_x, pos_y = self.player_position

        if self.map[pos_y][pos_x].type == 'obstacle':
            self.player_position = (old_x, old_y)
            self.collided = True
            return

    def handle_manual_command(self, evt):
        old_x, old_y = self.player_position

        print(evt)
        if evt.key == pygame.K_UP:
            self.player_position = (old_x, old_y - 1)
        elif evt.key == pygame.K_DOWN:
            self.player_position = (old_x, old_y + 1)

        elif evt.key == pygame.K_LEFT:
            self.player_position = (old_x - 1, old_y)

        elif evt.key == pygame.K_RIGHT:
            self.player_position = (old_x + 1, old_y)

