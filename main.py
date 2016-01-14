#!/usr/bin/python

import tkinter
import random
import uuid
from tkinter import N, S, E, W, ttk, messagebox

import game
import menu
import info_frame
from gameboard import CanvasHelper
from tkutils import ResizingCanvas, set_aspect

class MainWindow(ttk.Frame):

    def gameboard_onclick(self, e):
        """The callback for clicks on the gameboard.
        Calls Game.play() at the appropriate place, and returns feedback to
        the user."""
        try:
            (row, col) = CanvasHelper.get_square(self.gameboard, e.x, e.y)
            (outer_row, outer_col, inner_row, inner_col) = (row // 3, col // 3, row % 3, col % 3)
            self.game.play((outer_row, outer_col), (inner_row, inner_col))
            # self.set_status("Played at ({}, {}), ({}, {})".format(outer_row, outer_col, inner_row, inner_col))

            # That self.game.play(...) has changed self.game.active_player so
            # this is backwards
            if self.game.active_player == game.SquareState.X:
                CanvasHelper.draw_o(self.gameboard, row, col)
            else:
                CanvasHelper.draw_x(self.gameboard, row, col)

            if self.game.child_win is not None:
                self.game_onchildwin(self.game.child_win[0], self.game.child_win[1])
                self.game.child_win = None

            if self.game.overall_win is not None:
                CanvasHelper.higlight_available_boards(self.gameboard, ())
            else:
                CanvasHelper.higlight_available_boards(self.gameboard, self.game.available_boards())

        except game.InvalidMoveException:
            # self.set_status("({}, {}), ({}, {}) is an invalid move".format(outer_row, outer_col, inner_row, inner_col))
            pass

        except CanvasHelper.OnGridException:
            pass

    def game_onchildwin(self, board, player):
        """Called when a child board is won"""

        # Draw a line through the winning location
        winning_line = self.game.main_board[board].child.winning_line
        start_delta = CanvasHelper.get_midpoint(self.gameboard, winning_line[0][0], winning_line[0][1])
        end_delta = CanvasHelper.get_midpoint(self.gameboard, winning_line[1][0], winning_line[1][1])
        start_point = CanvasHelper.get_bbox(self.gameboard, board[0], board[1], 3, 3)
        line = (
                start_point[0] + start_delta[0],
                start_point[1] + start_delta[1],
                start_point[0] + end_delta[0],
                start_point[1] + end_delta[1])
        extension = (
                1.1 * (line[2] - line[0]) / 8,
                1.1 * (line[3] - line[1]) / 8)
        self.gameboard.create_line(
            line[0] - extension[0],
            line[1] - extension[1],
            line[2] + extension[0],
            line[3] + extension[1],
            fill="black",
            width=5,
            capstyle=tkinter.ROUND,
            tag=("resize",))

        # Draw a big X or O over the square they won
        if player == game.SquareState.X:
            CanvasHelper.draw_x(self.gameboard, board[0], board[1], 3, 3, 10, 0.75)
        else:
            CanvasHelper.draw_o(self.gameboard, board[0], board[1], 3, 3, 10, 0.75)


    def set_status(self, t):
        self.infoframe.status.config(text=t)

    # def start_game(self):
    #     if "" == self.infoframe.X_name.get().strip():
    #         self.infoframe.X_name.set("X")
    #     if "" == self.infoframe.O_name.get().strip():
    #         self.infoframe.O_name.set("O")
    #     self.infoframe.X_entry.config(state=tkinter.DISABLED)
    #     self.infoframe.O_entry.config(state=tkinter.DISABLED)
    #     self.set_status("{} to play".format(self.game.active_player.name))

    def __init__(self, parent, game, *args, **kwargs):
        ttk.Frame.__init__(self, parent, padding=20, *args, **kwargs)
        self.parent = parent
        self.game = game

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        self.infoframe = info_frame.InfoFrame(self, game, start_game=None) #self.start_game)
        self.infoframe.grid(column=0, row=1, sticky=(N, W, E, S))

        # We set up an auto-resizing, fixed-aspect-ratio frame which will
        # contain our gameboard canvas
        padframe = ttk.Frame(self, padding=0)
        padframe.grid(column=0, row=0, sticky=(N, W, E, S))
        gameframe = ttk.Frame(padframe, padding=0)
        gameframe.grid(column=0, row=0, sticky=(N, S, W, E))
        gameframe.columnconfigure(0, weight=1)
        gameframe.rowconfigure(0, weight=1)
        set_aspect(gameframe, padframe, 1)

        # We set up an auto-resizing canvas for the gameboard
        self.gameboard = ResizingCanvas(gameframe, bg="white")
        self.gameboard.grid(column=0, row=0, sticky=(N, S, E, W))

        # We need to update the root window to make sure we have the right
        # dimensions before we can draw the grids
        self.parent.update()
        CanvasHelper.draw_grid(self.gameboard, colour="#999", thickness=1, rows=9, cols=9, tags=("minor-grid",))
        CanvasHelper.draw_grid(self.gameboard, tags=("major-grid",))

        # Create the click binding for the gameboard
        self.gameboard.bind("<Button-1>", self.gameboard_onclick)

        # Highlight all available boards
        CanvasHelper.higlight_available_boards(self.gameboard, self.game.available_boards())

        # Display status
        def log_func(status):
            self.set_status(status)
        self.game.add_log_function(log_func)

        # Set status
        self.set_status("{} to play".format(self.game.active_player.name))

if __name__ == "__main__":
    root = tkinter.Tk()
    root.title("Ultimate XO")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    g = game.Game()

    main_window = MainWindow(root, g)
    main_window.grid(column=0, row=0, sticky=(N, W, E, S))
    root.config(menu=menu.MainMenu(root, g, main_window))

    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    root.mainloop()
