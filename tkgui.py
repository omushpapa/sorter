#! /usr/bin/env python3

from tkinter import *
from tkinter import filedialog, messagebox
from operations import initiate_operation


class TkGui(Tk):

    def __init__(self):
        super(TkGui, self).__init__()
        self.title('Sorter')
        self.maxsize(400, 200)
        self.minsize(350, 150)
        self.geometry('{0}x{1}+{2}+{3}'.format(400, 200, 200, 200))
        self.init_ui()

    def init_ui(self):
        self.top_frame = Frame(self)
        self.top_frame.pack(side=TOP, expand=YES, fill=X)
        self.mid_frame = Frame(self)
        self.mid_frame.pack(side=TOP, expand=YES, fill=X)
        self.bottom_frame = Frame(self)
        self.bottom_frame.pack(side=TOP, expand=YES, fill=X)

        label_frame = Frame(self.top_frame)
        label_frame.pack(side=LEFT, fill=Y, expand=YES)
        source_label = Label(label_frame, text='Source')
        source_label.pack(ipady=2.5, side=TOP)
        dst_label = Label(label_frame, text='Destination')
        dst_label.pack(ipady=2.5, side=BOTTOM)

        entry_frame = Frame(self.top_frame)
        entry_frame.pack(side=LEFT, fill=Y, expand=YES)
        self.source_entry = Entry(entry_frame, width=30)
        self.source_entry.pack(ipady=2.5, side=TOP, expand=YES)
        self.dst_entry = Entry(entry_frame, width=30)
        self.dst_entry.pack(ipady=2.5, side=BOTTOM, expand=YES)
        self.dst_entry.insert(0, 'optional')

        diag_frame = Frame(self.top_frame)
        diag_frame.pack(side=LEFT, expand=YES)
        source_button = Button(diag_frame,
                               text='Choose',
                               command=lambda: self.show_diag('source'))
        source_button.pack(side=TOP)
        dst_button = Button(diag_frame,
                            text='Choose',
                            command=lambda: self.show_diag('destination'))
        dst_button.pack(side=BOTTOM)

        options_frame = LabelFrame(self.mid_frame, text='Options')
        options_frame.pack(fill=BOTH, expand=YES)
        self.sort_folders = IntVar()
        self.recursive = IntVar()
        sort_option = Checkbutton(
            options_frame, text='Sort folders', variable=self.sort_folders)
        sort_option.pack(side=LEFT)
        recursive_option = Checkbutton(
            options_frame, text='recursive', variable=self.recursive)
        recursive_option.pack(side=LEFT)

        self.run_button = Button(self.bottom_frame,
                                 text='Run',
                                 command=self.run_sorter)
        self.run_button.pack(side=LEFT)
        self.quit_button = Button(self.bottom_frame,
                                  text='Quit',
                                  command=self.show_exit_dialog)
        self.quit_button.pack(side=RIGHT)

        self.status_bar = Label(self, text='Ready', bd=1,
                                relief=SUNKEN, anchor=W)
        self.status_bar.pack(side=BOTTOM, fill=X)

    def show_exit_dialog(self):
        answer = messagebox.askyesno(title='Leave',
                                     message='Do you really want to quit?')
        if answer:
            self.destroy()

    def run_sorter(self):
        dst = self.dst_entry.get()
        if dst == 'optional':
            dst = None

        initiate_operation(src=self.source_entry.get(),
                           dst=dst,
                           sort=bool(self.sort_folders.get()),
                           recur=bool(self.recursive.get()),
                           types=None,
                           status=self.status_bar,
                           gui='tkinter')

    def show_diag(self, text):
        dir_ = filedialog.askdirectory()
        print(dir_)
        if text == 'source':
            self.source_entry.delete(0, END)
            self.source_entry.insert(0, dir_)
        if text == 'destination':
            self.dst_entry.delete(0, END)
            self.dst_entry.insert(0, dir_)

    def tk_run(self):
        self.mainloop()
