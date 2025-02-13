import random
import copy
import math
from BoardClasses import Move
from BoardClasses import Board
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

def are_boards_equal(board1, board2):
    if len(board1) != len(board2) or len(board1[0]) != len(board2[0]):
        return False  # Boards must be the same dimensions

    for i in range(len(board1)):
        for j in range(len(board1[0])):
            piece1, piece2 = board1[i][j], board2[i][j]

            # Both must be either Checker objects or None
            if (piece1 is None) != (piece2 is None):
                return False

            # If both are Checkers, compare attributes
            if piece1 and piece2:
                if (piece1.color != piece2.color or
                        piece1.row != piece2.row or
                        piece1.col != piece2.col or
                        piece1.is_king != piece2.is_king):
                    return False

    return True

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
        self.game_state = game_state
        self.color = color
        self.parent = parent
        self.move = move
        self.children = []
        self.visit_count = 0
        self.win_count = 0
        self.uct_value = float('inf')
        self.terminal = False
        self.simulated_outcome = None

    def uct(self,  num_parent_simulations, exploration_weight=1.0):
        if self.visit_count == 0:
            return float('inf')
        return (self.win_count / self.visit_count) + exploration_weight * (math.sqrt(math.log(num_parent_simulations) / self.visit_count))

    def add_child(self, child_node):
        self.children.append(child_node)

        if (child_node.terminal):
            # if it's terminal it's visit count will be 0
            self.visit_count += 1
        else:
            # if it's not terminal, compute the win and visits
            self.win_count = 0
            child_wins = 0
            for child in self.children:
                self.visit_count += child.visit_count
                child_wins += child.win_count
            self.win_count = self.visit_count - child_wins

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

    # Example moves
    # [[(1,1)-(2,0), (1,1)-(2,2)], [(1,3)-(2,2), (1,3)-(2,4)], [(1,5)-(2,4), (1,5)-(2,6)]]

    def random_move(self, moves):
        if not moves:  # Check if moves is empty
            return None
        index = random.randint(0, len(moves) - 1)
        inner_index = random.randint(0, len(moves[index]) - 1)
        return moves[index][inner_index]

    def simulate_turn(self, copy_board, color, visited, stack):
        """Simulate a turn for a given player (AI or opponent)."""
        moves = copy_board.get_all_possible_moves(color)

        if not moves: # when a player is out of moves determine if it's a win/loss/tie
            res = copy_board.is_win("W" if color == 2 else "B")
            if res == 0:
                return None
            leaf = stack[-1]
            leaf.terminal = True
            leaf.win_count = 1
            leaf.visit_count = 1
            return res

        move = self.random_move(moves)
        copy_board.make_move(move, color)

        # keep track of each board state to handle different paths that might occur from that state
        if hash_board(copy_board.board) not in visited:
            # I need to preserve the state somewhere so I can access it on repeated instances
           visited[hash_board(copy_board.board)] =  MCTSNode(copy_board, color)
        node = MCTSNode(copy_board, color)
        stack.append(node)
        return None

    def simulate(self,  visited, stack, move=None):
        '''
        One call to this function performs one exploration and should return either a win/loss/tie
        This will randomly go down every node till it stops and then we'll call backprop to add the branch to the tree
        '''
        copy_board = copy.deepcopy(self.board)
        # copy_board.make_move(move, self.color)
        for i in range(100):
            # NOTE, the color of the player might be important here
            if self.color == 2:
                res = self.simulate_turn(copy_board,1, visited, stack)
                if res is not None:
                    return res

                res = self.simulate_turn(copy_board, self.color, visited, stack)
                if res is not None:
                    return res

            else:
                res = self.simulate_turn(copy_board, self.color, visited, stack)
                if res is not None:
                    return res

                res = self.simulate_turn(copy_board, 2, visited, stack)
                if res is not None:
                    return res

        return 0

    def backprop(self, root, visited, stack):
        '''
        The idea here is to store the nodes into a stack, once you find a win/loss you start to pop from the stack.
        To build the tree (Could be recursive but I'm lazy)

        parent.simulations = sum(children.simulations)
        parent.wins = sum(children.wins) - parent.simulations
        '''

        curr = None # we back propogate when we hit a terminal node
        while stack:
            node = stack.pop()
            if stack:
                curr = stack[-1]
                curr.add_child(node)
                # if (node.terminal):
                #     # if it's terminal it's visit count will be 0
                #     curr.visit_count += 1
                # else:
                #     # if it's not terminal, compute the win and visits
                #     curr.win_count = 0
                #     child_wins = 0
                #     for child in curr.children:
                #         curr.visit_count += child.visit_count
                #         child_wins += child.win_count
                #     curr.win_count = curr.visit_count - child_wins
            else:
                curr = node
        return curr

    def get_move(self, move):
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1

        visited = {}
        root = MCTSNode(self.board, self.color)
        stack = [root]

        moves = self.board.get_all_possible_moves(self.color)
        res = self.simulate(visited, stack, m)  # 1 simulation

        # dfs stuff
        # res = 1
        # found_result = False
        # move = None
        # for _ in range(100):
        #     for move_list in moves:
        #         for m in move_list:
        #             res = self.simulate(visited, stack, m)  # 1 simulation
        #             if res != 1:
        #                 move = m
        #                 found_result = True
        #                 break  # Break inner loop
        #         if found_result:
        #             break  # Break outer loop
        # if move is None:
        #     move = self.random_move(moves)
        self.board.make_move(move, self.color)
        return move