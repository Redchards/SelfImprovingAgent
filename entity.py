import pygame
from renderable import Renderable


class EmptyEntity:
    type = 'empty'
    symbol = '#'

    def __init__(self):
        self.id = -1
        self.renderable = Renderable(pygame.image.load('resources/image/land.png'))

    def get_visual(self):
        return self.renderable.get_visual()


class EnemyAgent(EmptyEntity):
    type = 'enemy'
    symbol = 'E'

    def __init__(self, entity_id):
        self.entity_id = entity_id
        self.renderable = Renderable(pygame.image.load('resources/image/Bearger.png'))


class Obstacle(EmptyEntity):
    type = 'obstacle'
    symbol = 'O'

    def __init__(self, entity_id):
        self.entity_id = entity_id
        self.renderable = Renderable(pygame.image.load('resources/image/Evergreen.png'))


class Food(EmptyEntity):
    type = 'food'
    symbol = 'F'

    def __init__(self, entity_id):
        self.entity_id = entity_id
        self.renderable = Renderable(pygame.image.load('resources/image/food.png'))


class PlayerAgent(EmptyEntity):
    type = 'player'
    symbol = 'I'

    def __init__(self, entity_id):
        self.entity_id = entity_id
        self.renderable = Renderable(pygame.image.load('resources/image/Wilba.png'))
