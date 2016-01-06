#!/usr/bin/python

from enum import Enum
from copy import copy
import random

class InvalidMoveException(Exception):
    pass

class SquareState(Enum):
    _ = 0
    empty = 0  # Alias of _
    X = 1
    x = 1  # alias of X
    O = 2
    o = 2  # alias of O

    def __str__(self):
        return self.name

class Square(object):
    child = None
    state = SquareState['empty']

    def __eq__(self, other):
        if isinstance(other, SquareState):
            return self.state == other
        else:
            return self.state == other.state

    def __str__(self):
        return self.state.name

class Board(object):
    parent = None # this is currently unused
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
        # It would probably be better to use a 2D array, but ¯\_(ツ)_/¯
        # This was a deliberate decision, to make winner() easier to read
        if parent is not None:
            self.parent = parent

    def __iter__(self):
        return copy(self)

    def __next__(self):
        i = self._index
        self._index = self._index + 1
        if i < 9:
            return self.square(i // 3, i % 3)
        else:
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
        """Returns the square at the relevant row, col"""
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
    def square_name(row_or_tuple, col=None):
        """Returns a human readable name of the square at row, col"""

        if col is None:
            # Then row_or_tuple should be a tuple, extract row and col from there
            try:
                row = row_or_tuple[0]
                col = row_or_tuple[1]
            except TypeError:
                raise ValueError("Row and column are both required")
        else:
            # row_or_tuple is the row
            row = row_or_tuple

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

    def winner(self):
        """Returns the winner of this board (a SquareState value, which will
        be SquareState.empty if the board is a draw) or None if the board is
        not yet finalized."""
        
        # Use the cached value rather than checking again
        if self._winner is not None:
            return self._winner

        # It is possible for multiple wins to exist (for example: last move is X
        # to tl when X is already in tc, tr, ml, bl), in which case the winning_line
        # will be whatever gets set last in this cascade. This doesn't *really*
        # matter but it is arbitrary and therefore not elegant.

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

        if self._winner is None:
            # Nobody has won, but the board might be full. Start from that assumption
            # and reset _winner to None if we find an empty square.
            self._winner = SquareState['empty']
            for square in self:
                if square == SquareState.empty:
                    # There is at least one empty square, so board is still active
                    self._winner = None
                    break

        return self._winner

    # This __str__ is super ick but is kind of useful in debugging
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
    
    # child_win and overall_win are flags that should be reset after they are read
    child_win = None # if not None, a tuple (child_board, winning_player)
    overall_win = None # if not None, the winning_player

    def __init__(self, starting_player=None):
        self.main_board = Board()

        for i in range(3):
            for j in range(3):
                self.main_board[(i, j)].child = Board(self.main_board)

        if starting_player is None:
            if random.choice('xo') == 'x':
                self.active_player = SquareState['X']
            else:
                self.active_player = SquareState['O']
        else:
            try:
                if starting_player.lower() in ('x', 'o'):
                    starting_player = SquareState[starting_player]
            except:
                if starting_player != SquareState.X and starting_player != SquareState.O:
                    raise ValueError("The starting_player must be SquareState.X or SquareState.O")
            self.active_player = starting_player

        self.log_status("{} to play".format(self.active_player.name))

        # All boards start active
        self.active_boards = [(i, j) for i in range(3) for j in range(3)]

    def add_log_function(self, fun):
        self._log_functions.append(fun)

    def log_status(self, status):
        print(status)
        for f in self._log_functions:
            f(status)

    def play(self, child_board, square):
        """Progress state by having self.active_player play on square in child_board.
        Each of child_board and square to be specified as (row, col) tuples."""
        
        if (self.main_board[child_board].child.winner() is not None) or (self.main_board[child_board].child[square] != SquareState.empty) or (child_board not in self.available_boards()):
            # Can't play if child_board has been won
            # Can't play if the square is occupied
            # Can't play except in accordance with the available_boards() rule
            raise InvalidMoveException

        self.main_board[child_board].child[square].state = self.active_player # Record the play

        self.log_status("{} played in the {} square of the {} board".format(
            self.active_player.name,
            Board.square_name(square),
            Board.square_name(child_board)
            ))
        
        # Check to see if this move resulted in child_board being won
        board_winner = self.main_board[child_board].child.winner()
        if board_winner is not None:
            self.main_board[child_board].state = self.active_player
            self.log_status("{} won the {} board with a line from {} to {}".format(
                self.active_player,
                Board.square_name(child_board),
                Board.square_name(self.main_board[child_board].child.winning_line[0]),
                Board.square_name(self.main_board[child_board].child.winning_line[1])
                ))
            self.active_boards.remove(child_board)
            self.child_win = (child_board, self.active_player)
        
        # Check to see if this move finished the game
        board_winner = self.main_board.winner()
        if board_winner is not None:
            self.log_status("{} won the game overall with a line from {} to {}".format(
                self.active_player,
                Board.square_name(self.main_board.winning_line[0]),
                Board.square_name(self.main_board.winning_line[1])
                ))
            self.overall_win = self.active_player

        self.last_move = (square[0], square[1]) # needed for available_boards()
        
        if self.active_player == SquareState.X:
            self.active_player = SquareState['O']
            #self.log_status("{} to play".format(self.active_player))
        elif self.active_player == SquareState.O:
            self.active_player = SquareState['X']
            #self.log_status("{} to play".format(self.active_player))

    def available_boards(self):
        """Returns child boards which are available for this move, based on the following rules:
        1. if it's the first move, you can play anywhere
        2. the child board available for play is that board which is in the same position on the
           main board as the last move was on its child board, subject to (3)
        3. if the child board in accordance with (2) is unplayable (being full or already won)
           then you can play anywhere
        4. you can never play on a board that is full or which has been already won"""
        
        if self.last_move is not None and self.main_board[self.last_move].child.winner() is None:
            return [self.last_move]

        for b in self.active_boards:
            if self.main_board[b].child.winner() is not None:
                self.active_boards.remove(b)
        return self.active_boards
