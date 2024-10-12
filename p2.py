import sys, parse
import time, os, copy
from p1 import Board, Game
from p1 import PACMAN, GHOST
import random


def calculate_manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


class SmartGame(Game):
    """
    Smart pacman game, pacman will choose the best move based on an evaluation function
    """
    def play_game_smart(self, seed):
        if seed != -1:
            random.seed(seed, version=1)
        solution = self.generate_initial_state(seed)

        while not self.game_over:
            # pacman has a smarter movement
            self.player = PACMAN
            pacman_direction = self.choose_pacman_direction_smart()
            solution += self.handle_pacman(pacman_direction)
            if self.game_over:
                break

            self.player = GHOST
            ghost_direction = self.choose_ghost_direction()
            solution += self.handle_ghost(ghost_direction)
        solution += f'WIN: {self.winner}'
        return solution, self.winner

    def choose_pacman_direction_smart(self):
        """
        use a simple evaluation method to choose the best move for pacman
        """
        best_score = float('-inf')
        best_move = None
        valid_directions = self.board.get_valid_directions_in_order(self.board.pacman_pos)
        for direction in valid_directions:
            score = self.evaluate(direction)
            if score > best_score:
                best_score = score
                best_move = direction
        return best_move

    def evaluate(self, direction):
        """
        Evaluate the score of a move
        combine the distance to the closest food and the distance to the ghost
        """
        new_pacman_pos = self.board.move_by_direction(self.board.pacman_pos, direction)

        distance_to_ghost = calculate_manhattan_distance(new_pacman_pos, self.board.ghost_pos_dict[GHOST])
        # may have multiple food
        closest_to_food = float('inf')
        for food_pos in self.board.food_pos_list:
            distance_to_food = calculate_manhattan_distance(new_pacman_pos, food_pos)
            if distance_to_food < closest_to_food:
                closest_to_food = distance_to_food
        # minimize the distance to food and maximize the distance to the ghost
        # pacman will have a higher chance to win if it is far from the ghost, so give the ghost a higher weight
        return -closest_to_food + 1.5 * distance_to_ghost


def better_play_single_ghosts(problem):
    board = Board(problem['board'])
    game = SmartGame(board)
    return game.play_game_smart(problem['seed'])


if __name__ == "__main__":
    test_case_id = int(sys.argv[1])
    problem_id = 2
    file_name_problem = str(test_case_id) + '.prob'
    file_name_sol = str(test_case_id) + '.sol'
    path = os.path.join('test_cases', 'p' + str(problem_id))
    problem = parse.read_layout_problem(os.path.join(path, file_name_problem))
    num_trials = int(sys.argv[2])
    verbose = bool(int(sys.argv[3]))
    print('test_case_id:', test_case_id)
    print('num_trials:', num_trials)
    print('verbose:', verbose)
    start = time.time()
    win_count = 0
    for i in range(num_trials):
        solution, winner = better_play_single_ghosts(copy.deepcopy(problem))
        if winner == 'Pacman':
            win_count += 1
        if verbose:
            print(solution)
    win_p = win_count / num_trials * 100
    end = time.time()
    print('time: ', end - start)
    print('win %', win_p)
