import random
import torch.nn as nn
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
        self.network_sync_rate = hyperparameters['network_sync_rate']
        self.learning_rate = hyperparameters['learning_rate']
        self.discount_factor = hyperparameters['discount_factor']

        self.loss_fn = nn.MSELoss()
        self.optimizer = None

    def optimize(self, mini_batch, policy_net, target_net):
        states, actions, new_states, rewards, terminations = zip(*mini_batch)
        states = torch.stack(states)
        actions = torch.stack(actions)
        new_states = torch.stack(new_states)
        rewards = torch.stack(rewards)
        terminations = torch.tensor(terminations).float().to(device)

        with torch.no_grad():
            # calculate expected rewards
            # if termination is true, target_q is the exact "rewards" since (1 - terminations) == 0
            target_q = rewards + (1 - terminations) * self.discount_factor * target_net(new_states).max(dim=1)[0]

        # calculate current_q from policy_net
        current_q = policy_net(states).gather(dim=1, index=actions.unsqueeze(dim=1)).squeeze()

        # compute loss and optimize
        loss = self.loss_fn(current_q, target_q)
        loss.backward()
        self.optimizer.step()

    def learn(self, game, num_trials: int, is_training=True):
        # game is a new instance of the game we are playing, set to start parameters
        policy_dqn = DQN(game.num_states, game.num_actions).to(device)
        if is_training:
            buffer = ReplayBuffer(self.replay_buffer_size)
            epsilon = self.epsilon_init
            target_dqn = DQN(game.num_states, game.num_actions).to(device)
            target_dqn.load_state_dict(policy_dqn.state_dict())

            # want to track how many training steps we've taken, and sync after an appropriate interval
            step_count = 0
            self.optimizer = torch.optim.Adam(policy_dqn.parameters(), lr = self.learning_rate)

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
                new_state = torch.tensor(new_state.flatten(), dtype=torch.float, device=device)
                reward = torch.tensor(reward, dtype=torch.float, device=device)

                if is_training:
                    log_entry = [
                                state,  # float32 tensor [42]
                                sample_move,  # int64 tensor
                                new_state,  # float32 tensor [42]
                                reward,  # float32 tensor
                                terminated  # bool, handled in optimize
                                ]
                    game_log.append(log_entry)
                    epsilon = max(epsilon * self.epsilon_decay, self.epsilon_min)
                    step_count += 1

                    # when we've reached the mini batch size in memory, resync target to policy network
                    if len(buffer) > self.mini_batch_size:
                        mini_batch = buffer.sample(self.mini_batch_size)
                        self.optimize(mini_batch, policy_dqn, target_dqn)

                        if step_count > self.network_sync_rate:
                            target_dqn.load_state_dict(policy_dqn.state_dict())
                            step_count = 0

                state = new_state

            # if someone won the game, change the second to last reward to -1, since that move allowed the win (+1)
            if game_log[-1][3].item() == 1.0:
                game_log[-2][3] = torch.tensor(-1.0, dtype=torch.float32, device=device)

            # push the data to the replay buffer
            if is_training:
                buffer.push_game(game_log)

            # reset the game and decay epsilon for epsilon-greedy algorithm
            game.reset()

    def choose_move(self, possible_moves, game):
        # assume we've already learned
        return super().choose_move(possible_moves, game)
