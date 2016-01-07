#!/usr/bin/python

import tkinter
from tkinter import N, S, E, W, ttk, messagebox

class InfoFrame(tkinter.Frame):

    def __init__(self, parent, game, start_game, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(3, weight=0)

        ttk.Separator(
            self,
            orient=tkinter.HORIZONTAL).grid(
                column=1,
                columnspan=3,
                row=1, #2,
                pady=5,
                sticky=(N, S, E, W))

        self.status = ttk.Label(
            self,
            text="Starting up...")
        self.status.grid(
            column=1, columnspan=3, row=2, #1,
            sticky=(N, S, E, W), pady=10)

        # self.X_name = tkinter.StringVar()
        # ttk.Label(
        #     self,
        #     text="Player X:").grid(
        #     column=1,
        #     row=3,
        #     sticky=(
        #         W,
        #         S))
        # self.X_entry = ttk.Entry(self, textvariable=self.X_name)
        # self.X_entry.grid(column=1, row=4, sticky=(E, W, N))
        #
        # self.O_name = tkinter.StringVar()
        # ttk.Label(
        #     self,
        #     text="Player O:").grid(
        #     column=3,
        #     row=3,
        #     sticky=(
        #         W,
        #         S))
        # self.O_entry = ttk.Entry(self, textvariable=self.O_name)
        # self.O_entry.grid(column=3, row=4, sticky=(E, W, N))
        #
        # ttk.Button(
        #     self,
        #     text="Start",
        #     command=start_game,
        #     default=tkinter.ACTIVE).grid(
        #         column=2,
        #         row=4,
        #         padx=10,
        #         sticky=(N, S, E, W))
