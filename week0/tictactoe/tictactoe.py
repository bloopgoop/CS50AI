"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    if board == initial_state():
        return X
    
    x_count = 0
    o_count = 0
    for row in board:
        for char in row:
            if char == X:
                x_count += 1
            if char == O:
                o_count += 1
    
    if x_count > o_count:
        return O
    else:
        return X



def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible_actions.add((i,j))
    
    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    result = copy.deepcopy(board)
    result[action[0]][action[1]] = player(result)
    return result
    


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(3):
        # 3 in a column
        if board[0][i] == X and board[1][i] == X and board[2][i] == X:
            return X
        if board[0][i] == O and board[1][i] == O and board[2][i] == O:
            return O
        
        # 3 in a row
        if board[i][0] == X and board[i][1] == X and board[i][2] == X:
            return X
        if board[i][0] == O and board[i][1] == O and board[i][2] == O:
            return O

    # Diagonals
    if board[0][0] == X and board[1][1] == X and board[2][2] == X:
        return X
    if board[0][2] == X and board[1][1] == X and board[2][0] == X:
        return X
    if board[0][0] == O and board[1][1] == O and board[2][2] == O:
        return O
    if board[0][2] == O and board[1][1] == O and board[2][0] == O:
        return O
    
    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board):
        return True
    
    # Check whether the board is full
    for row in board:
        for char in row:
            if char == EMPTY:
                return False

    return True



def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == None:
        return 0
    else:
        return -1


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    moves = []
    if player(board) == O:
        for action in actions(board):
            moves.append((max_value(result(board, action)), action))
        return sorted(moves, key=lambda x: x[0])[0][1]
        
    else:
        for action in actions(board):
            moves.append((min_value(result(board, action)), action))
        return sorted(moves, key=lambda x: x[0], reverse=True)[0][1]


def max_value(board):
    """
    Returns the greatest score out of all possible moves
    """
    if terminal(board):
        return utility(board)
    
    v = -math.inf
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v


def min_value(board):
    """
    Returns the lowest score out of all possible moves value
    """ 
    if terminal(board):
        return utility(board)

    v = math.inf
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v