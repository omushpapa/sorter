#! /usr/bin/env python3.4

import base64
from tkinter import *
from tkinter import ttk
try:
    from .icons import icon_100
except SystemError:
    from icons import icon_100


class Loader(Tk):

    def __init__(self):
        super(Loader, self).__init__()
        self.overrideredirect(True)

        # Configure default theme
        style = ttk.Style(self)
        style.theme_use('clam')
        self.bg = self.cget('bg')
        style.configure('My.TFrame', background=self.bg)
        style.configure("blue.Horizontal.TProgressbar",
                        background='#778899', troughcolor=self.bg)
        self.geometry('{0}x{1}+{2}+{3}'.format(300, 200, 230, 250))
        self._init_ui()

    def _init_ui(self):
        image_data = base64.b64decode(icon_100)
        image = PhotoImage(data=image_data)

        name_frame = ttk.Frame(self, style="My.TFrame", relief=RAISED)
        name_frame.pack(side=TOP, fill=X)

        top_frame = ttk.Frame(self, style="My.TFrame")
        top_frame.pack(side=TOP, fill=X)

        mid_frame = ttk.Frame(self, style="My.TFrame")
        mid_frame.pack(side=TOP, fill=X)

        bottom_frame = ttk.Frame(self, style="My.TFrame")
        bottom_frame.pack(side=BOTTOM, fill=X)

        name_label = ttk.Label(name_frame, background=self.bg,
                               text='Sorter', justify='center', font="Helvetica 12 bold italic")
        name_label.pack(pady=1)

        image_label = ttk.Label(top_frame, image=image,
                                text='546', background=self.bg)
        image_label.image = image
        image_label.pack(side=LEFT, anchor=CENTER, pady=15, padx=20)

        info = 'Easy file organisation\nand management\nwith Sorter.\n\nCopyright \u00a9 2017\n\nAswa Paul\nAll rights reserved.'
        info_label = Message(top_frame, text=info, justify='center')
        info_label.pack(side=LEFT, pady=5, padx=5)

        self.progress_label = ttk.Label(mid_frame, justify='center',
                                        text='loading', background=self.bg, foreground="#778899")
        self.progress_label.pack(side=BOTTOM)

        status_bar = ttk.Label(bottom_frame)
        status_bar.pack(side=BOTTOM, fill=X)

        self.progress_var = DoubleVar()
        self.progress_bar = ttk.Progressbar(status_bar,
                                            length=400, variable=self.progress_var,
                                            orient=HORIZONTAL, maximum=100, style="blue.Horizontal.TProgressbar")
        self.progress_bar.pack(side=LEFT, fill=X)
        self.progress_var.set(10)

    def report_progress(self, value, msg):
        self.progress_label.config(text=msg)
        if value == 100:
            self.destroy()
        else:
            self.progress_var.set(value)
            self.update()

    def tk_run(self):
        self.mainloop()
