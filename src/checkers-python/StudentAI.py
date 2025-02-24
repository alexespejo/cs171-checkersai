import random
import copy
import math
import time
from BoardClasses import Move, Board

def hash_board(board):
    board_tuple = tuple(
        tuple(
            (piece.color, piece.is_king) if piece else None  # Convert Checkers to immutable tuples
            for piece in row
        )
        for row in board
    )
    return hash(board_tuple)

# Heuristic function for evaluating moves
def evaluate_move(board, color):
    """
    A heuristic evaluation function that evaluates the board state from the perspective of the given color.
    This could consider factors such as:
    - Number of opponent pieces captured
    - Number of pieces promoted
    - Position of pieces (e.g., centralization, edge control)
    """
    opponent = 2 if color == 1 else 1
    score = 0

    # Example Heuristic: Favor advancing towards promotion (closer to the opponent's back row)
    for row in board:
        for piece in row:
            if piece:
                if piece.color == color:
                    score += 1  # Count pieces of the AI
                    if piece.is_king:
                        score += 5  # Kings are more valuable
                    # Encourage advancing forward, penalize staying on the back row
                    score += (7 - piece.row) if piece.color == color else 0
                elif piece.color == opponent:
                    score -= 1  # Penalize opponent's pieces

    return score


# MCTS Node definition
class MCTSNode:
    def __init__(self, game_state, color, parent=None, move=None):
        self.game_state = copy.deepcopy(game_state)
        self.color = color
        self.parent = parent
        self.move = move
        self.children = []
        self.visit_count = 0
        self.win_count = 0
        self.uct_value = float('inf')
        self.terminal = False

    def uct(self, num_parent_simulations, exploration_weight=1.41):
        if self.visit_count == 0:
            return 1000  # Prevents unvisited nodes from being ignored
        return (self.win_count / self.visit_count) + exploration_weight * (
            math.sqrt(math.log(num_parent_simulations) / self.visit_count)
        )

    def add_child(self, child_hash, visited):
        self.children.append(child_hash)
        if not self.terminal:
            self.win_count = sum(visited[child].win_count for child in self.children)
            self.visit_count = sum(visited[child].visit_count for child in self.children)


# Student AI definition
class StudentAI:
    def __init__(self, col, row, p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col, row, p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1: 2, 2: 1}
        self.color = 2

    def random_move(self, moves):
        index = random.randint(0, len(moves) - 1)
        inner_index = random.randint(0, len(moves[index]) - 1)
        return moves[index][inner_index]

    def simulate_turn(self, copy_board, color, visited, stack):
        moves = copy_board.get_all_possible_moves(color)
        if not moves:
            result = copy_board.is_win("W" if color == 2 else "B")
            leaf = visited[stack[-1]]
            leaf.terminal, leaf.win_count, leaf.visit_count = True, 1, 1
            return result
        move = self.random_move(moves)
        copy_board.make_move(move, color)
        board_hash = hash_board(copy_board.board)
        if board_hash not in visited:
            visited[board_hash] = MCTSNode(copy_board, color, move=move)
        stack.append(board_hash)
        return None

    def simulate(self, visited, stack):
        copy_board = copy.deepcopy(self.board)
        for _ in range(300):  # Increased iterations for better accuracy
            res = self.simulate_turn(copy_board, self.color, visited, stack)
            if res is not None:
                return res
            res = self.simulate_turn(copy_board, self.opponent[self.color], visited, stack)
            if res is not None:
                return res
        return 0

    def backprop(self, visited, stack):
        while stack:
            node = visited[stack.pop()]
            if stack:
                visited[stack[-1]].add_child(hash_board(node.game_state.board), visited)
        return node

    def get_move(self, move):
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1  # First move, assign player color

        hash_start = hash_board(self.board.board)
        root = MCTSNode(self.board, self.color)
        visited = {hash_start: root}

        moves = self.board.get_all_possible_moves(self.color)
        if not moves:
            return None  # No valid moves

        start_time = time.time()
        time_limit = 5.0  # Max 5 seconds per move

        while time.time() - start_time < time_limit:
            stack = [hash_start]
            self.simulate(visited, stack)
            self.backprop(visited, stack)

        # Select the best move based on visit count (most explored) and heuristic evaluation
        best_move = None
        max_visits = -1
        best_score = -float('inf')

        for c in root.children:
            node = visited[c]
            if node.visit_count > max_visits or (
                    node.visit_count == max_visits and evaluate_move(node.game_state.board, self.color) > best_score):
                max_visits = node.visit_count
                best_score = evaluate_move(node.game_state.board, self.color)
                best_move = node.move

        # Fallback to a random move if no valid move was selected
        if best_move is None:
            best_move = self.random_move(moves)

        self.board.make_move(best_move, self.color)
        return best_move
