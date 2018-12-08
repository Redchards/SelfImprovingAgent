import numpy.random as random
import torch
import nn
import torch.optim as optim
import numpy as np

class BaseStrategy:
    moveset = [(0, -1), (1, 0), (0, 1), (-1, 0)]

    def select_move(self, sensors_values, energy_level, history):
        pass

    def update_strategy(self, sensors_values, energy_level, history):
        pass

class RandomStrategy(BaseStrategy):
    def select_move(self, sensors_values, energy_level, history):
       idx = random.randint(0, 3)
       return idx, self.moveset[idx]

    def update_strategy(self, sensors_values, energy_level, history):
        pass

class QCONStrategy(BaseStrategy):
    def __init__(self, update_rate=0.9, initial_temperature=20, temperature_bounds=(20, 60)):
        self.update_rate = update_rate
        self.temperature = initial_temperature
        self.temperature_bounds = temperature_bounds
        self.lr = 1e-5
        self.nin = 145
        self.nout = 1
        self.layers = [30]

        self.utility_network = nn.NN(self.nin, self.nout, self.layers)
        self.optimizer = optim.Adam(self.utility_network.parameters(), lr=self.lr)
        self.criterion = nn.LinLoss()
        self.last_forward_pass = None

        self.speed = 60
        self.iter = 0
        self.can_update = False

    def select_move(self, sensors_values, energy_level, history):
        self.iter += 1

        if 60/self.iter <= self.speed:
            self.iter = 0
            self.can_update = True
            utility_values = self.get_utilities(sensors_values, energy_level, history)
            print("utility : ", utility_values)
            self.temperature *= 1.01
            if self.temperature > self.temperature_bounds[1]:
                self.temperature = self.temperature_bounds[1]
            print([u.item() for u in torch.nn.Softmax(dim=0)(utility_values * self.temperature)])
            probs = np.array([u.item() for u in torch.nn.Softmax(dim=0)(utility_values * self.temperature)])
            probs /= sum(probs)
            idx = random.choice(len(self.moveset), p=probs)

            self.last_forward_pass = utility_values
            print("idx : ", idx)
            return idx, self.moveset[idx]
        return -1, (0, 0)

    def update_strategy(self, sensors_values, energy_level, history, current_reward):
        if self.can_update:
            print("reward : ", current_reward)
            self.can_update = False
            self.optimizer.zero_grad()

            if self.last_forward_pass is None:
                return

            utility_values = self.get_utilities(sensors_values, energy_level, history)
            print("utilities :", utility_values)
            target = current_reward + self.update_rate * max(utility_values)
            print("predicted reward : ", target)
            loss = self.criterion.forward(self.last_forward_pass, target, history[:3].index(1) if 1 in history[:3] else 0)
            print("loss : ", loss)
            print(loss.grad)
            loss.backward()
            self.optimizer.step()

    def get_utilities(self, sensors_values, energy_level, history):
        return self.utility_network.forward(nn.get_features(sensors_values, energy_level, history))
