import numpy.random as random
import torch
import nn
import torch.optim as optim
import numpy as np
from collections import namedtuple
import copy


class BaseStrategy:
    moveset = [(0, -1), (1, 0), (0, 1), (-1, 0)]

    def select_move(self, sensors_values, energy_level, history):
        pass

    def update_strategy(self, sensors_values, energy_level, history):
        pass

    def reset_agent(self):
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
        self.criterion = torch.nn.MSELoss()
        self.last_forward_pass = [None for _ in range(4)]

        self.speed = 5
        self.iter = 0
        self.can_update = False

    def select_move(self, sensors_values, energy_level, history):
        self.iter += 1

        if 60 / self.iter <= self.speed:
            self.iter = 0
            self.can_update = True
            utility_values = self.get_utilities(sensors_values, energy_level, history)
            print("utility : ", utility_values)
            self.temperature *= 1.001
            print("temperature : ", self.temperature)
            if self.temperature > self.temperature_bounds[1]:
                self.temperature = self.temperature_bounds[1]
            print([u.item() for u in torch.nn.Softmax(dim=0)(torch.Tensor(utility_values) * self.temperature)])
            probs = np.array(
                [u.item() for u in torch.nn.Softmax(dim=0)(torch.Tensor(utility_values) * self.temperature)])
            probs /= sum(probs)
            idx = random.choice(len(self.moveset), p=probs)

            self.last_forward_pass = utility_values
            print("idx : ", idx)
            return idx, self.moveset[idx]
        return -1, (0, 0)

    def update_strategy(self, sensors_values, energy_level, history, current_reward, action):
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
            # target.register_hook(print)
            # self.last_forward_pass.register_hook(print)
            loss.backward()
            print(loss.grad)
            self.optimizers[last_action].step()

    def get_utilities(self, sensors_values, energy_level, history):
        val = nn.get_features(sensors_values, energy_level, history)
        return [self.utility_networks[i].forward(val[i]) for i in range(4)]


class QCONStrategy2(BaseStrategy):
    def __init__(self, update_rate=0.9, initial_temperature=0.01, temperature_bounds=(0.01, 60), epsilon=0.1,
                 epsilon_decay=0.99):
        self.update_rate = update_rate
        self.temperature = initial_temperature
        self.temperature_bounds = temperature_bounds
        self.lr = 0.0003
        self.nin = 145
        self.nout = 4
        self.layers = [500]

        self.utility_network = nn.NN(self.nin, self.nout, self.layers)
        self.optimizer = optim.Adam(self.utility_network.parameters(), lr=self.lr)
        self.criterion = torch.nn.SmoothL1Loss()
        self.last_forward_pass = None

        self.speed = 50
        self.iter = 0
        self.can_update = False

        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay

    def select_move(self, sensors_values, energy_level, history):
        self.iter += 1

        if 60 / self.iter <= self.speed:
            self.iter = 0
            self.can_update = True
            utility_values = self.get_utilities(sensors_values, energy_level, history)
            print("utility : ", utility_values)
            self.temperature *= 1.001
            print("temperature : ", self.temperature)
            if self.temperature > self.temperature_bounds[1]:
                self.temperature = self.temperature_bounds[1]
            print([u.item() for u in torch.nn.Softmax(dim=0)(torch.Tensor(utility_values) * self.temperature)])
            probs = np.array(
                [u.item() for u in torch.nn.Softmax(dim=0)(torch.Tensor(utility_values) * self.temperature)])
            probs /= sum(probs)
            eps_explore_draw = random.uniform(0, 1)
            if eps_explore_draw < self.epsilon:
                idx = random.randint(0, 4)
            else:
                idx = random.choice(len(self.moveset), p=probs)
            self.epsilon *= self.epsilon_decay

            self.last_forward_pass = utility_values
            print("idx : ", idx)
            return idx, self.moveset[idx]
        return -1, (0, 0)

    def update_strategy(self, sensors_values, energy_level, history, current_reward, action):
        if self.can_update:
            print("reward : ", current_reward)
            self.can_update = False
            self.optimizer.zero_grad()

            if self.last_forward_pass is None:
                return

            utility_values = self.get_utilities(sensors_values, energy_level, history)
            print("utilities :", utility_values)
            target = torch.autograd.Variable(current_reward + self.update_rate * max(utility_values),
                                             requires_grad=False)
            print(max(utility_values))
            print("predicted reward : ", target)
            last_action = history[:3].index(1) if 1 in history[:3] else 0
            print(last_action)
            loss = self.criterion.forward(self.last_forward_pass[last_action], target)
            print("loss : ", loss)
            loss.retain_grad()
            # target.register_hook(print)
            # self.last_forward_pass.register_hook(print)
            loss.backward()
            print(loss.grad)
            self.optimizer.step()

    def get_utilities(self, sensors_values, energy_level, history):
        val = nn.get_features(sensors_values, energy_level, history)
        return self.utility_network.forward(val[0])


class QCONStrategy3(BaseStrategy):
    def __init__(self, update_rate=0.9, initial_temperature=0.1, temperature_bounds=(0.1, 60)):
        self.update_rate = update_rate
        self.temperature = initial_temperature
        self.temperature_bounds = temperature_bounds
        self.lr = 0.3
        self.nin = 145
        self.nout = 1
        self.layers = [30]

        self.utility_network = nn.NN(self.nin, self.nout, self.layers)
        self.optimizer = optim.SGD(self.utility_network.parameters(), lr=self.lr)
        self.criterion = torch.nn.MSELoss()
        self.last_forward_pass = None

        self.speed = 50
        self.iter = 0
        self.can_update = False

    def select_move(self, sensors_values, energy_level, history):
        self.iter += 1

        if 60 / self.iter <= self.speed:
            self.iter = 0
            self.can_update = True
            utility_values = self.get_utilities(sensors_values, energy_level, history)
            print("utility : ", utility_values)
            self.temperature *= 1.001
            print("temperature : ", self.temperature)
            if self.temperature > self.temperature_bounds[1]:
                self.temperature = self.temperature_bounds[1]
            print([u.item() for u in torch.nn.Softmax(dim=0)(utility_values * self.temperature)])
            probs = np.array([u.item() for u in torch.nn.Softmax(dim=0)(utility_values * self.temperature)])
            probs /= sum(probs)
            idx = random.choice(len(self.moveset), p=probs)

            self.last_forward_pass = utility_values[idx]
            print("idx : ", idx)
            return idx, self.moveset[idx]
        return -1, (0, 0)

    def update_strategy(self, sensors_values, energy_level, history, current_reward, action):
        if self.can_update:
            print("reward : ", current_reward)
            self.can_update = False
            self.optimizer.zero_grad()

            if self.last_forward_pass is None:
                return

            utility_values = self.get_utilities(sensors_values, energy_level, history)
            print("utilities :", utility_values)
            target = current_reward + self.update_rate * max(utility_values.detach())
            print("predicted reward : ", target)
            loss = self.criterion.forward(self.last_forward_pass, target)
            print("loss : ", loss)
            print(loss.grad)
            loss.backward()
            self.optimizer.step()

    def get_utilities(self, sensors_values, energy_level, history):
        return self.utility_network.forward(nn.get_features(sensors_values, energy_level, history))


Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward'))


class ReplayMemory(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.position = 0

    def push(self, *arg):  # transition: ('state', 'action', 'next_state', 'reward','done')
        """Saves a transition."""
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        self.memory[self.position] = Transition(*arg)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)


class QCONRStrategy(BaseStrategy):
    def __init__(self, update_rate=0.9, initial_temperature=0.1, temperature_bounds=(0.1, 60)):
        self.update_rate = update_rate
        self.temperature = initial_temperature
        self.temperature_bounds = temperature_bounds
        self.lr = 0.3
        self.nin = 145
        self.nout = 4  # 4 actions
        self.layers = [30]
        self.capacity = 1000000  # memory capacity
        self.batch_size = 1000
        self.C_target = 300  # update target nn every C times
        self.state_prec = 0  # precedent state
        self.count = 0  # count for updating the target nn

        self.utility_network = nn.NN(self.nin, self.nout, self.layers)
        self.utility_network_target = copy.deepcopy(self.utility_network)
        self.optimizer = optim.SGD(self.utility_network.parameters(), lr=self.lr)
        self.criterion = torch.nn.SmoothL1Loss()  # nn.MSELoss()
        self.last_forward_pass = None

        self.speed = 50
        self.iter = 0
        self.can_update = False

    def select_move(self, sensors_values, energy_level, history):
        self.iter += 1

        if 60 / self.iter <= self.speed:
            self.iter = 0
            self.can_update = True
            utility_values = self.get_utilities(sensors_values, energy_level, history)
            print("utility : ", utility_values)
            self.temperature *= 1.01
            print("temperature : ", self.temperature)
            if self.temperature > self.temperature_bounds[1]:
                self.temperature = self.temperature_bounds[1]
            print([u.numpy() for u in torch.nn.Softmax(dim=0)(utility_values * self.temperature)])
            probs = np.array([u.numpy() for u in torch.nn.Softmax(dim=0)(utility_values * self.temperature)])
            probs /= sum(probs)
            idx = random.choice(len(self.moveset), p=probs)

            self.last_forward_pass = utility_values[idx]
            print("idx : ", idx)

            self.state_prec = torch.tensor(nn.get_features(sensors_values, energy_level, history), dtype=torch.float)
            return idx, self.moveset[idx]
        return -1, (0, 0)

    def update_strategy(self, sensors_values, energy_level, history, current_reward, action):
        if self.can_update:
            state = torch.tensor(nn.get_features(sensors_values, energy_level, history), dtype=torch.float)
            action = torch.tensor([action])
            reward = torch.tensor([current_reward], dtype=torch.float)
            self.D.push(self.state_prec, action, state, reward)
            if len(self.D) < self.batch_size:
                return
            mini_batch = self.D.sample(self.batch_size)
            batch = Transition(*zip(*mini_batch))
            state_batch = torch.cat(batch.state)
            action_batch = torch.cat(batch.action)
            next_state_batch = torch.cat(batch.next_state)
            reward_batch = torch.cat(batch.reward)

            print("reward : ", current_reward)
            self.can_update = False

            self.optimizer.zero_grad()
            if self.last_forward_pass is None:
                return

            ytarget = reward_batch + self.update_rate * self.utility_network_target(next_state_batch).max(dim=1)[0]
            ypred = self.utility_network(state_batch)[list(range(self.batch_size)), action_batch]
            batch_loss = self.criterion(ypred, ytarget.detach())
            self.optimizer.zero_grad()
            batch_loss.backward()
            print("loss : ", batch_loss)
            self.optimizer.step()

            self.count += 1
            if self.count % self.C_target == 0:
                self.count = 0
                self.utility_network_target = copy.deepcopy(self.utility_network)

    def get_utilities(self, sensors_values, energy_level, history):
        return self.utility_network.forward(nn.get_features(sensors_values, energy_level, history)).detach()


class QCONRStrategy2(BaseStrategy):
    def __init__(self, update_rate=0.9, initial_temperature=0.1, temperature_bounds=(0.1, 60), memory_size=100):
        self.update_rate = update_rate
        self.temperature = initial_temperature
        self.temperature_bounds = temperature_bounds
        self.lr = 0.3
        self.nin = 145
        self.nout = 1
        self.layers = [30]
        self.memory_size = memory_size
        self.memory = [None for _ in range(memory_size)]

        self.utility_network = nn.NN(self.nin, self.nout, self.layers)
        self.optimizer = optim.SGD(self.utility_network.parameters(), lr=self.lr)
        self.criterion = torch.nn.MSELoss()
        self.last_forward_pass = None
        self.last_state = None
        self.last_action = None

        self.speed = 50
        self.iter = 0
        self.step = 0
        self.can_update = False

        self.reset_agent()

    def select_move(self, sensors_values, energy_level, history):
        self.iter += 1

        if 60 / self.iter <= self.speed:
            self.iter = 0
            self.can_update = True
            utility_values = self.get_utilities(sensors_values, energy_level, history)
            print("utility : ", utility_values)
            self.temperature *= 1.01
            print("temperature : ", self.temperature)
            if self.temperature > self.temperature_bounds[1]:
                self.temperature = self.temperature_bounds[1]
            print([u.item() for u in torch.nn.Softmax(dim=0)(utility_values * self.temperature)])
            probs = np.array([u.item() for u in torch.nn.Softmax(dim=0)(utility_values * self.temperature)])
            probs /= sum(probs)
            last_action = random.choice(len(self.moveset), p=probs)

            self.last_forward_pass = utility_values[last_action]
            self.last_state = (sensors_values, energy_level, history)
            print("idx : ", last_action)
            return last_action, self.moveset[last_action]
        return -1, (0, 0)

    def update_strategy(self, sensors_values, energy_level, history, current_reward, action):
        if self.can_update:
            print("reward : ", current_reward)
            self.can_update = False

            if self.last_forward_pass is None:
                return

            self.update_utility_network(self.last_forward_pass, sensors_values, energy_level, history, current_reward, action)

            self.memory[(self.step - 1) % self.memory_size].append((self.last_state, action, \
                                                             (sensors_values, energy_level, history), current_reward))

            if self.step > 1:
                lesson = self.memory[QCONRStrategy2.choose_lesson(min(self.memory_size, self.step - 1))]

                for experience in reversed(lesson):
                    s1, a, s2, r = experience
                    if not r > 0.001:
                        continue

                    last_forward_pass = self.get_utilities(*s1)[a]
                    s, e, h = s2
                    self.update_utility_network(last_forward_pass, s, e, h, r, a)


    def update_utility_network(self, last_forward, sensors_values, energy_level, history, current_reward, action):
            self.optimizer.zero_grad()
            utility_values = self.get_utilities(sensors_values, energy_level, history)
            print("utilities :", utility_values)
            target = current_reward + self.update_rate * max(utility_values.detach())
            print("predicted reward : ", target)
            loss = self.criterion.forward(last_forward, target)
            print("loss : ", loss)
            print(loss.grad)
            loss.backward()
            self.optimizer.step()

    def get_utilities(self, sensors_values, energy_level, history):
        return self.utility_network.forward(nn.get_features(sensors_values, energy_level, history))

    def reset_agent(self):
        self.iter = 0
        self.step += 1
        self.memory[(self.step - 1) % self.memory_size] = []

    def choose_lesson(n):
        w = min(3, 1 + 0.02 * n)
        r = random.rand()
        k = n * np.log(1 + r * (np.exp(w) - 1)) / w
        print(k)
        return int(k)
