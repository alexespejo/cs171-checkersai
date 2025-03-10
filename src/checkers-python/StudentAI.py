import random
import math
import copy
import hashlib
import time
from BoardClasses import Move
from BoardClasses import Board

#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

def hash_board(board: Board) -> str:
    """
    Hashes the checkers board state.
    :param board: Board object
    :return: Hash value as a hexadecimal string
    """
    board_str = "".join(
        f"{checker.color}{'K' if checker.is_king else ''}{checker.row}{checker.col}" 
        for row in board
        for checker in row
    )
    return hashlib.sha256(board_str.encode()).hexdigest()

def valid_move(moves: list, max_move: Move) -> bool:
    """
    Checks if a move is in the list of valid moves.
    :param moves: List of possible moves
    :param max_move: Move to validate
    :return: True if valid, False otherwise
    """
    for row in moves:
        for move in row:
            if str(move) == str(max_move):
                return True
    return False

def has_only_one_item(matrix: list) -> bool:
    """
    Checks if a matrix has only one item.
    :param matrix: List of lists
    :return: True if only one item, False otherwise
    """
    count = 0
    for row in matrix:
        count += len(row)
        if count > 1:
            return False
    return count == 1

def winning(color: int, board: Board) -> bool:
    """
    Determines if the given color is winning.
    :param color: Player color (1 for white, 2 for black)
    :param board: Current board state
    :return: True if winning, False otherwise
    """
    white_pieces = 0
    black_pieces = 0
    white_kings = 0
    black_kings = 0

    for row in board:
        for checker in row:
            if checker:
                if checker.color == "W":
                    white_pieces += 1
                    if checker.is_king:
                        white_kings += 1
                else:
                    black_pieces += 1
                    if checker.is_king:
                        black_kings += 1
    total_pieces = white_pieces + black_pieces

    if total_pieces > 20: 
        piece_weight = 1.0
        king_weight = 1.5
    elif 10 <= total_pieces <= 20:  
        piece_weight = 1.0
        king_weight = 2.0
    else:  
        piece_weight = 1.0
        king_weight = 3.0 

    white_score = (
        piece_weight * (white_pieces - white_kings)
        + king_weight * white_kings
    )
    black_score = (
        piece_weight * (black_pieces - black_kings)
        + king_weight * black_kings
    )

    if color == 1:
        return white_score < black_score
    else:
        return black_score < white_score
        
class MCTSNode:
    def __init__(self, parent=None, move=None, color=None):
        self.parent = parent
        self.move = move
        self.color = color
        self.children = set()
        self.terminal = False
        self.visits = 0
        self.wins = 0
        self.limited = False
        self.winner = None

    def uct(self,  num_parent_simulations: int, exploration_weight: float = 1.0) -> float:
        """
        Calculates the UCT value.
        :param num_parent_simulations: Number of parent simulations
        :param exploration_weight: Exploration factor
        :return: UCT value
        """
        if self.visits == 0:
            return float('inf')
        return (self.wins/ self.visits) + exploration_weight * (math.sqrt(math.log(num_parent_simulations) / self.visits))

class StudentAI():
    def __init__(self, col, row, p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.opponent = {1:2,2:1}
        self.color = 2
        self.visited = {}
        self.stack = [] # odd length for player win, even length for opponent win
        self.terminal_nodes = 0
        self.root = None
        self.iterations = 1000
        self.leaves = 0
        self.cycles = 0
        self.limit_reached = 0
        self.move = None
        self.prev_node = None

    def make_terminal(self, node: MCTSNode) -> None:
        """
        Makes node terminal.
        :param node: Node to make terminal
        """
        self.terminal_nodes += 1
        node.terminal = True
        node.wins = 1
        node.visits = 1

    def random_move(self, moves: list) -> Move:
        """
        Selects a random move from available moves.
        :param moves: List of possible moves
        :return: Randomly selected move
        """
        if not moves: 
            return None
        index = random.randint(0, len(moves) - 1)
        inner_index = random.randint(0, len(moves[index]) - 1)
        return moves[index][inner_index]

    def simulate_turn(self, board: Board, color: int) -> MCTSNode:
        """
        Simulates a turn in the game.
        :param board: Current board state
        :param color: Player color
        :return: Node representing the result of the turn
        """
        is_win = board.is_win(color)
        moves = board.get_all_possible_moves(color)
        hashed = hash_board(board.board)
            
        if (not moves or is_win != 0):
            node = self.prev_node
            self.make_terminal(node)
            node.wins = int(is_win == color)
            return node

        move = self.random_move(moves)
        board.make_move(move, color)
        hashed = hash_board(board.board)

        if self.move is None: # capture our ititial move
            self.move = move

        if (hashed in self.visited):
            i = 0
            while hashed in self.stack and i < 10:
                board.undo()
                move = self.random_move(moves)
                board.make_move(move, color)
                hashed = hash_board(board.board)
                i += 1

            if hashed in self.stack and i == 10:
                board.undo()
                node = self.prev_node
                self.make_terminal(node)
                return node

        if (hashed not in self.visited):
            self.visited[hashed] = MCTSNode(color=color, move=move)

        self.visited[hashed].parent = self.stack[-1] 
        self.prev_node = MCTSNode(color=color, move=move)
        self.stack.append(hashed)
        return None

    def simulation(self):
        copy_board = copy.deepcopy(self.board)
      
        for _ in range(30):
            res = self.simulate_turn(copy_board, self.color)
            if res is not None:
                self.leaves += 1
                return res
            
            res = self.simulate_turn(copy_board, self.opponent[self.color])
            if res is not None:
                self.leaves += 1
                return res 

        node = self.visited[self.stack[-1]]
        self.make_terminal(node)
        
        if (winning(self.color, copy_board.board)):
            if node.color != self.color:
                node.wins = 0
        else:
            if node.color == self.color:
                node.wins = 0
        return node 

    def backpropagation(self, starting_board):
        def add_child(nh, ch):
            node = self.visited[nh]        
            if node.limited:
                node.terminal = False
            node.children.add(ch)

            node.visits = 0
            node.wins = 0
            wins = 0
            for c in node.children:
                child_node = self.visited[c]
                node.visits += child_node.visits
                wins += child_node.wins
            node.wins = node.visits - wins

        while self.stack:
            # if self.stack[-1] != starting_board:
            #     self.board.undo()
            top = self.stack.pop()
            
            if self.stack:
                add_child(self.stack[-1], top)

    def get_move(self, move: Move) -> Move:
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1

        moves = self.board.get_all_possible_moves(self.color)
        temp = hash_board(self.board.board)
        root = MCTSNode(color=self.color, move=None)
        max_move = self.random_move(moves)

        if has_only_one_item(moves):
            max_move = moves[0][0]
        else:
            if temp not in self.visited:
                self.visited[temp] = root
            self.prev_node = root
            board_moves = {}
            for row in moves:
                for move in row:
                    board_moves[str(move)] = MCTSNode(color=self.color, move=move)
            
            start_time = time.time()
            for _ in range(self.iterations):
                if time.time() - start_time > 5:
                    break
                self.move = None
                self.stack = [temp]
                res = self.simulation()
                # print(f"Color: {res.color} | wins: {res.wins} | Limited: {res.limited} ")

                # "backpropogation"
                node = board_moves[str(self.move)]
                node.visits += 1

                if res.color == self.color:
                    node.wins += res.wins

            max_uct = float("-inf")
            for move in board_moves:
                node = board_moves[move]
                uct = node.uct(self.iterations)
                if uct > max_uct:
                    max_uct = uct
                    max_move = node.move
            """
            print()
            print(f"Playing as {self.color}")
            explored, wins = 0, 0
            for c in board_moves:
                if board_moves[c].visits > 0:
                    node = board_moves[c]
                    print(f"{c} {node.uct(500)}, Wins: {node.wins} | Visits: {node.visits}")
                    if node.visits > 0:
                        explored += node.visits
                    wins += node.wins
            print(f"Explored: {explored} | Wins: {wins}") 
            print(self.board.get_all_possible_moves(self.color))
                self.backpropagation(temp)
            
            print(f"Time: {time.time() - start_time} | Iterations: {self.leaves} | limit_reached: {self.limit_reached}")
            print(f"White: {self.limit_white} | Black: {self.limit_black}")
            max_uct = -1
            for c in root.children:
                node = self.visited[c]
                uct = node.uct(self.iterations)
                if uct > max_uct:  
                    max_move = node.move
                    max_uct =  uct
            
        print(f"Playing as {self.color}")
        print(f"original board {temp} Same? {temp == hash_board(self.board.board)}")
        print(f"Root Wins: {self.win_count} {root.wins} | Visits: {root.visits}")
        print(f"Cycles: {self.cycles}, Leaves: {self.leaves}")
        for c in root.children:
            node = self.visited[c]
            print(f" Wins: {node.wins} | Visits: {node.visits}")
        
        repeats = 0
        for n1 in self.visited:
            inst = 0
            for n2 in self.visited:
                if n1 in self.visited[n2].children:
                    inst += 1
            if inst > 1:
                repeats += 1
        print(f"Repeats: {repeats}")
        """
        self.board.make_move(max_move,self.color)
        return max_move