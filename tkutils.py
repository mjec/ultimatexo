#!/usr/bin/python

import tkinter
from tkinter import N, S, E, W, ttk, messagebox


class ResizingCanvas(tkinter.Canvas):
    """A tkinter.Canvas which automatically resizes its children"""
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


def set_aspect(content_frame, pad_frame, aspect_ratio):
    """A function which places a tkinter frame within a containing frame, and then
    forces the inner frame to keep a specific aspect ratio."""
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
