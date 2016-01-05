#!/usr/bin/python

import tkinter
import random
import uuid
import game
from tkinter import N, S, E, W, ttk, messagebox


class ResizingCanvas(tkinter.Canvas):
    # http://stackoverflow.com/questions/22835289/how-to-get-tkinter-canvas-to-dynamically-resize-to-window-width

    def __init__(self, parent, **kwargs):
        tkinter.Canvas.__init__(self, parent, **kwargs)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        # determine the ratio of old width/height to new width/height
        wscale = event.width / self.width
        hscale = event.height / self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "resize" tag
        self.scale("resize", 0, 0, wscale, hscale)


class MainWindow(ttk.Frame):

    class OnGridException(Exception):
        pass

    def draw_grid(
            self,
            colour="black",
            thickness=2,
            rows=3,
            cols=3,
            outer=False,
            caps=tkinter.PROJECTING,
            tags=()):
        """Draws a grid with the specified number of rows and columns on the
        gameboard with the specified colour and line thickness. Each line of the
        grid is tagged with 'resize', 'grid' and anything specified in tags.
        The line caps for each line are those specified by caps. If outer is set
        to True then an outer border will also be drawn."""
        width = self.gameboard.winfo_width()
        height = self.gameboard.winfo_height()
        for r in range(rows):
            if outer or 0 != r:
                y_coord = int(r * height / rows)
                self.gameboard.create_line(
                    0,
                    y_coord,
                    width,
                    y_coord,
                    fill=colour,
                    width=thickness,
                    capstyle=caps,
                    tags=("resize", "grid") + tags)
        for c in range(cols):
            if outer or 0 != c:
                x_coord = int(c * width / cols)
                self.gameboard.create_line(
                    x_coord,
                    0,
                    x_coord,
                    height,
                    fill=colour,
                    width=thickness,
                    capstyle=caps,
                    tags=("resize", "grid") + tags)
        if outer:
            self.gameboard.create_line(
                0,
                height,
                width,
                height,
                fill=colour,
                width=thickness,
                capstyle=caps,
                tags=("resize", "grid") + tags)
            self.gameboard.create_line(
                width,
                0,
                width,
                height,
                fill=colour,
                width=thickness,
                capstyle=caps,
                tags=("resize", "grid") + tags)

    def set_aspect(self, content_frame, pad_frame, aspect_ratio):
        # From http://stackoverflow.com/questions/16523128/resizing-tkinter-frames-with-fixed-aspect-ratio
        # a function which places a frame within a containing frame, and
        # then forces the inner frame to keep a specific aspect ratio

        def enforce_aspect_ratio(event):
            # when the pad window resizes, fit the content into it,
            # either by fixing the width or the height and then
            # adjusting the height or width based on the aspect ratio.

            # start by using the width as the controlling dimension
            desired_width = event.width
            desired_height = int(event.width / aspect_ratio)

            # if the window is too tall to fit, use the height as
            # the controlling dimension
            if desired_height > event.height:
                desired_height = event.height
                desired_width = int(event.height * aspect_ratio)

            # place the window, giving it an explicit size
            content_frame.place(in_=pad_frame,
                                relx=0.5, x=(0 - (desired_width / 2)),
                                rely=0.5, y=(0 - (desired_height / 2)),
                                width=desired_width, height=desired_height)

        pad_frame.bind("<Configure>", enforce_aspect_ratio)

    def get_midpoint(self, row, col, totalrows=9, totalcols=9):
        """Returns a point (x, y) at the centre of the square at row, col
        in the gameboard divided into totalrows rows and totalcols columns."""
        sqare_nw = (
            col * self.gameboard.winfo_width() / totalcols,
            row * self.gameboard.winfo_height() / totalrows)
        dimensions = (
            self.gameboard.winfo_width() / totalcols,
            self.gameboard.winfo_height() / totalrows)
        middle = (sqare_nw[0] + (dimensions[0] / 2),
                  sqare_nw[1] + (dimensions[1] / 2))
        return middle

    def get_bbox(self, row, col, totalrows=9, totalcols=9, size=1):
        """Returns a bounding box (x0, y0, x1, y1) for the square at row, col
        in the gameboard divided into totalrows rows and totalcols columns,
        scaled by size with the same centre point."""
        middle = self.get_midpoint(row, col, totalrows, totalcols)
        dimensions = (
            self.gameboard.winfo_width() / totalcols,
            self.gameboard.winfo_height() / totalrows)
        bbox = (
            middle[0] - (dimensions[0] * size * 0.5),
            middle[1] - (dimensions[1] * size * 0.5),
            middle[0] + (dimensions[0] * size * 0.5),
            middle[1] + (dimensions[1] * size * 0.5)
        )
        return bbox

    def draw_o(
            self,
            row,
            col,
            totalrows=9,
            totalcols=9,
            thickness=5,
            size=0.5,
            tags=()):
        """Draws an O on the gameboard at row, col based on a board with
        totalrows rows and totalcols columns, with thickness as specified. The
        O will be size * the size of the box and will be tagged 'resize', 'o'
        and whatever is specified in tags."""
        bbox = self.get_bbox(row, col, totalrows, totalcols, size)
        self.gameboard.create_oval(
            bbox[0],
            bbox[1],
            bbox[2],
            bbox[3],
            outline="red",
            width=thickness,
            tag=("resize", "o") + tags)

    def draw_x(
            self,
            row,
            col,
            totalrows=9,
            totalcols=9,
            thickness=5,
            size=0.5,
            tags=()):
        """Draws an X on the gameboard at row, col based on a board with
        totalrows rows and totalcols columns, with thickness as specified. The
        X will be size * the size of the box and will be tagged 'resize', 'x'
        and whatever is specified in tags."""
        bbox = self.get_bbox(row, col, totalrows, totalcols, size)
        self.gameboard.create_line(
            bbox[0],
            bbox[1],
            bbox[2],
            bbox[3],
            fill="blue",
            width=thickness,
            capstyle=tkinter.ROUND,
            tag=("resize", "x") + tags)
        self.gameboard.create_line(
            bbox[0],
            bbox[3],
            bbox[2],
            bbox[1],
            fill="blue",
            width=thickness,
            capstyle=tkinter.ROUND,
            tag=("resize", "x") + tags)

    def clear_square(self, type, x0, y0, x1, y1, exclude_tags=("grid",)):
        """Deletes all itesm on the gameboard either overlapping or enclosed by
        the square x0, y0, x1, y1 (determined by the type paramater, which must
        be one of 'enclosed' or 'overlapping'), except those tagged with at
        least one of the exclude_tags"""
        deltag = uuid.uuid4().hex
        if "overlapping" == type:
            self.gameboard.addtag_overlapping(deltag, x0, y0, x1, y1)
        elif "enclosed" == type:
            self.gameboard.addtag_enclosed(deltag, x0, y0, x1, y1)
        else:
            raise TypeError(
                "Argument 'type' must be one of: 'enclosed', 'overlapping'")
        for t in exclude_tags:
            self.gameboard.dtag(t, deltag)
        self.gameboard.delete(deltag)

    def clear_overlapping(self, x0, y0, x1, y1, exclude_tags=("grid",)):
        """Deletes all itesm on the gameboard overlapping the square
        x0, y0, x1, y1 except those tagged with at least one of the exclude_tags"""
        return self.clear_square("overlapping", x0, y0, x1, y1, exclude_tags)

    def clear_enclosed(self, x0, y0, x1, y1, exclude_tags=("grid",)):
        """Deletes all itesm on the gameboard enclosed by the square
        x0, y0, x1, y1 except those tagged with at least one of the exclude_tags"""
        return self.clear_square("enclosed", x0, y0, x1, y1, exclude_tags)

    def clear_board(self, exclude_tags=("grid",)):
        """Deletes all itesm on the gameboard except those tagged with at least
        one of the exclude_tags"""
        return self.clear_square(
            "overlapping",
            0,
            0,
            self.gameboard.winfo_width(),
            self.gameboard.winfo_height(),
            exclude_tags)

    def get_square(self, x, y, totalrows=9, totalcols=9):
        """Returns the (row, col) on the gameboard, divided into totalrows rows
        and totalcols columns, which contains (x, y). Throws MainWindow.OnGridException
        if (x, y) falls on an element tagged 'grid'"""
        row = int(y // (self.gameboard.height / totalrows))
        col = int(x // (self.gameboard.width / totalcols))
        overlapping = self.gameboard.find_overlapping(x, y, x, y)
        if len(overlapping) > 0:
            for e in overlapping:
                tags = self.gameboard.gettags(e)
                if "grid" in tags:
                    raise self.OnGridException()
        return (row, col)

    def gameboard_onclick(self, e):
        """The callback for clicks on the gameboard.
        Calls Game.play() at the appropriate place, and returns feedback to
        the user."""
        try:
            (row, col) = self.get_square(e.x, e.y)
            (outer_row, outer_col, inner_row, inner_col) = (row // 3, col // 3, row % 3, col % 3)
            self.game.play((outer_row, outer_col), (inner_row, inner_col))
            # self.set_status("Played at ({}, {}), ({}, {})".format(outer_row, outer_col, inner_row, inner_col))

            # That self.game.play(...) has changed self.game.active_player so
            # this is backwards
            if self.game.active_player == game.SquareState.X:
                self.draw_o(row, col)
            else:
                self.draw_x(row, col)

            if self.game.child_win is not None:
                self.game_onchildwin(self.game.child_win[0], self.game.child_win[1])
                self.game.child_win = None

            if self.game.overall_win is not None:
                self.show_available_boards(())
            else:
                self.show_available_boards(self.game.available_boards())

        except game.InvalidMoveException:
            self.set_status("({}, {}), ({}, {}) is an invalid move".format(outer_row, outer_col, inner_row, inner_col))

        except self.OnGridException:
            pass

    def game_onchildwin(self, board, player):
        """Called when a child board is won"""

        # Draw a line through the winning location
        winning_line = self.game.main_board[board].child.winning_line
        start_delta = self.get_midpoint(winning_line[0][0], winning_line[0][1])
        end_delta = self.get_midpoint(winning_line[1][0], winning_line[1][1])
        start_point = self.get_bbox(board[0], board[1], 3, 3)
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
            self.draw_x(board[0], board[1], 3, 3, 10, 0.75)
        else:
            self.draw_o(board[0], board[1], 3, 3, 10, 0.75)

    def show_available_boards(self, available_boards):
        self.gameboard.delete("available")
        for b in available_boards:
            bbox = self.get_bbox(b[0], b[1], 3, 3)
            self.gameboard.create_rectangle(
                bbox[0],
                bbox[1],
                bbox[2],
                bbox[3],
                fill="yellow",
                width=0,
                stipple="gray12",
                tags=("resize", "available")
                )
        self.gameboard.tag_lower("available", "grid")

    def set_status(self, t):
        self.infoframe.status.config(text=t)

    def make_infoframe(self):
        self.infoframe = ttk.Frame(self, padding=0)

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

        self.infoframe = InfoFrame(self, game, start_game=None) #self.start_game)
        self.infoframe.grid(column=0, row=1, sticky=(N, W, E, S))

        # We set up an auto-resizing, fixed-aspect-ratio frame which will
        # contain our gameboard canvas
        padframe = ttk.Frame(self, padding=0)
        padframe.grid(column=0, row=0, sticky=(N, W, E, S))
        gameframe = ttk.Frame(padframe, padding=0)
        gameframe.grid(column=0, row=0, sticky=(N, S, W, E))
        gameframe.columnconfigure(0, weight=1)
        gameframe.rowconfigure(0, weight=1)
        self.set_aspect(gameframe, padframe, 1)

        # We set up an auto-resizing canvas for the gameboard
        self.gameboard = ResizingCanvas(gameframe, bg="white")
        self.gameboard.grid(column=0, row=0, sticky=(N, S, E, W))

        # We need to update the root window to make sure we have the right
        # dimensions before we can draw the grids
        self.parent.update()
        self.draw_grid(
            colour="#999",
            thickness=1,
            rows=9,
            cols=9,
            tags=(
                "minor-grid",
            ))
        self.draw_grid(tags=("major-grid",))

        # Create the click binding for the gameboard
        self.gameboard.bind("<Button-1>", self.gameboard_onclick)

        # Highlight all available boards
        self.show_available_boards(self.game.available_boards())

        # Display status
        def log_func(status):
            self.set_status(status)
        self.game.add_log_function(log_func)

        # Set status
        self.set_status("{} to play".format(self.game.active_player.name))

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
            "An ultimate noughts and crosses game by Michael Cordover. Version 1.0 (January 2016). MIT licence.",)

if __name__ == "__main__":
    root = tkinter.Tk()
    root.title("Ultimate XO")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    g = game.Game()

    main_window = MainWindow(root, g)
    main_window.grid(column=0, row=0, sticky=(N, W, E, S))
    root.config(menu=MainMenu(root, g, main_window))

    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    root.mainloop()
