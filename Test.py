from agents.Heuristic import Heuristic
from agents.Minimax import Minimax
from agents.DQNLearning import DQNLearning
from Player import Player
from games.ConnectFour import ConnectFour


def pre_train_agents(heuristic, minimax, dqn, train_game_type, duration: int):
    # the agents are PLayer instances
    # train_game_type is an instance of a child class of DeterministicGame
    training1 = train_game_type([heuristic, minimax])  # train the minimax by filling transposition table
    for t in range(duration):
        training1.play_game()
        training1.reset()

    training2 = train_game_type([minimax, dqn])  # with trained minimax, now train dqn
    dqn.strategy.learn(training2, duration, True)


if __name__ == "__main__":
    h = Player(False, Heuristic())
    m = Player(False, Minimax())
    d = Player(False, DQNLearning())
    pre_train_agents(h, m, d, ConnectFour, 10)
