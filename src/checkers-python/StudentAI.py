import random
from BoardClasses import Move
from BoardClasses import Board
import math
import copy
import hashlib
import time

#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
def hash_board(board):
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

def valid_move(moves, max_move):
    for row in moves:
        for move in row:
            if str(move) == str(max_move):
                return True
    return False

def has_only_one_item(matrix):
    count = 0
    for row in matrix:
        count += len(row)
        if count > 1:
            return False
    return count == 1

def winning(color, board):
    white_count = 0
    black_count = 0
    for row in board:
        for checker in row:
            if checker.color == "W":
                white_count += 1
            elif checker.color == "B":
                black_count += 1
    if color == 1:
        return white_count < black_count
    else:
        return black_count < white_count
        
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

    def uct(self,  num_parent_simulations, exploration_weight=1.0):
        if self.visits == 0:
            return float('inf')
        return (self.wins/ self.visits) + exploration_weight * (math.sqrt(math.log(num_parent_simulations) / self.visits))

class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
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

    def make_terminal(self, node):
        self.terminal_nodes += 1
        node.terminal = True
        node.wins = 1
        node.visits = 1
        pass


    def valid_move(self, moves, move):
        for row in moves:
            for m in row:
                if m == move:
                    return True
        return False

    def random_move(self, moves):
        if not moves: 
            return None
        index = random.randint(0, len(moves) - 1)
        inner_index = random.randint(0, len(moves[index]) - 1)
        return moves[index][inner_index]

    def simulate_turn(self, board, color):
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

        return 0

    def backprop(self, visited, stack):
        '''
        The idea here is to store the nodes into a stack, once you find a win/loss you start to pop from the stack.
        To build the tree (Could be recursive but I'm lazy)

        parent.simulations = sum(children.simulations)
        parent.wins = sum(children.wins) - parent.simulations
        '''
        curr = None 
        while stack:
            h_top = stack.pop()
            node = visited[h_top]

            # if (self.board.saved_move and hash_board(self.board.board) != original_board):
            #     self.board.undo()
            top = self.stack.pop()
            
            if self.stack:
                add_child(self.stack[-1], top)

    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1

        moves = self.board.get_all_possible_moves(self.color)

        start_time = time.time()
        iterations = 0

        if (len(moves) > 1):
            while time.time() - start_time < 5 and iterations < 1000:
                if time.time() - start_time >= 5:
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

            # print()
            # print(f"Playing as {self.color}")
            # explored, wins = 0, 0
            # for c in board_moves:
            #     if board_moves[c].visits > 0:
            #         node = board_moves[c]
            #         print(f"{c} {node.uct(500)}, Wins: {node.wins} | Visits: {node.visits}")
            #         if node.visits > 0:
            #             explored += node.visits
            #         wins += node.wins
            # print(f"Explored: {explored} | Wins: {wins}") 
            # print(self.board.get_all_possible_moves(self.color))
                # self.backpropagation(temp)
            
            # print(f"Time: {time.time() - start_time} | Iterations: {self.leaves} | limit_reached: {self.limit_reached}")
            # print(f"White: {self.limit_white} | Black: {self.limit_black}")
            # max_uct = -1
            # for c in root.children:
            #     node = self.visited[c]
            #     uct = node.uct(self.iterations)
            #     if uct > max_uct:  
            #         max_move = node.move
            #         max_uct =  uct

        # print(f"Playing as {self.color}")
        # print(f"original board {temp} Same? {temp == hash_board(self.board.board)}")
        # print(f"Root Wins: {self.win_count} {root.wins} | Visits: {root.visits}")
        # print(f"Cycles: {self.cycles}, Leaves: {self.leaves}")
        # for c in root.children:
        #     node = self.visited[c]
        #     print(f" Wins: {node.wins} | Visits: {node.visits}")
        
#         repeats = 0
#         for n1 in self.visited:
#             inst = 0
#             for n2 in self.visited:
#                 if n1 in self.visited[n2].children:
#                     inst += 1
#             if inst > 1:
#                 repeats += 1
#         print(f"Repeats: {repeats}")
# 
        self.board.make_move(max_move,self.color)
        return max_move

    