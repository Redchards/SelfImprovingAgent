#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import copy
import torch
import torch.nn as nn
import torch.optim as optim


class NN(nn.Module):
    def __init__(self, inSize, outSize, layers=[]):  # in:145, out:1 - 4 times
        super(NN, self).__init__()
        self.layers = nn.ModuleList([])
        for x in layers:
            self.layers.append(nn.Linear(inSize, x))
            self.layers[-1].bias.data.fill_(0)
            inSize = x
        self.layers.append(nn.Linear(inSize, outSize))
        self.layers[-1].bias.data.fill_(0)

    def forward(self, x):
        x = self.layers[0](x)
        for i in range(1, len(self.layers)):
            x = torch.nn.functional.leaky_relu(x)
            x = self.layers[i](x)
            x = 1 / (1 + torch.exp(-x)) - 0.5
        return x


class NillLoss(torch.autograd.Function):
    @staticmethod
    def forward(ctx, inp):
        ctx.save_for_backward(inp)
        return inp

    @staticmethod
    def backward(ctx, grad_output):
        inp = ctx.saved_tensors
        inp = grad_output.clone()
        return inp


class LinLoss(nn.Module):
    def __init__(self):
        super(LinLoss, self).__init__()

    def forward(self, y_hat, y):
        return NillLoss.apply(y_hat - y)

    '''def forward(self, y_hat, y, action):
        res = torch.zeros(4)
        res[action] = y - y_hat[action]
        return res'''


def get_features(sensors, energy, history):
    li = []
    for i in range(4):
        t = tuple(np.roll(x, i * (len(x) // 4)) for x in sensors)
        # print(t)
        # sen = np.hstack(tuple(np.roll(x, i * (len(x) // 4)) for x in sensors))
        sen = np.hstack(t)
        sen = np.hstack((sen, np.array(energy), np.array(history)))
        li.append(sen)

    return torch.from_numpy(np.array(li)).type(torch.FloatTensor)


if __name__ == "__main__":
    episode_count = 100
    lr = 0.3
    nin = 145
    nout = 1
    layers = [30]

    model = NN(nin, nout, layers)
    optimizer = optim.SGD(model.parameters(), lr=lr)
    criterion = nn.LinLoss()

# for i in range(episode_count):
#    while True:
#        
#        ################################
#        # predict U and choose action
#        ob, reward, done, _ = env.step(action)
#        # learn 
#        ##########################
#        
#        rsum+=reward
#        j += 1
#        if envx.verbose:
#            envx.render()
#        if done:
#            print(str(i)+" rsum="+str(rsum)+", "+str(j)+" actions")
#            rsum=0
#            break
#
# print("done")
# env.close()
