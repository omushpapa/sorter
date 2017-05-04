#! /usr/bin/env python3

import base64
from .icons import icon_string
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from operations import initiate_operation
from filegroups import typeGroups


class TkGui(Tk):

    def __init__(self):
        super(TkGui, self).__init__()
        self.title('Sorter')

        # Configure icon
        icondata = base64.b64decode(icon_string)  # utf-8 encoded
        self.icon = PhotoImage(data=icondata)
        self.tk.call('wm', 'iconphoto', self._w, self.icon)

        # Configure main window
        self.resizable(width=False, height=True)
        self.maxsize(550, 300)
        self.minsize(550, 200)
        self.geometry('{0}x{1}+{2}+{3}'.format(550, 300, 200, 200))
        self.init_ui()

    def init_ui(self):
        # Configure default theme
        style = ttk.Style(self)
        style.theme_use('clam')
        bg = self.cget('bg')
        style.configure('My.TFrame', background=bg)

        # Configure menubar
        menu = Menu(self)
        self.config(menu=menu)
        file_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label='File', menu=file_menu)
        dir_submenu = Menu(file_menu, tearoff=False)
        dir_submenu.add_command(
            label='Source', command=lambda: self._show_diag('source'))
        dir_submenu.add_command(label='Destination',
                                command=lambda: self._show_diag('destination'))
        file_menu.add_cascade(label='Open', menu=dir_submenu)

        file_menu.add_separator()
        file_menu.add_command(label='Quit', command=self._show_exit_dialog)

        help_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label='Help', menu=help_menu)
        help_menu.add_command(
            label='Help', command=self._show_help, accelerator='F1')
        help_menu.add_command(label='About', command=self._show_about)
        self.bind_all('<F1>', self._show_help)

        # Create main frames
        self.top_frame = ttk.Frame(self, style='My.TFrame')
        self.top_frame.pack(side=TOP, expand=YES, fill=X)
        self.mid_frame = ttk.Frame(self, style='My.TFrame')
        self.mid_frame.pack(side=TOP, expand=YES, fill=BOTH)
        self.bottom_frame = ttk.Frame(self, style='My.TFrame')
        self.bottom_frame.pack(side=TOP, expand=YES, fill=X)

        # Configure frame for Label widgets
        label_frame = ttk.Frame(self.top_frame, style='My.TFrame')
        label_frame.pack(side=LEFT, fill=Y, expand=YES)
        source_label = ttk.Label(
            label_frame, text='Source', anchor=W, background=bg)
        source_label.pack(ipady=2.5, pady=5, side=TOP, fill=X)
        dst_label = ttk.Label(
            label_frame, text='Destination', anchor=W, background=bg)
        dst_label.pack(ipady=2.5, pady=5, side=BOTTOM, fill=X)

        # Configure frame for Entry widgets
        entry_frame = ttk.Frame(self.top_frame, style='My.TFrame')
        entry_frame.pack(side=LEFT, fill=Y, expand=YES)
        self.source_entry = ttk.Entry(entry_frame, width=50)
        self.source_entry.pack(ipady=2.5, pady=5, side=TOP, expand=YES)
        self.dst_entry = ttk.Entry(entry_frame, width=50)
        self.dst_entry.pack(ipady=2.5, pady=5, side=BOTTOM, expand=YES)
        self.dst_entry.insert(0, 'optional')

        # Configure frame for dialog buttons
        diag_frame = ttk.Frame(self.top_frame, style='My.TFrame')
        diag_frame.pack(side=LEFT, expand=YES)
        source_button = ttk.Button(diag_frame,
                                   text='Choose',
                                   command=lambda: self._show_diag('source'))
        source_button.pack(side=TOP, pady=5)
        dst_button = ttk.Button(diag_frame,
                                text='Choose',
                                command=lambda: self._show_diag('destination'))
        dst_button.pack(side=BOTTOM, pady=5)

        # Configure Options frame
        options_frame = LabelFrame(self.mid_frame, text='Options')
        options_frame.pack(fill=BOTH, expand=YES, padx=5, pady=10)
        self.sort_folders = IntVar()
        self.recursive = IntVar()
        types_value = IntVar()
        self.file_types = []
        sort_option = Checkbutton(
            options_frame, text='Sort folders', variable=self.sort_folders)
        sort_option.pack(side=LEFT)
        recursive_option = Checkbutton(
            options_frame, text='recursive', variable=self.recursive)
        recursive_option.pack(side=LEFT)
        self.types_window = None
        self.items_option = Checkbutton(options_frame, text='types',
                                        variable=types_value,
                                        command=lambda: self._show_types_window(types_value))
        self.items_option.pack(side=LEFT)

        # Configure action buttons
        self.run_button = ttk.Button(self.bottom_frame,
                                     text='Run',
                                     command=self.run_sorter)
        self.run_button.pack(side=LEFT, padx=5)
        self.quit_button = ttk.Button(self.bottom_frame,
                                      text='Quit',
                                      command=self._show_exit_dialog)
        self.quit_button.pack(side=RIGHT, padx=5)

        # Configure status bar
        self.status_bar = ttk.Label(self, text='Ready',
                                    relief=SUNKEN, anchor=W)
        self.status_bar.pack(side=BOTTOM, fill=X)

    def _set_types(self, types, item):
        type_obj = types.get(item)
        add = bool(type_obj.get())
        if add:
            self.file_types.append(item.lower())
        if not add:
            self.file_types.remove(item.lower())

    def _on_closing(self, event=None):
        if not self.file_types or event is None:
            self.file_types = ['*']
            self.items_option.deselect()

    def _show_types_window(self, button_value):
        if bool(button_value.get()):
            self.file_types = []
            # Create new window
            types_window = Toplevel(self)
            types_window.wm_title('Types')
            types_window.tk.call('wm', 'iconphoto', types_window._w, self.icon)
            types_window.resizable(height=False, width=False)
            types_window.bind('<Destroy>', self._on_closing)

            # Configure x-axis scrollbar
            xscrollbar = Scrollbar(types_window, orient=HORIZONTAL)
            xscrollbar.grid(row=1, column=0, sticky=E + W)

            # Configure y-axis scrollbar
            yscrollbar = Scrollbar(types_window, orient=VERTICAL)
            yscrollbar.grid(row=0, column=1, sticky=N + S)

            # Configure canvas
            canvas = Canvas(types_window,
                            width=900,
                            height=600,
                            scrollregion=(0, 0, 2500, 1000),
                            xscrollcommand=xscrollbar.set,
                            yscrollcommand=yscrollbar.set)

            canvas.grid(row=0, column=0)
            canvas.config(scrollregion=canvas.bbox("all"))
            yscrollbar.config(command=canvas.yview)
            xscrollbar.config(command=canvas.xview)

            frame = Frame(canvas)

            canvas.create_window(0, 0, anchor=NW, window=frame)

            types = dict()

            # Add items to canvas
            for count, key in enumerate(sorted(typeGroups.keys())):
                options_frame = LabelFrame(frame, text=key)
                options_frame.grid(row=count,
                                   column=0, padx=5, pady=10, sticky=W)

                for item_count, item in enumerate(typeGroups[key]):
                    types[item] = IntVar()
                    item_button = Checkbutton(options_frame,
                                              text=item,
                                              variable=types[item],
                                              command=lambda types=types, key=item: self._set_types(types, key))
                    item_button.pack(side=LEFT)

        else:
            self._on_closing()

    def _show_about(self):
        self.option_add('*Dialog.msg.font', 'Helvetica 9')
        about_message = "Copyright (c) 2017, Aswa Paul.\nAll rights reserved.\nMore information at https://github.com/giantas/sorter"
        messagebox.showinfo(title='About', message=about_message)

    def _show_help(self, info=None):
        self.option_add('*Dialog.msg.font', 'Helvetica 9')
        help_message = "A Python program that sorts files in a folder into folders which are named by type e.g pdf, docx. It (optionally) sorts the folders created in the first sorting into categories e.g audio, video.\nThe 'Source' folder defines the folder in which the sorting should be done.\nThe 'Destination' folder is an optional destination where the user would want the sorted files/folders to be moved to.\n'Sort folders' option sets the program to sort the folders created after sorting files into categories as aforementioned.\n'Recursive option' checks into every subfolder, starting from the source, and sorts files accordingly."
        messagebox.showinfo(title='Help', message=help_message)

    def _show_exit_dialog(self):
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
                           types=self.file_types,
                           status=self.status_bar,
                           gui='tkinter')

    def _show_diag(self, text):
        dir_ = filedialog.askdirectory()
        if text == 'source':
            self.source_entry.delete(0, END)
            self.source_entry.insert(0, dir_)
        if text == 'destination':
            self.dst_entry.delete(0, END)
            self.dst_entry.insert(0, dir_)

    def tk_run(self):
        self.mainloop()
