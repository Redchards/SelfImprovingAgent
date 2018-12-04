# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 19:39:14 2018

@author: Loic
"""


class DefaultColorManager:
    def __init__(self):
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)

        self.cell_color = self.WHITE
        self.margin_color = self.BLACK
