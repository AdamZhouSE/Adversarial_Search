import sys, grader, parse, math
from p1 import Board, Game
from p1 import DIRECTIONS
from p1 import PACMAN, WALL
import random


class MultiGhostBoard(Board):
    """
    Bases on the Board class in p1, we add more ghosts (up to 4) and ensure that ghosts move in alphabetical order.
    """
    def __init__(self, board):
        super().__init__(board)
        # we may have up to 4 ghosts
        self.ghost_list = ['W', 'X', 'Y', 'Z']
        # ensure that ghosts move in alphabetical order
        self.ghost_pos_dict = dict(sorted(self.find_ghost_pos_dict().items()))
        # get exact ghost list
        self.ghost_list = list(self.ghost_pos_dict.keys())
        self.food_pos_list = self.find_food_pos_list()

    def check_valid_move(self, pos, direction):
        """
        Based on the original board, here we have to consider multiple ghosts.
        """
        start_row, start_col = pos
        d_row, d_col = DIRECTIONS[direction]
        end_row, end_col = start_row + d_row, start_col + d_col
        # Ghosts can't move on top of each other.
        if self.board[start_row][start_col] in self.ghost_list and self.board[end_row][end_col] in self.ghost_list:
            return False
        return self.board[end_row][end_col] != WALL


class MultiGhostGame(Game):
    """
    Bases on the Game class in p1, we implement random movement for the pacman and ghosts.
    """
    def play_game_randomly(self, seed):
        # ensure random.choice in a fixed order
        if seed != -1:
            random.seed(seed, version=1)
        solution = self.generate_initial_state(seed)

        while not self.game_over:
            self.player = PACMAN
            pacman_direction = self.choose_pacman_direction()
            solution += self.handle_pacman(pacman_direction)
            if self.game_over:
                break

            # handle multiple ghosts
            for ghost in self.board.ghost_list:
                self.player = ghost
                ghost_direction = self.choose_ghost_direction()
                if not ghost_direction:
                    # Even if a ghost is stuck, we still have to print it.
                    solution += self.generate_state(self.player, '')
                else:
                    solution += self.handle_ghost(ghost_direction)
                # The game may end at each ghost
                if self.game_over:
                    break
        solution += f'WIN: {self.winner}'
        return solution

    def choose_ghost_direction(self):
        ghost_pos = self.board.ghost_pos_dict[self.player]
        valid_directions = self.board.get_valid_directions_in_order(ghost_pos)
        # If a Ghost is stuck no move will be done.
        if not valid_directions:
            return None
        return random.choice(self.board.get_valid_directions_in_order(ghost_pos))


def random_play_multiple_ghosts(problem):
    board = MultiGhostBoard(problem['board'])
    game = MultiGhostGame(board)
    return game.play_game_randomly(problem['seed'])


if __name__ == "__main__":
    test_case_id = int(sys.argv[1])
    problem_id = 3
    grader.grade(problem_id, test_case_id, random_play_multiple_ghosts, parse.read_layout_problem)
