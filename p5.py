import sys, parse
import time, os, copy
from p1 import PACMAN
from p2 import calculate_manhattan_distance
from p3 import MultiGhostBoard, MultiGhostGame
from collections import deque


class MinimaxGame(MultiGhostGame):
    """
    Based on p3, we implement a minimax pacman against multiple minimax ghosts
    """

    def __init__(self, board, depth):
        super().__init__(board)
        # k means the depth of the minimax search
        self.depth = depth
        # count the number of walls, which decide the evaluation method
        self.wall_count = self.count_wall()
        # the standard to switch the evaluation method
        self.switch_count = 100
        # record the visited positions of the pacman
        self.visited_positions = []

    def play_game_with_minimax(self, seed):
        """
        play the game with minimax search
        here we only use minimax once, and find out if pacman can win in k steps
        """
        solution = self.generate_initial_state(seed)

        self.player = PACMAN
        self.minimax()
        # if the pacman does not win in k steps, ghosts win
        if not self.winner:
            self.winner = 'Ghost'

        # In p5, we can't record every step of the game.
        solution += f'WIN: {self.winner}'
        return solution, self.winner

    def minimax(self):
        simulation_board = copy.deepcopy(self.board)
        initial_state = self.get_state(simulation_board, self.depth, self.player)
        if self.player == PACMAN:
            self.minimax_pacman(initial_state, float('-inf'), float('inf'))
        else:
            self.minimax_ghost(initial_state, float('-inf'), float('inf'))
        return initial_state['best_move']

    def minimax_pacman(self, state, alpha, beta):
        """
        maximum pac-man's value and return the best value
        """
        if self.terminal_state(state):
            return self.evaluate(state['board'])

        best_value = float('-inf')
        for direction in state['board'].get_valid_directions_in_order(state['board'].pacman_pos):
            new_state = self.simulate_move(state, direction, PACMAN)
            value = self.minimax_ghost(new_state, alpha, beta)
            if value > best_value:
                best_value = value
                state['best_move'] = direction
            # pruning
            alpha = max(alpha, best_value)
            if alpha >= beta:
                break
        return best_value

    def minimax_ghost(self, state, alpha, beta):
        """
        minimum ghost's value and return the best value
        """
        if self.terminal_state(state):
            return self.evaluate(state['board'])

        best_value = float('inf')
        valid_directions = state['board'].get_valid_directions_in_order(state['board'].ghost_pos_dict[state['player']])
        # if the ghost is stuck, return directly
        if not valid_directions:
            return best_value
        for direction in valid_directions:
            new_state = self.simulate_move(state, direction, state['player'])
            # decide min or max method by the next player
            value = self.minimax_pacman(new_state, alpha, beta) if new_state[
                                                                       'player'] == PACMAN else self.minimax_ghost(
                new_state, alpha, beta)
            if value < best_value:
                best_value = value
                state['best_move'] = direction
            # pruning
            beta = min(beta, best_value)
            if alpha >= beta:
                break
        return best_value

    def terminal_state(self, state):
        """
        check if the state is terminal: reach the bottom or game over
        """
        game_over, winner = self.simulate_game_over(state['board'])
        # if the pacman wins in a leaf node, make the winner as pacman
        if game_over and winner == 'Pacman':
            self.winner = 'Pacman'
        return state['depth'] == 0 or game_over

    def simulate_move(self, state, direction, player):
        """
        simulate the move in minimax search, not change the original board
        """
        new_board = copy.deepcopy(state['board'])
        if player == PACMAN:
            new_pacman_pos = new_board.move_by_direction(new_board.pacman_pos, direction)
            new_board.update_board(new_board.pacman_pos, new_pacman_pos, player)
            new_board.pacman_pos = new_pacman_pos
            if new_pacman_pos in new_board.food_pos_list:
                new_board.food_pos_list.remove(new_pacman_pos)
        else:
            ghost_pos = new_board.ghost_pos_dict[player]
            new_ghost_pos = new_board.move_by_direction(ghost_pos, direction)
            new_board.update_board(ghost_pos, new_ghost_pos, player)
            new_board.ghost_pos_dict[player] = new_ghost_pos

        next_player = self.get_next_player(player, new_board.ghost_list)
        return self.get_state(new_board, state['depth'] - 1, next_player)

    def get_next_player(self, player, ghost_list):
        if player == PACMAN:
            return ghost_list[0]
        elif player == ghost_list[-1]:
            return PACMAN
        else:
            return ghost_list[(ghost_list.index(player) + 1) % len(ghost_list)]

    def evaluate(self, board):
        """
        evaluate the end state by manhattan distance or bfs
        switch the method by the size of the board, deciding by the number of walls
        if the board is small, use manhattan distance to get the result faster, otherwise use bfs
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

        return self.evaluate_manhattan(board) if self.wall_count < self.switch_count else self.evaluate_bfs(board)

    def evaluate_bfs(self, board):
        """
        evaluate the end state by bfs
        """
        closest_food_distance = self.calculate_bfs(board, board.pacman_pos, board.food_pos_list)
        closest_ghost_distance = self.calculate_bfs(board, board.pacman_pos, board.ghost_pos_dict.values())
        # avoiding pacman moving in a loop, so we give a higher weight to the food here
        return -closest_food_distance + 2 * closest_ghost_distance

    def calculate_bfs(self, board, pos, target_pos_list):
        """
        calculate the minimum distance from pos to target_pos_list
        """
        visited = set()
        queue = deque([(pos, 0)])
        while queue:
            pos, distance = queue.popleft()
            if pos in target_pos_list:
                return distance
            if pos in visited:
                continue
            visited.add(pos)
            for direction in board.get_valid_directions_in_order(pos):
                new_pos = board.move_by_direction(pos, direction)
                queue.append((new_pos, distance + 1))
        return float('inf')

    def evaluate_manhattan(self, board):
        """
        evaluate the end state
        consider the manhattan distance between pacman, ghosts and food
        """
        closest_to_ghost = self.get_closest_distance(board.pacman_pos, board.ghost_pos_dict.values())
        closest_to_food = self.get_closest_distance(board.pacman_pos, board.food_pos_list)

        return -closest_to_food + 2 * closest_to_ghost

    def get_closest_distance(self, pos, target_pos_list):
        closest_distance = float('inf')
        for target_pos in target_pos_list:
            distance = calculate_manhattan_distance(pos, target_pos)
            if distance < closest_distance:
                closest_distance = distance
        return closest_distance

    def simulate_game_over(self, board):
        pacman_pos = board.pacman_pos
        ghost_pos_list = board.ghost_pos_dict.values()
        food_pos_list = board.food_pos_list

        # judge if the game is over when doing minimax search
        if pacman_pos in ghost_pos_list:
            return True, 'Ghost'
        if not food_pos_list:
            return True, 'Pacman'
        return False, None

    def get_state(self, board, depth, player):
        return {
            'depth': depth,
            'player': player,
            'board': board,
            'best_move': None,
        }

    def count_wall(self):
        wall_count = 0
        for row in self.board.board:
            wall_count += row.count('%')
        return wall_count


def min_max_multiple_ghosts(problem, k):
    board = MultiGhostBoard(problem['board'])
    game = MinimaxGame(board, k)
    return game.play_game_with_minimax(problem['seed'])


if __name__ == "__main__":
    test_case_id = int(sys.argv[1])
    problem_id = 5
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
        solution, winner = min_max_multiple_ghosts(copy.deepcopy(problem), k)
        if winner == 'Pacman':
            win_count += 1
        if verbose:
            print(solution)
    win_p = win_count / num_trials * 100
    end = time.time()
    print('time: ', end - start)
    print('win %', win_p)
