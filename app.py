# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 19:26:53 2018

@author: Loic
"""

from renderer import Renderer
from simulator import MockSimulator
from strategy import QCONStrategy
from strategy import QCONStrategy2

if __name__ == "__main__":
    renderer = Renderer(simulator=MockSimulator(), player_strategy=QCONStrategy2())
    renderer.render()