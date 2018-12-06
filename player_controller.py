import pygame
from event_handler import EventHandler

class PlayerController:
    def __init__(self, map):
        self.map = map
        self.player_position = next((j, i) for i, _ in enumerate(map) for j, e in enumerate(map[i]) if e.type == 'player')
        self.dim = (len(map[0]), len(map))

        event_handlers = {
            pygame.KEYDOWN: lambda evt: self.move(evt)
        }

        self.handler = EventHandler(event_handlers)
        self.collided = False
        print(self.player_position)


    def step(self, evt_queue):
        self.handler.handle_events(evt_queue)

    def move(self, evt):
        self.collided = False
        old_x, old_y = self.player_position

        if evt.key == pygame.K_UP:
            self.player_position = (old_x, old_y - 1)

        elif evt.key == pygame.K_DOWN:
            self.player_position = (old_x, old_y + 1)

        elif evt.key == pygame.K_LEFT:
            self.player_position = (old_x - 1, old_y)

        elif evt.key == pygame.K_RIGHT:
            self.player_position = (old_x + 1, old_y)

        pos_x, pos_y = self.player_position

        if self.player_position[0] < 0:
            self.player_position = (0, pos_y)

        elif self.player_position[1] < 0:
            self.player_position = (pos_x, 0)

        elif self.player_position[0] >= self.dim[0]:
            self.player_position = (self.dim[0] - 1, pos_y)

        elif self.player_position[1] >= self.dim[1]:
            self.player_position = (pos_x, self.dim[1] - 1)

        pos_x, pos_y = self.player_position

        if self.map[pos_y][pos_x].type == 'obstacle':
            self.player_position = (old_x, old_y)
            self.collided = True
            return

