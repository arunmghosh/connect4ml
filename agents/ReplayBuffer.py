from collections import deque
import random


class ReplayBuffer:

    def __init__(self, max_length):
        self.memory = deque(maxlen=max_length)

    def push(self, transition):
        # transition is (state, action, reward, next_state, done)
        self.memory.append(transition)

    def push_game(self, game_log):
        # game log is a list of transitions
        for t in game_log:
            self.memory.append(t)

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)
