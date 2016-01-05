#!/usr/bin/python

from enum import Enum
from copy import deepcopy as copy
import random

class InvalidMoveException(Exception):
    pass

class SquareState(Enum):
    _ = 0  # Alias for empty
    empty = 0
    X = 1
    x = 1  # alias of X
    O = 2
    o = 2  # alias of O

class Square(object):
    child = None
    state = SquareState['empty']
    
    def __eq__(self, other):
        if isinstance(other, SquareState):
            return self.state.value == other.value
        else:
            return self.state.value == other.state.value

    def __str__(self):
        return self.state.name
    
class Board(object):
    parent = None
    _index = 0
    _winner = None
    winning_line = None

    def __init__(self, parent=None):
        self.tl = Square()  # Top left
        self.tc = Square()  # Top center
        self.tr = Square()  # Top right
        self.ml = Square()  # Middle left
        self.mc = Square()  # Middle centre
        self.mr = Square()  # Middle right
        self.bl = Square()  # Bottom left
        self.bc = Square()  # Bottom centre
        self.br = Square()  # Bottom right
        if not parent is None:
            self.parent = parent

    def __iter__(self):
        return copy(self)

    def __next__(self):
        i = self._index
        self._index = self._index + 1
        if i < 9:
            return self.square(i // 3, i % 3)
        else:
            self._index = 0
            raise StopIteration

    def __getitem__(self, key):
        try:
            return self.square(key[0], key[1])
        except:
            raise KeyError

    def __setitem__(self, key, value):
        try:
            item = self.square(key[0], key[1])
        except:
            raise KeyError
        if not isinstance(value, Square):
            raise ValueError("The value must be an instance of Square")
        item = value

    def __delitem__(self, key):
        try:
            item = self.square(key[0], key[1])
        except:
            raise KeyError
        item.state = SquareState.empty
        # Note that we do NOT set item.child = None

    def square(self, row, col):
        if 0 == row:
            if 0 == col:
                return self.tl
            elif 1 == col:
                return self.tc
            elif 2 == col:
                return self.tr
        elif 1 == row:
            if 0 == col:
                return self.ml
            elif 1 == col:
                return self.mc
            elif 2 == col:
                return self.mr
        elif 2 == row:
            if 0 == col:
                return self.bl
            elif 1 == col:
                return self.bc
            elif 2 == col:
                return self.br
        raise TypeError(
            "No such (row, column) pair: each must be in range 0-2 inclusive")
    
    @staticmethod
    def square_name(row, col):
        if 0 == row:
            if 0 == col:
                return "top left"
            elif 1 == col:
                return "top centre"
            elif 2 == col:
                return "top right"
        elif 1 == row:
            if 0 == col:
                return "middle left"
            elif 1 == col:
                return "middle centre"
            elif 2 == col:
                return "middle right"
        elif 2 == row:
            if 0 == col:
                return "bottom left"
            elif 1 == col:
                return "bottom centre"
            elif 2 == col:
                return "bottom right"
        raise TypeError(
            "No such (row, column) pair: each must be in range 0-2 inclusive")
        
    @property
    def winner(self):
        """Returns the winner of this board (a SquareState value, which will
        be SquareState.empty if the board is a draw) or None if the board is
        not yet finalized."""
        if not (self._winner is None):
            return self._winner
        if self.tl != SquareState.empty:
            if self.tl == self.tc == self.tr:
                self.winning_line = ((0,0), (0,2))
                self._winner = self.tl.state
            if self.tl == self.ml == self.bl:
                self.winning_line = ((0,0), (2,0))
                self._winner = self.tl.state
        if self.br != SquareState.empty:
            if self.br == self.bc == self.bl:
                self.winning_line = ((2,0), (2,2))
                self._winner = self.br.state
            if self.br == self.mr == self.tr:
                self.winning_line = ((0,2), (2,2))
                self._winner = self.br.state
        if self.mc != SquareState.empty:
            if self.mc == self.tl == self.br:
                self.winning_line = ((0,0), (2,2))
                self._winner = self.mc.state
            if self.mc == self.bl == self.tr:
                self.winning_line = ((2,0), (0,2))
                self._winner = self.mc.state
            if self.mc == self.ml == self.mr:
                self.winning_line = ((1,0), (1,2))
                self._winner = self.mc.state
            if self.mc == self.tc == self.bc:
                self.winning_line = ((0,1), (2,1))
                self._winner = self.mc.state
        else:
            # Nobody has won, but we assume we can't play
            self._winner = SquareState['empty']
            for square in self:
                if square == SquareState.empty:
                    # There is at least one empty square, so board is still active
                    self._winner = None
                    break
        return self._winner

    def __str__(self):
        s = ""
        for c in self:
            s = "{}\n{}: ".format(s, c)
            if c.child:
                a = ""
                for k in c.child:
                    a = "{}{}".format(a, k)
            s = "{}{}".format(s, a)
        return s


class Game(object):
    last_move = None
    _log_functions = []
    _won_child_functions = []
    _won_overall_functions = []

    def __init__(self, starting_player=None):
        self.main_board = Board()
        for i in range(3):
            for j in range(3):
                self.main_board[(i,j)].child = Board(self.main_board)
        
        if starting_player is None:
            if random.choice('xo') == 'x':
                self.active_player = SquareState['X']
            else:
                self.active_player = SquareState['O']
        else:
            self.active_player = starting_player
        
        if (not isinstance(self.active_player, SquareState)) or (self.active_player != SquareState.X and self.active_player != SquareState.O):
            raise ValueError("The starting_player must be SquareState.X or SquareState.O")
        
        self.log_status("{} to play".format(self.active_player.name))
        
        self.active_boards = [(i, j) for i in range(3) for j in range(3)]
    
    def add_log_function(self, fun):
        self._log_functions.append(fun)
    
    def add_won_child_function(self, fun):
        self._won_child_functions.append(fun)
    
    def add_won_overall_function(self, fun):
        self._won_overall_functions.append(fun)
    
    def log_status(self, status):
        print(status)
        for f in self._log_functions:
            f(status)
    
    def _fire_won_child(self, board, player):
        for f in self._won_child_functions:
            f(board, player)
        
    def _fire_won_overall(self, player):
        for f in self._won_overall_functions:
            f(player)
    
    def play(self, child_board, square):
        if (not (self.main_board[child_board].child.winner is None)) or self.main_board[child_board].child[square] != SquareState.empty:
            raise InvalidMoveException
            return
        
        self.main_board[(child_board[0], child_board[1])].child[(square[0], square[1])].state = SquareState[self.active_player.name]
        
        self.log_status("{} played in the {} square of the {} board".format(
            self.active_player.name,
            Board.square_name(square[0], square[1]),
            Board.square_name(child_board[0], child_board[1])
            ))
        
        board_winner = self.main_board[child_board].child.winner
        if not board_winner is None:
            self.main_board[(child_board[0], child_board[1])].state = self.active_player
            self.log_status("{} won the {} board with a line from {} to {}".format(
                self.active_player,
                Board.square_name(child_board[0], child_board[1]),
                Board.square_name(self.main_board[(child_board[0], child_board[1])].child.winning_line[0][0], self.main_board[(child_board[0], child_board[1])].child.winning_line[0][1]),
                Board.square_name(self.main_board[(child_board[0], child_board[1])].child.winning_line[1][0], self.main_board[(child_board[0], child_board[1])].child.winning_line[1][1])
                ))
            self.active_boards.remove((child_board[0], child_board[1]))
            self._fire_won_child((child_board[0], child_board[1]), self.active_player)
        
        board_winner = self.main_board.winner
        if not board_winner is None:
            self.log_status("{} won the game overall with a line from {} to {}".format(
                self.active_player,
                Board.square_name(self.main_board.winning_line[0][0], self.main_board.winning_line[0][1]),
                Board.square_name(self.main_board.winning_line[1][0], self.main_board.winning_line[1][1])
                ))
            self._fire_won_overall(self.active_player)
        
        self.last_move = (square[0], square[1])
        if self.active_player == SquareState.X:
            self.active_player = SquareState['O']
            self.log_status("{} to play".format(self.active_player))
        elif self.active_player == SquareState.O:
            self.active_player = SquareState['X']
            self.log_status("{} to play".format(self.active_player))
    
    def available_boards(self):
        if not self.last_move is None:
            if self.main_board[self.last_move].child.winner is None:
                return [self.last_move]
        
        for b in self.active_boards:
            if not self.main_board[b].child.winner is None:
                del self.active_boards[b]
        
        return self.active_boards
