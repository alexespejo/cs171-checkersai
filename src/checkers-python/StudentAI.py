import random
import copy
import math
from BoardClasses import Move
from BoardClasses import Board
import time
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

def hash_board(board):
    board_tuple = tuple(
        tuple(
            (piece.color, piece.is_king) if piece else None  # Convert Checkers to immutable tuples
            for piece in row
        )
        for row in board
    )
    return hash(board_tuple)

# 0: white, 1: black
class MCTSNode:
    def __init__(self, game_state, color, parent=None,  move=None):
        # self.game_state = copy.deepcopy(game_state)
        self.game_state =  None
        self.color = color
        self.parent = parent
        self.move = move
        self.children = set() 
        self.visit_count = 0
        self.win_count = 0
        self.uct_value = float('inf')
        self.terminal = False
        self.simulated_outcome = None

    def uct(self,  num_parent_simulations, exploration_weight=1.0):
        if self.visit_count == 0:
            return float('inf')
        return (self.win_count / self.visit_count) + exploration_weight * (math.sqrt(math.log(num_parent_simulations) / self.visit_count))

    # This is used in the backpropogation step to handle the children and update the visit and win count
    def add_child(self, child_hash, visited):
        self.children.add(child_hash)

        if (not self.terminal):
            # if it's not terminal, compute the win and visits
            self.win_count = 0
            self.visit_count = 0
            child_wins = 0
            for child in self.children:
                # if (len(self.children) > 1): ### Detects if multiple children exist in a branch (happens when dupes are found)
                #     visited[child].game_state.show_board()
                self.visit_count += visited[child].visit_count
                child_wins += visited[child].win_count
                
            self.win_count = self.visit_count - child_wins
            # print(self.visit_count, end=" ") 

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
        self.cycle_set = set()
        self.limit_count = 0

    def random_move(self, moves):
        if not moves: 
            return None
        index = random.randint(0, len(moves) - 1)
        inner_index = random.randint(0, len(moves[index]) - 1)
        return moves[index][inner_index]

    def simulate_turn(self, copy_board, color, visited, stack):
        """Simulate a turn for a given player (AI or opponent)."""
        moves = copy_board.get_all_possible_moves(color)

        if not moves: 
            res = copy_board.is_win("W" if color == 2 else "B")
            # if res == 0:
                # return None

            leaf = visited[stack[-1]]
            leaf.terminal = True
            leaf.win_count = 1
            leaf.visit_count = 1
            return res

        move = self.random_move(moves)
        copy_board.make_move(move, color)
        board_hash = hash_board(copy_board.board)

        while len(moves) > 1 and board_hash in stack:
            copy_board.undo()
            move = self.random_move(moves)
            copy_board.make_move(move, color)
            board_hash = hash_board(copy_board.board)

        if (len(moves) == 1 and board_hash in stack) or len(stack) >= 50:
            ## This is how you end the simulation step
            # print('no more moves ')
            if len(stack)// 2 == 30:
                self.limit_count += 1
            leaf = visited[stack[-1]]
            leaf.terminal = True
            leaf.win_count = 0
            leaf.visit_count = 1
            return -1 

        if board_hash not in visited:
            ### Preserve the node to save space 
            visited[board_hash] =  MCTSNode(copy_board, color)
            visited[board_hash].move = move 

        # self.cycle_set.add(board_hash)
        stack.append(board_hash)
        return None

    def simulate(self, visited, stack, move=None):
        '''
        One call to this function performs one exploration and should return either a win/loss/tie
        This will randomly go down every node till it stops and then we'll call backprop to add the branch to the tree
        '''
        copy_board = copy.deepcopy(self.board) 
        if move is not None:
            copy_board.make_move(move, self.color)
        for _ in range(100):
            res = self.simulate_turn(copy_board, self.color, visited, stack)
            if res is not None:
                return res

            res = self.simulate_turn(copy_board,self.opponent[self.color], visited, stack)
            if res is not None:
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
            if stack:
                curr = visited[stack[-1]]
                curr.add_child(h_top, visited)
            else:
                curr = node
        return curr

    def get_move(self, move):
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1

        hash_start = hash_board(self.board.board)
        root = MCTSNode(self.board, self.color)
        visited = {hash_start: root}

        start_time = time.time()
        iterations = 0

        while time.time() - start_time < 25 and iterations < 600:
            if time.time() - start_time >= 25:
                break
            stack = [hash_start]
            self.simulate(visited, stack)
            self.backprop(visited, stack)
            iterations += 1
            
        max_uct = -1
        max_move = None
        for c in root.children:
            node = visited[c]
            if node.uct(root.visit_count) > max_uct:
                max_move = node.move
                max_uct = node.uct(root.visit_count)

        self.board.make_move(max_move, self.color)

        return max_move