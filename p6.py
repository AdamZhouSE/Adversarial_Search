import sys, parse
import time, os, copy
from p1 import PACMAN
from p3 import MultiGhostBoard
from p5 import MinimaxGame
import random


class ExpectiMaxGame(MinimaxGame):
    """
    Based on MinimaxGame, we implement an expecti-max pacman against multiple random ghosts
    """

    def play_game_with_expectimax(self, seed):
        if seed != -1:
            random.seed(seed, version=1)
        solution = self.generate_initial_state(seed)

        while not self.game_over:
            self.player = PACMAN
            # use expecti-max to decide the best move
            pacman_direction = self.expecti_max()
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

    def expecti_max(self):
        """
        get best move through expecti-max
        """
        simulation_board = copy.deepcopy(self.board)
        initial_state = self.get_state(simulation_board, self.depth, self.player)
        self.expecti_pacman(initial_state)
        # print('best_move:',  initial_state['best_move'])
        return initial_state['best_move']

    def expecti_pacman(self, state):
        """
        maximum pac-man's value and return the best value
        """
        if self.terminal_state(state):
            return self.evaluate(state['board'])

        best_value = float('-inf')
        for direction in state['board'].get_valid_directions_in_order(state['board'].pacman_pos):
            new_state = self.simulate_move(state, direction, PACMAN)
            # record the visited positions
            self.visited_positions.append(new_state['board'].pacman_pos)
            value = self.expecti_ghost(new_state)
            self.visited_positions.pop()
            if value > best_value:
                best_value = value
                # record the best move
                state['best_move'] = direction
        return best_value

    def expecti_ghost(self, state):
        """
        ghosts are chance nodes in expecti-max, and the probability of each direction is equal
        """
        if self.terminal_state(state):
            return self.evaluate(state['board'])

        total_value = 0
        valid_directions = state['board'].get_valid_directions_in_order(state['board'].ghost_pos_dict[state['player']])
        # if the ghost is stuck, return directly
        if not valid_directions:
            return total_value
        for direction in valid_directions:
            new_state = self.simulate_move(state, direction, state['player'])
            # decide min or max method by the next player
            value = self.expecti_pacman(new_state) if new_state['player'] == PACMAN else self.expecti_ghost(new_state)
            total_value += value
        return total_value / len(valid_directions)

    def terminal_state(self, state):
        """
        check if the state is terminal: reach the bottom or game over
        """
        game_over, _ = self.simulate_game_over(state['board'])
        return state['depth'] == 0 or game_over

    def evaluate(self, board):
        """
        evaluate the end state by manhattan distance or bfs
        switch the method by the size of the board, deciding by the number of walls
        if the board is small, use manhattan distance to get the result faster, otherwise use bfs

        The key is to avoid pacman moving in a loop, ex N -> S -> N -> S ...
        so we give a penalty if pacman visits the same position and encourage pacman to eat food
        """
        pacman_pos = board.pacman_pos
        ghost_pos_list = board.ghost_pos_dict.values()
        food_pos_list = board.food_pos_list

        # if the pacman wins, give it a large bonus
        if not food_pos_list:
            return 10000

        # if ghosts win, give it a heavy penalty
        if pacman_pos in ghost_pos_list:
            return -10000

        # Give a bonus if pacman eats food, encourage pacman to eat food
        value = (len(self.board.food_pos_list) - len(board.food_pos_list)) * 100

        # Give a penalty if pacman visits the same position
        if board.pacman_pos in self.visited_positions:
            value -= 100 * self.visited_positions.count(board.pacman_pos)

        value += self.evaluate_manhattan(board) if self.wall_count < self.switch_count else self.evaluate_bfs(board)
        return value

    def evaluate_bfs(self, board):
        """
        evaluate the end state by bfs
        It seems that in large and complex boards, give eating food a higher weight will avoid pacman moving in a loop
        """
        closest_food_distance = self.calculate_bfs(board, board.pacman_pos, board.food_pos_list)
        closest_ghost_distance = self.calculate_bfs(board, board.pacman_pos, board.ghost_pos_dict.values())
        # avoiding pacman moving in a loop, so we give a higher weight to the food here
        return -3 * closest_food_distance + closest_ghost_distance


def expecti_max_multiple_ghosts(problem, k):
    board = MultiGhostBoard(problem['board'])
    game = ExpectiMaxGame(board, k)
    return game.play_game_with_expectimax(problem['seed'])


if __name__ == "__main__":
    test_case_id = int(sys.argv[1])
    problem_id = 6
    file_name_problem = str(test_case_id) + '.prob'
    file_name_sol = str(test_case_id) + '.sol'
    path = os.path.join('test_cases', 'p' + str(problem_id))
    problem = parse.read_layout_problem(os.path.join(path, file_name_problem))
    k = int(sys.argv[2])
    num_trials = int(sys.argv[3])
    verbose = bool(int(sys.argv[4]))
    print('test_case_id:', test_case_id)
    print('k:', k)
    print('num_trials:', num_trials)
    print('verbose:', verbose)
    start = time.time()
    win_count = 0
    for i in range(num_trials):
        solution, winner = expecti_max_multiple_ghosts(copy.deepcopy(problem), k)
        if winner == 'Pacman':
            win_count += 1
        if verbose:
            print(solution)
    win_p = win_count / num_trials * 100
    end = time.time()
    print('time: ', end - start)
    print('win %', win_p)
