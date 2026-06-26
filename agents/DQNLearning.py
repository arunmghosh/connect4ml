import random

import torch.cuda

from Strategy import Strategy
from DQN import DQN
from ReplayBuffer import ReplayBuffer
import yaml

device = 'cuda' if torch.cuda.is_available() else 'cpu'


class DQNLearning(Strategy):
    def __init__(self):
        super().__init__("DQN")

        # load hyperparameters
        with open('hyperparameters.yaml', 'r') as file:
            hyperparameters = yaml.safe_load(file)['connectfour1']

        self.replay_buffer_size = hyperparameters['replay_buffer_size']
        self.mini_batch_size = hyperparameters['mini_batch_size']
        self.epsilon_init = hyperparameters['epsilon_init']
        self.epsilon_decay = hyperparameters['epsilon_decay']
        self.epsilon_min = hyperparameters['epsilon_min']

    def learn(self, game, num_trials: int, is_training=True):
        # game is a new instance of the game we are playing, set to start parameters
        policy_dqn = DQN(game.num_states, game.num_actions).to(device)
        if is_training:
            buffer = ReplayBuffer(self.replay_buffer_size)
            epsilon = self.epsilon_init

        for t in range(num_trials):
            # copy and flatten the grid into one row
            state = torch.tensor(game.board_state.flatten(), dtype=torch.float32, device=device)
            game_log = []
            while not game.game_finished:
                if is_training and random.random() < epsilon:
                    sample_move = game.sample_move_space()
                    sample_move = torch.tensor(sample_move, dtype=torch.int64, device=device)
                else:
                    with torch.no_grad():
                        sample_move = policy_dqn(state.unsqueeze(dim=0)).squeeze().argmax()  # automatically a tensor
                new_state, reward, terminated = game.step(sample_move.item())
                new_state = torch.tensor(new_state, dtype=torch.float, device=device)
                reward = torch.tensor(reward, dtype=torch.float, device=device)

                if is_training:
                    log_entry = [state, sample_move, new_state, reward, terminated]
                    game_log.append(log_entry)
                    epsilon = max(epsilon * self.epsilon_decay, self.epsilon_min)

                state = new_state

            # if someone won the game, change the second to last reward to -1, since that move allowed the win (+1)
            if game_log[-1][3] == 1:
                game_log[-2][3] = -1

            # push the data to the replay buffer
            if is_training:
                buffer.push_game(game_log)

            # reset the game and decay epsilon for epsilon-greedy algorithm
            game.reset()

    def choose_move(self, possible_moves, game):
        # assume we've already learned
        return super().choose_move(possible_moves, game)
