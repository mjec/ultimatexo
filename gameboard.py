#!/usr/bin/python

import tkinter
from tkinter import N, S, E, W, ttk, messagebox


class CanvasHelper(object):

    class OnGridException(Exception):
        pass

    @staticmethod
    def draw_grid(canvas, colour="black", thickness=2, rows=3, cols=3, outer=False, caps=tkinter.PROJECTING, tags=()):
        """Draws a grid with the specified number of rows and columns on the
        gameboard with the specified colour and line thickness. Each line of the
        grid is tagged with 'resize', 'grid' and anything specified in tags.
        The line caps for each line are those specified by caps. If outer is set
        to True then an outer border will also be drawn."""

        width = canvas.winfo_width()
        height = canvas.winfo_height()
        for r in range(rows):
            if outer or 0 != r:
                y_coord = int(r * height / rows)
                canvas.create_line(
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
                canvas.create_line(
                    x_coord,
                    0,
                    x_coord,
                    height,
                    fill=colour,
                    width=thickness,
                    capstyle=caps,
                    tags=("resize", "grid") + tags)
        if outer:
            canvas.create_line(
                0,
                height,
                width,
                height,
                fill=colour,
                width=thickness,
                capstyle=caps,
                tags=("resize", "grid") + tags)
            canvas.create_line(
                width,
                0,
                width,
                height,
                fill=colour,
                width=thickness,
                capstyle=caps,
                tags=("resize", "grid") + tags)

    @staticmethod
    def get_midpoint(canvas, row, col, totalrows=9, totalcols=9):
        """Returns a point (x, y) at the centre of the square at row, col
        in the gameboard divided into totalrows rows and totalcols columns."""
        sqare_nw = (
            col * canvas.winfo_width() / totalcols,
            row * canvas.winfo_height() / totalrows)
        dimensions = (
            canvas.winfo_width() / totalcols,
            canvas.winfo_height() / totalrows)
        middle = (sqare_nw[0] + (dimensions[0] / 2),
                  sqare_nw[1] + (dimensions[1] / 2))
        return middle

    @staticmethod
    def get_bbox(canvas, row, col, totalrows=9, totalcols=9, size=1):
        """Returns a bounding box (x0, y0, x1, y1) for the square at row, col
        in the gameboard divided into totalrows rows and totalcols columns,
        scaled by size with the same centre point."""
        middle = CanvasHelper.get_midpoint(canvas, row, col, totalrows, totalcols)
        dimensions = (
            canvas.winfo_width() / totalcols,
            canvas.winfo_height() / totalrows)
        bbox = (
            middle[0] - (dimensions[0] * size * 0.5),
            middle[1] - (dimensions[1] * size * 0.5),
            middle[0] + (dimensions[0] * size * 0.5),
            middle[1] + (dimensions[1] * size * 0.5)
        )
        return bbox

    @staticmethod
    def clear_square(canvas, type, x0, y0, x1, y1, exclude_tags=("grid",)):
        """Deletes all itesm on the gameboard either overlapping or enclosed by
        the square x0, y0, x1, y1 (determined by the type paramater, which must
        be one of 'enclosed' or 'overlapping'), except those tagged with at
        least one of the exclude_tags"""
        deltag = uuid.uuid4().hex
        if "overlapping" == type:
            canvas.addtag_overlapping(deltag, x0, y0, x1, y1)
        elif "enclosed" == type:
            canvas.addtag_enclosed(deltag, x0, y0, x1, y1)
        else:
            raise TypeError(
                "Argument 'type' must be one of: 'enclosed', 'overlapping'")
        for t in exclude_tags:
            canvas.dtag(t, deltag)
        canvas.delete(deltag)

    @staticmethod
    def clear_overlapping(canvas, x0, y0, x1, y1, exclude_tags=("grid",)):
        """Deletes all itesm on the gameboard overlapping the square
        x0, y0, x1, y1 except those tagged with at least one of the exclude_tags"""
        return CanvasHelper.clear_square(canvas, "overlapping", x0, y0, x1, y1, exclude_tags)

    @staticmethod
    def clear_enclosed(canvas, x0, y0, x1, y1, exclude_tags=("grid",)):
        """Deletes all itesm on the gameboard enclosed by the square
        x0, y0, x1, y1 except those tagged with at least one of the exclude_tags"""
        return CanvasHelper.clear_square(canvas, "enclosed", x0, y0, x1, y1, exclude_tags)

    @staticmethod
    def clear_board(canvas, exclude_tags=("grid",)):
        """Deletes all itesm on the gameboard except those tagged with at least
        one of the exclude_tags"""
        return CanvasHelper.clear_square(
            canvas,
            "overlapping",
            0,
            0,
            canvas.winfo_width(),
            canvas.winfo_height(),
            exclude_tags)

    @staticmethod
    def get_square(canvas, x, y, totalrows=9, totalcols=9):
        """Returns the (row, col) on the gameboard, divided into totalrows rows
        and totalcols columns, which contains (x, y). Throws CanvasHelper.OnGridException
        if (x, y) falls on an element tagged 'grid'"""
        row = int(y // (canvas.height / totalrows))
        col = int(x // (canvas.width / totalcols))
        overlapping = canvas.find_overlapping(x, y, x, y)
        if len(overlapping) > 0:
            for e in overlapping:
                tags = canvas.gettags(e)
                if "grid" in tags:
                    raise CanvasHelper.OnGridException()
        return (row, col)

    @staticmethod
    def draw_o(canvas, row, col, totalrows=9, totalcols=9, thickness=5, size=0.5, tags=()):
        """Draws an O on the canvas at row, col based on a board with
        totalrows rows and totalcols columns, with thickness as specified. The
        O will be size * the size of the box and will be tagged 'resize', 'o'
        and whatever is specified in tags."""
        bbox = CanvasHelper.get_bbox(canvas, row, col, totalrows, totalcols, size)
        canvas.create_oval(
            bbox[0],
            bbox[1],
            bbox[2],
            bbox[3],
            outline="red",
            width=thickness,
            tag=("resize", "o") + tags)

    @staticmethod
    def draw_x(canvas, row, col, totalrows=9, totalcols=9, thickness=5, size=0.5, tags=()):
        """Draws an X on the canvas at row, col based on a board with
        totalrows rows and totalcols columns, with thickness as specified. The
        X will be size * the size of the box and will be tagged 'resize', 'x'
        and whatever is specified in tags."""
        bbox = CanvasHelper.get_bbox(canvas, row, col, totalrows, totalcols, size)
        canvas.create_line(
            bbox[0],
            bbox[1],
            bbox[2],
            bbox[3],
            fill="blue",
            width=thickness,
            capstyle=tkinter.ROUND,
            tag=("resize", "x") + tags)
        canvas.create_line(
            bbox[0],
            bbox[3],
            bbox[2],
            bbox[1],
            fill="blue",
            width=thickness,
            capstyle=tkinter.ROUND,
            tag=("resize", "x") + tags)

    @staticmethod
    def higlight_available_boards(canvas, available_boards):
        canvas.delete("available")
        for b in available_boards:
            bbox = CanvasHelper.get_bbox(canvas, b[0], b[1], 3, 3)
            canvas.create_rectangle(
                bbox[0],
                bbox[1],
                bbox[2],
                bbox[3],
                fill="yellow",
                width=0,
                stipple="gray12",
                tags=("resize", "available")
                )
        canvas.tag_lower("available", "grid")
