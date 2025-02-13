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

        self.visit_count = 0
        self.win_count = 0
        for child in self.children:
            # the win count is the inverse of it's children's wins
            self.win_count += (child.visit_count - child.win_count)
            self.visit_count += child.visit_count

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
        if not moves:
            res = copy_board.is_win("W" if color == 2 else "B")
            if res == 0:
                return None
            stack[-1].terminal = True
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

    def simulate(self, tree,  visited, stack):
        copy_board = copy.deepcopy(self.board)
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

        return None

    def backprop(self, root, visited, stack):
        curr = None
        while stack:
            node = stack.pop()
            if stack:
                curr = stack[-1]
                curr.add_child(node)
            else:
                node.add_child(curr)
                curr = node
        return curr

    def get_move(self, move):
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color])
        else:
            self.color = 1

        visited = {}
        stack = []
        root = MCTSNode(self.board, self.color)

        # win, loss = 0, 0
        # for _ in range(100):
        res = self.simulate(root, visited, stack) # 1 simulation
        #     if res == 1:
        #         loss += 1
        #     else:
        #         win += 1
        # print("win: ", win)
        # print("loss: ", loss)

        root.add_child(self.backprop(root, visited, stack))
        print(root.win_count)

        # remove
        moves = self.board.get_all_possible_moves(self.color)
        index = random.randint(0, len(moves) - 1)
        inner_index = random.randint(0, len(moves[index]) - 1)
        move = moves[index][inner_index]
        self.board.make_move(move, self.color)
        return move

    # def get_move(self,move):
    #     if len(move) != 0:
    #         self.board.make_move(move,self.opponent[self.color])
    #     else:
    #         self.color = 1
    #     root = MCTSNode(self.board)
    #     moves = self.board.get_all_possible_moves(self.color)
    #     index = randint(0,len(moves)-1)
    #     inner_index =  randint(0,len(moves[index])-1)
    #     move = moves[index][inner_index]
    #     self.board.make_move(move,self.color)
    #     return move
