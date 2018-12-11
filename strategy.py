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
        self.lr = 0.3
        self.nin = 145
        self.nout = 1
        self.layers = [30]

        self.utility_networks = [nn.NN(self.nin, self.nout, self.layers) for _ in range(4)]
        self.optimizers = [optim.SGD(self.utility_networks[i].parameters(), lr=self.lr) for i in range(4)]
        self.criterion = nn.LinLoss()
        self.last_forward_pass = [None for _ in range(4)]

        self.speed = 5
        self.iter = 0
        self.can_update = False

    def select_move(self, sensors_values, energy_level, history):
        self.iter += 1

        if 60/self.iter <= self.speed:
            self.iter = 0
            self.can_update = True
            utility_values = self.get_utilities(sensors_values, energy_level, history)
            print("utility : ", utility_values)
            self.temperature *= 1.0001
            print("temperature : ", self.temperature)
            if self.temperature > self.temperature_bounds[1]:
                self.temperature = self.temperature_bounds[1]
            print([u.item() for u in torch.nn.Softmax(dim=0)(torch.Tensor(utility_values) * self.temperature)])
            probs = np.array([u.item() for u in torch.nn.Softmax(dim=0)(torch.Tensor(utility_values) * self.temperature)])
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
            for optimizer in self.optimizers:
                optimizer.zero_grad()

            if self.last_forward_pass is None:
                return

            utility_values = self.get_utilities(sensors_values, energy_level, history)
            print("utilities :", utility_values)
            target = current_reward + self.update_rate * max(utility_values)
            print(max(utility_values))
            print("predicted reward : ", target)
            last_action = history[:3].index(1) if 1 in history[:3] else 0
            print(last_action)
            loss = self.criterion.forward(self.last_forward_pass[last_action], target)
            print("loss : ", loss)
            loss.retain_grad()
            #target.register_hook(print)
            #self.last_forward_pass.register_hook(print)
            loss.backward()
            print(loss.grad)
            self.optimizers[last_action].step()

    def get_utilities(self, sensors_values, energy_level, history):
        val = nn.get_features(sensors_values, energy_level, history)
        return [self.utility_networks[i].forward(val[i]) for i in range(4)]
