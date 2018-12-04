import pygame
from renderable import Renderable


class EmptyEntity:
    type = 'empty'
    symbol = '#'

    def __init__(self):
        self.id = -1
        self.renderable = Renderable(pygame.image.load('resources/empty.png'))

    def get_visual(self):
        return self.renderable.get_visual()


class EnemyAgent(EmptyEntity):
    type = 'enemy'
    symbol = 'E'

    def __init__(self, entity_id):
        self.entity_id = entity_id
        self.renderable = Renderable(pygame.image.load('resources/enemy.jpg'))


class Obstacle(EmptyEntity):
    type = 'obstacle'
    symbol = 'O'

    def __init__(self, entity_id):
        self.entity_id = entity_id
        self.renderable = Renderable(pygame.image.load('resources/obstacle.png'))


class Food(EmptyEntity):
    type = 'food'
    symbol = 'F'

    def __init__(self, entity_id):
        self.entity_id = entity_id
        self.renderable = Renderable(pygame.image.load('resources/food.png'))


class PlayerAgent(EmptyEntity):
    type = 'player'
    symbol = 'I'

    def __init__(self, entity_id):
        self.entity_id = entity_id
        self.renderable = Renderable(pygame.image.load('resources/player.jpg'))
