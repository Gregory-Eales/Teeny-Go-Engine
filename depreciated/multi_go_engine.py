import numpy as np
import time
import pyspiel
from matplotlib import pyplot as plt

class MultiGoEngine(object):

    def __init__(self, num_games=100):
        self.num_games = num_games
        self.active_games = []
        self.games = {}
        self.game_states = {}
        self.game_x_data = {}
        self.game_y_data = {}
        self.move_tensor = None
        self.generate_game_objects()
        self.move_map = self.get_move_map()

    def get_move_map(self):
        board_size = {"board_size": pyspiel.GameParameter(9)}
        game = pyspiel.load_game("go", board_size)

        state = game.new_initial_state()
        return state.legal_actions()


    def is_playing_games(self):
        return len(self.active_games)>0

    def finalize_game_data(self):

        for game in self.games.keys():

            self.game_x_data[game] = np.concatenate(self.game_x_data[game], axis=0)
            self.game_y_data[game] = np.concatenate(self.game_y_data[game], axis=0)

            rewards = self.games[game].returns()

            # if black wins
            if rewards[0]==1:
                None

            # if white wins
            elif rewards[1]==1:
                self.game_y_data[game][:,82] = self.game_y_data[game][:,82] *-1

            # if draw
            else:
                self.game_y_data[game][:,82] = self.game_y_data[game][:,82]*0

    def take_game_step(self, move_tensor):

        # internalize move_tensor
        self.input_move_tensor(move_tensor)

        # removes invalid moves
        self.remove_invalid_moves()

        # makes moves
        self.make_moves()

        # remove terminal games from active games
        self.remove_inactive_games()

    def input_move_tensor(self, move_tensor):
        self.move_tensor = move_tensor

    def remove_invalid_moves(self):

        valid_move_tensor = []

        for game in self.active_games:
            valid_moves = self.games[game].legal_actions_mask()
            valid_moves = np.array(valid_moves[0:441]).reshape(21, 21)
            valid_moves = valid_moves[1:10,1:10].reshape(81)
            valid_moves = np.append(valid_moves, 1)
            valid_move_tensor.append(valid_moves)

        valid_move_tensor = np.array(valid_move_tensor)
        self.move_tensor[:,0:82] = self.move_tensor[:,0:82] * valid_move_tensor

    def make_moves(self):

        for num, game in enumerate(self.active_games):
            y_input = np.copy(self.move_tensor[num])

            if self.games[game].current_player() == 0:
                y_input[-1] = 1
            elif self.games[game].current_player() == 1:
                y_input[-1] = -1
            else:
                y_input[-1] = 0

            self.game_y_data[game].append(np.copy(y_input.reshape([1, -1])))
            moves = list(range(82))

            sum = np.sum(self.move_tensor[num][0:82])

            if sum > 0:
                move = np.random.choice(moves, p=self.move_tensor[num][0:82]/sum)
            else:
                move = 81
            self.games[game].apply_action(self.move_map[int(move)])



    def get_active_game_states(self):

        states_tensor = []
        for game in self.active_games:
            state = self.games[game].observation_as_normalized_vector()
            state = np.array(state).reshape(-1, 81)
            state = (state[0] + state[1]*-1)
            self.game_states[game].append(np.copy(state.reshape(1, 9, 9)))
            state_tensor = self.generate_state_tensor(game)
            self.game_x_data[game].append(np.copy(state_tensor))
            states_tensor.append(np.copy(state_tensor))
        return np.concatenate(states_tensor)

    def generate_state_tensor(self, game):

        black = []
        white = []
        turn = self.games[game].current_player()

        if turn == 1:
            turn = [np.zeros([1, 9, 9])]

        elif turn == 0:
            turn = [np.ones([1, 9, 9])]

        else:
            print(turn)

        for i in range(1, 6):
            black.append(np.copy(np.where(self.game_states[game][-i] == 1, 1, 0).reshape(1, 9, 9)))
            white.append(np.copy(np.where(self.game_states[game][-i] == -1, 1, 0).reshape(1, 9, 9)))

        black = np.concatenate(black, axis=0)
        white = np.concatenate(white, axis=0)
        turn = np.concatenate(turn, axis=0)

        output = np.concatenate([black, white, turn]).reshape(1, 11, 9, 9)

        return output

    def get_all_game_states(self):
        states_tensor = []
        for i in range(self.num_games):
            states_tensor.append(self.games["G"+str(i)].get_board_tensor())
        return np.copy(np.concatenate(states_tensor))

    def remove_inactive_games(self):

        to_remove = []
        for game in self.active_games:
            if self.games[game].is_terminal() == True:
                to_remove.append(game)

        for game in to_remove:
            self.active_games.remove(game)

    def generate_game_objects(self):

        self.games = {}
        self.game_states = {}
        self.game_x_data = {}
        self.game_y_data = {}
        self.active_games = []
        board_size = {"board_size": pyspiel.GameParameter(9)}
        game = pyspiel.load_game("go", board_size)

        for i in range(self.num_games):
            self.games["G"+str(i)] = game.new_initial_state()
            self.game_states["G"+str(i)] = []
            self.game_x_data["G"+str(i)] = []
            self.game_y_data["G"+str(i)] = []
            for j in range(7):
                self.game_states["G"+str(i)].append(np.zeros([9,9]))
            self.active_games.append("G"+str(i))

    def reset_games(self, num_games=None):
        if self.num_games == None: pass
        else: self.num_games = num_games
        del(self.games)
        del(self.game_states)
        del(self.game_x_data)
        del(self.game_y_data)
        self.generate_game_objects()

    def get_turn(self):
        turn = self.games[self.active_games[0]].current_player()
        return turn

    def get_all_data(self):

        x = []
        y = []

        for game in self.games.keys():
            x.append(self.game_x_data[game])
            y.append(self.game_y_data[game])

        x = np.concatenate(x, axis=0)
        y = np.concatenate(y, axis=0)

        return x, y




def main():
    n = 100
    mge = MultiGoEngine(num_games=n)
    mge.move_tensor = np.ones([n, 83])
    t = time.time()
    active_hist = []
    count = 0
    while mge.is_playing_games():
        
        active_hist.append(len(mge.active_games))
        mge.move_tensor = np.ones([len(mge.active_games), 83])
        mge.get_active_game_states()
        mge.remove_invalid_moves()
        mge.make_moves()
        mge.remove_inactive_games()

        count += 1
        if count > 50:
            break

    mge.finalize_game_data()
    time_took = time.time()-t
    print("Game Step Time:", round(time_took, 3), "s")
    print(round(n/time_took, 3), "games per second")

    mge.get_all_data()
    plt.plot(active_hist)
    plt.show()

if __name__ == "__main__":
    main()
