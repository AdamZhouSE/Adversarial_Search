import sys, parse
import time, os, copy
from p1 import PACMAN
from p2 import SmartGame
from p2 import calculate_manhattan_distance
from p3 import MultiGhostBoard, MultiGhostGame
import random


class SmartGameWithMultiGhost(MultiGhostGame, SmartGame):
    """
    Based on p3, we implement a smart pacman against multiple random ghosts.
    """
    def play_game_smart(self, seed):
        # ensure random.choice in a fixed order
        if seed != -1:
            random.seed(seed, version=1)
        solution = self.generate_initial_state(seed)

        while not self.game_over:
            self.player = PACMAN
            pacman_direction = self.choose_pacman_direction_smart()
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
        return solution, self.winner

    def evaluate(self, direction):
        """
        As we have multiple ghosts, here we consider the distance to the closest ghost.
        """
        new_pacman_pos = self.board.move_by_direction(self.board.pacman_pos, direction)

        closest_to_ghost = float('inf')
        for ghost_pos in self.board.ghost_pos_dict.values():
            distance_to_ghost = calculate_manhattan_distance(new_pacman_pos, ghost_pos)
            if distance_to_ghost < closest_to_ghost:
                closest_to_ghost = distance_to_ghost

        closest_to_food = float('inf')
        for food_pos in self.board.food_pos_list:
            distance_to_food = calculate_manhattan_distance(new_pacman_pos, food_pos)
            if distance_to_food < closest_to_food:
                closest_to_food = distance_to_food
        # minimize the distance to food and maximize the distance to the ghost
        # pacman will have a higher chance to win if it is far from the ghost, so give the ghost a higher weight
        return -closest_to_food + 2 * closest_to_ghost


def better_play_multiple_ghosts(problem):
    board = MultiGhostBoard(problem['board'])
    game = SmartGameWithMultiGhost(board)
    return game.play_game_smart(problem['seed'])


if __name__ == "__main__":
    test_case_id = int(sys.argv[1])
    problem_id = 4
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
        solution, winner = better_play_multiple_ghosts(copy.deepcopy(problem))
        if winner == 'Pacman':
            win_count += 1
        if verbose:
            print(solution)
    win_p = win_count / num_trials * 100
    end = time.time()
    print('time: ', end - start)
    print('win %', win_p)
