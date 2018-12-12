# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 19:26:53 2018

@author: Loic
"""

from renderer import Renderer
from simulator import MockSimulator
from strategy import QCONStrategy
from strategy import QCONStrategy2
import matplotlib as mpl
mpl.use('module://backend_interagg')
import matplotlib.pyplot as plt

if __name__ == "__main__":
    renderer = Renderer(simulator=MockSimulator(), player_strategy=QCONStrategy2(update_rate=0.999))
    renderer.render()
    plt.ticklabel_format(style='plain', axis='x', useOffset=False)
    plt.plot(range(len(renderer.simulator.cummulated_rewards)), renderer.simulator.cummulated_rewards)
    print(renderer.simulator.pieces_of_food_found_history)
    plt.plot(range(len(renderer.simulator.pieces_of_food_found_history)), renderer.simulator.pieces_of_food_found_history)
    plt.show()