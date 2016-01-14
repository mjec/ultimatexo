#!/usr/bin/python

import game
import tkinter
from tkinter import N, S, E, W, ttk, messagebox

class MainMenu(tkinter.Menu):

    def __init__(self, root, game, main_window, *args, **kwargs):
        tkinter.Menu.__init__(self, root, *args, **kwargs)
        self.root = root
        self.game = game
        self.main_window = main_window

        gamemenu = tkinter.Menu(self, tearoff=0)
        gamemenu.add_command(
            label="New game",
            command=self.new_game,
            underline=0,
            accelerator="Ctrl+N")
        root.bind_all("<Control-n>", self.new_game)

        # gamemenu.add_command(
        #     label="Undo",
        #     command=self.undo,
        #     underline=0,
        #     accelerator="Ctrl+Z")
        # root.bind_all("<Control-z>", self.undo)

        gamemenu.add_separator()
        gamemenu.add_command(label="Exit", command=self.exit, underline=1)

        helpmenu = tkinter.Menu(self, tearoff=0)
        helpmenu.add_command(label="About", command=self.about, underline=0)

        self.add_cascade(label="Game", menu=gamemenu, underline=0)
        self.add_cascade(label="Help", menu=helpmenu, underline=0)

    def new_game(self, e=None):
        confirm = messagebox.askquestion(
            "New game",
            "Are you sure you want to start a new game?",
            icon="warning")
        if "yes" == confirm:
            self.main_window.clear_board()
            g = game.Game()
            self.main_window.game = g
            self.game = g

    def undo(self, e=None):
        print("Undo: {}".format(e))
        pass

    def exit(self, e=None):
        confirm = messagebox.askquestion(
            "Quit",
            "Are you sure you want to quit?",
            icon="warning")
        if "yes" == confirm:
            exit(0)

    def about(self, e=None):
        confirm = messagebox.showinfo(
            "About",
            "An ultimate noughts and crosses game by Michael Cordover. Version 1.0 (January 2016). MIT licence. In honour of Ben, who taught me the game.",)
