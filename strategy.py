import numpy.random as random
import torch
import nn
import torch.optim as optim

class BaseStrategy:
    moveset = [(0, -1), (1, 0), (0, 1), (-1, 0)]

    def select_move(self, sensors_values, energy_level, history):
        pass

class RandomStrategy(BaseStrategy):
    def select_move(self, sensors_values, energy_level, history):
       idx = random.randint(0, 3)
       return idx, self.moveset[idx]

class QCONStrategy(BaseStrategy):
    def __init__(self, initial_temperature=20, temperature_bounds=(20, 60)):
        self.temperature = initial_temperature
        self.temperature_bounds = temperature_bounds
        self.lr = 1e-5
        self.nin = 145
        self.nout = 1
        self.layers = [30]

        self.utility_network = nn.NN(self.nin, self.nout, self.layers)
        self.optimizer = optim.Adam(self.utility_network.parameters(), lr=self.lr)
        self.criterion = nn.LinLoss()

    def select_move(self, sensors_values, energy_level, history):
        utility_values = self.utility_network.forward(nn.get_features(sensors_values, energy_level, history))
        idx = random.choice(len(self.moveset), [int(u.item) for u in torch.nn.Softmax(utility_values * self.temperature)])
        return idx, self.moveset[idx]



