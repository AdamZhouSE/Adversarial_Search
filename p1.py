import sys, random, grader, parse

DIRECTIONS = {
    'N': (-1, 0),
    'S': (1, 0),
    'E': (0, 1),
    'W': (0, -1),
}

PACMAN_SCORES = {
    'FOOD': 10,
    'LOSE': -500,
    'WIN': 500,
    'MOVE': -1
}

PACMAN = 'P'
GHOST = 'W'
FOOD = '.'
WALL = '%'
EMPTY = ' '


class Board:
    """
    Board class for pacman game, record the positions of pacman, ghosts and food
    """
    def __init__(self, board):
        self.board = board
        # only one pacman while multiple ghosts and food
        self.pacman_pos = self.find_pacman_pos()
        # only one ghost W for p1&p2
        self.ghost_list = ['W']
        # use a dict here for solving multi-ghost questions easier later
        self.ghost_pos_dict = self.find_ghost_pos_dict()
        self.food_pos_list = self.find_food_pos_list()

    def find_pacman_pos(self):
        return self.find_entity_pos(PACMAN)

    def find_ghost_pos_dict(self):
        position_dict = {}
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board[row][col] in self.ghost_list:
                    position_dict[self.board[row][col]] = (row, col)
        return position_dict

    def find_food_pos_list(self):
        return self.find_entity_pos(FOOD, multiple=True)

    def find_entity_pos(self, entity, multiple=False):
        """
        find positions for the given entity, including pacman and food
        the flag multiple is used to decide whether the entity is multiple
        """
        position_list = []
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board[row][col] == entity:
                    if multiple:
                        position_list.append((row, col))
                    else:
                        return row, col
        return position_list if multiple else None

    def get_valid_directions_in_order(self, pos):
        valid_directions = []
        for direction in DIRECTIONS.keys():
            if self.check_valid_move(pos, direction):
                valid_directions.append(direction)
        # sort alphabetically to get expected results
        valid_directions.sort()
        return valid_directions

    def check_valid_move(self, pos, direction):
        start_row, start_col = pos
        d_row, d_col = DIRECTIONS[direction]
        return self.board[start_row + d_row][start_col + d_col] != WALL

    def move_by_direction(self, pos, direction):
        d_row, d_col = DIRECTIONS[direction]
        return pos[0] + d_row, pos[1] + d_col

    def update_board(self, pos, new_pos, entity):
        # the ghost can be on the top of the food, restore food after the ghost leaves
        if entity in self.ghost_list and pos in self.food_pos_list:
            self.board[pos[0]][pos[1]] = FOOD
        else:
            self.board[pos[0]][pos[1]] = EMPTY
        # the pacman commits suicide, leave the ghost sign
        if entity == PACMAN and new_pos in self.ghost_pos_dict.values():
            self.board[new_pos[0]][new_pos[1]] = self.board[new_pos[0]][new_pos[1]]
        else:
            self.board[new_pos[0]][new_pos[1]] = entity

    def __str__(self):
        return '\n'.join(''.join(row) for row in self.board) + '\n'


class Game:
    """
    Basic class for pacman game, implement the moving logic
    both the pacman and ghost move randomly
    """
    def __init__(self, board):
        self.board = board
        self.score = 0
        self.steps_count = 0
        self.winner = None
        self.game_over = False
        self.player = None

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

            self.player = GHOST
            ghost_direction = self.choose_ghost_direction()
            solution += self.handle_ghost(ghost_direction)
        solution += f'WIN: {self.winner}'
        return solution

    def choose_pacman_direction(self):
        return random.choice(self.board.get_valid_directions_in_order(self.board.pacman_pos))

    def choose_ghost_direction(self):
        return random.choice(
            self.board.get_valid_directions_in_order(self.board.ghost_pos_dict[self.player]))

    def handle_pacman(self, direction):
        """
        handle the pacman's move, update the board, score and check the game status
        """
        # pacman moves
        new_pacman_pos = self.board.move_by_direction(self.board.pacman_pos, direction)
        self.board.update_board(self.board.pacman_pos, new_pacman_pos, PACMAN)
        self.board.pacman_pos = new_pacman_pos

        # check if the pacman eats food
        if new_pacman_pos in self.board.food_pos_list:
            self.board.food_pos_list.remove(new_pacman_pos)
            self.score += PACMAN_SCORES['FOOD']
            # check if the pacman eats all food -> pacman wins
            if len(self.board.food_pos_list) == 0:
                self.score += PACMAN_SCORES['WIN']
                self.winner = 'Pacman'
                self.game_over = True
        # suicide -> ghost wins
        # compare with all the ghosts' coordinates
        if new_pacman_pos in self.board.ghost_pos_dict.values():
            self.score += PACMAN_SCORES['LOSE']
            self.winner = 'Ghost'
            self.game_over = True

        self.score += PACMAN_SCORES['MOVE']
        return self.generate_state(PACMAN, direction)

    def handle_ghost(self, direction):
        """
        handle ghost's move, update the board, score and check the game status
        """
        # ghost moves
        old_ghost_pos = self.board.ghost_pos_dict[self.player]
        new_ghost_pos = self.board.move_by_direction(old_ghost_pos, direction)
        self.board.update_board(old_ghost_pos, new_ghost_pos, self.player)
        self.board.ghost_pos = new_ghost_pos
        self.board.ghost_pos_dict[self.player] = new_ghost_pos
        # the ghost eats the pacman -> ghost wins
        if new_ghost_pos == self.board.pacman_pos:
            self.score += PACMAN_SCORES['LOSE']
            self.winner = 'Ghost'
            self.game_over = True
        return self.generate_state(self.player, direction)

    def generate_initial_state(self, seed):
        return f"seed: {seed}\n0\n{self.board}"

    def generate_state(self, player, direction):
        self.steps_count += 1
        return f"{self.steps_count}: {player} moving {direction}\n{self.board}score: {self.score}\n"


def random_play_single_ghost(problem):
    board = Board(problem['board'])
    game = Game(board)
    return game.play_game_randomly(problem['seed'])


if __name__ == "__main__":
    test_case_id = int(sys.argv[1])
    problem_id = 1
    grader.grade(problem_id, test_case_id, random_play_single_ghost, parse.read_layout_problem)
