# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 19:26:53 2018

@author: Loic
"""

from renderer import Renderer
from simulator import MockSimulator

if __name__ == "__main__":
    renderer = Renderer(simulator=MockSimulator())
    renderer.render()