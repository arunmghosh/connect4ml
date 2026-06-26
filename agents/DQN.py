import torch
from torch import nn


class DQN(nn.Module):

    def __init__(self, state_dim, action_dim, hidden_dim=128):
        super(DQN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),

            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),

            nn.Linear(hidden_dim, action_dim)
        )

    def forward(self, x):
        return self.net(x)


if __name__ == '__main__':
    st = 42
    act = 7
    net = DQN(st, act)
    board = torch.randn(1, st)
    output = net(board)
    print(output)