#! /usr/bin/env python3

import base64
import os
import shutil
import sqlite3
import requests
import json
from .icons import icon_string
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from operations import initiate_operation, recreate_path, DB_NAME, IS_OKAY_FIELD_NAME, DST_FIELD_NAME, SRC_FIELD_NAME, PATHS_TABLE
from filegroups import typeGroups
from requests.exceptions import ConnectionError


class TkGui(Tk):
    SHORT_DESCRIPTION = "Sorter organises/sorts files in a folder into folders which are grouped by type e.g pdf, docx. It (optionally) groups/sorts the folders created in the first sorting into categories e.g audio, video."
    SOURCE_DESCRIPTION = "SOURCE (required)\nThis is the folder in which the sorting should be done i.e the folder containing the disorganised files."
    DESTINATION_DESCRIPTION = "DESTINATION (optional)\nAn optional destination (a folder) where the user would want the sorted files/folders to be moved to."
    SORT_FOLDER_DESCRIPTION = "SORT FOLDERS (optional)\nInstructs Sorter to group the folders created after the first sorting into categories, such as documents, videos, etc."
    RECURSIVE_DESCRIPTION = "RECURSIVE (optional)\nChecks into every subfolder,starting from the source, and groups/sorts the files accordingly."
    TYPES_DESCRIPTION = "TYPES (optional)\nSelect the specific file types/formats to be sorted."
    SEARCH_DESCRIPTION = "SEARCH (optional)\nDirects Sorter to group files containing this value. If this is enabled then, by default, Sort Folders option is enabled to enable the sorted files to be moved to a folder whose name will be the value provided here."
    HELP_MESSAGE = "How it Works \n" + SHORT_DESCRIPTION + "\n\n" + SOURCE_DESCRIPTION + "\n\n" + DESTINATION_DESCRIPTION + \
        "\n\n" + SORT_FOLDER_DESCRIPTION + "\n\n" + RECURSIVE_DESCRIPTION + \
        "\n\n" + TYPES_DESCRIPTION + "\n\n" + SEARCH_DESCRIPTION
    COPYRIGHT_MESSAGE = "Copyright \u00a9 2017\n\nAswa Paul\nAll rights reserved.\n\nMore information at\nhttps://github.com/giantas/sorter"
    TAG = "2.0.0"

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
        self.connection = sqlite3.connect(DB_NAME)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self._check_for_update()

    def init_ui(self):
        # Configure default theme
        style = ttk.Style(self)
        style.theme_use('clam')
        style.map("TEntry", fieldbackground=[
                  ("active", "white"), ("disabled", "#DCDCDC")])
        self.bg = self.cget('bg')
        style.configure('My.TFrame', background=self.bg)

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
        help_menu.add_command(label='Refresh', command=self._delete_db)
        help_menu.add_command(
            label='Update', command=lambda: self._check_for_update(user_checked=True))
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
            label_frame, text='Source', anchor=W, background=self.bg)
        source_label.pack(ipady=2.5, pady=5, side=TOP, fill=X)
        dst_label = ttk.Label(
            label_frame, text='Destination', anchor=W, background=self.bg)
        dst_label.pack(ipady=2.5, pady=5, side=BOTTOM, fill=X)

        # Configure frame for Entry widgets
        entry_frame = ttk.Frame(self.top_frame, style='My.TFrame')
        entry_frame.pack(side=LEFT, fill=Y, expand=YES)
        self.source_entry = ttk.Entry(entry_frame, width=50)
        self.source_entry.pack(ipady=2.5, pady=5, side=TOP, expand=YES)
        self.dst_entry = ttk.Entry(entry_frame, width=50, state='disabled')
        self.dst_entry.pack(ipady=2.5, pady=5, side=BOTTOM, expand=YES)

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

        # Configure search string option
        self.search_option_value = IntVar()
        search_option = Checkbutton(
            options_frame, text='search',
            variable=self.search_option_value,
            command=lambda: self._enable_search_entry(self.search_option_value))
        search_option.pack(side=LEFT)

        self.search_entry = ttk.Entry(
            options_frame, width=15, state='disabled')
        self.search_entry.pack(side=LEFT)

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

    def _check_for_update(self, user_checked=False):
        link = 'https://api.github.com/repos/giantas/sorter/releases/latest'
        try:
            resp = requests.get(link, timeout=5)
        except ConnectionError:
            pass
        else:
            if resp.ok:
                items = json.loads(resp.text)
                latest_tag = items.get('tag_name')
                if latest_tag.strip('v') > self.TAG:
                    url = items.get('html_url')
                    message = 'Update available!\n\nSorter {0} found.\n\nDownload from {1}'.format(
                        latest_tag, url)
                    relief = SUNKEN
                else:
                    if user_checked:
                        message = 'No update found.\n\nYou have the latest version installed.\n\nStay tuned for more!'
                        relief = FLAT
                    else:
                        return
            else:
                return
            self._show_update_window(message, relief)

    def _show_update_window(self, message, relief):
        update_window = self._create_window('Update!')
        update_window.resizable(height=False, width=False)
        update_window.geometry('{0}x{1}+{2}+{3}'.format(280, 170, 300, 150))
        msg = Message(update_window, justify=CENTER,
                      text=message, relief=relief)
        msg.config(pady=10, padx=10, font='Helvetica 12')
        msg.pack(fill=Y)

    def _delete_db(self):
        try:
            os.remove(os.path.join(os.getcwd(), DB_NAME))
        except FileNotFoundError:
            error_msg = 'Could not locate "{0}". Check application folder and delete "{0}"'.format(
                DB_NAME)
            messagebox.showwarning(title='Error', message=error_msg)

    def _enable_search_entry(self, value):
        if bool(value.get()):
            self.search_entry.config(state='normal')
        else:
            self.search_entry.config(state='disabled')

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
            types_window = self._create_window('Types')
            types_window.geometry('{0}x{1}+{2}+{3}'.format(900, 600, 100, 80))
            types_window.bind('<Destroy>', self._on_closing)

            canvas = self._create_canvas(types_window)

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

                # Hack: Alter height to refit contents to canvas
                h = canvas.winfo_height()
                canvas.configure(height=h + 1)

        else:
            self._on_closing()

    def _create_window(self, title):
        toplevel_window = Toplevel(self)
        toplevel_window.wm_title(title)
        toplevel_window.tk.call(
            'wm', 'iconphoto', toplevel_window._w, self.icon)
        return toplevel_window

    def _show_about(self):
        about_window = self._create_window('About')
        about_window.resizable(height=False, width=False)
        about_window.geometry('+{0}+{1}'.format(300, 150))
        about_message = 'Sorter v' + self.TAG + '\n' + self.COPYRIGHT_MESSAGE
        msg = Message(about_window, justify=CENTER,
                      text=about_message, relief=SUNKEN)
        msg.config(pady=10, padx=10, font='Helvetica 9')
        msg.pack(fill=Y)

    def _show_help(self, info=None):
        help_window = self._create_window('Help')
        help_window.resizable(height=False, width=False)
        help_window.geometry('+{0}+{1}'.format(200, 200))
        help_message = self.HELP_MESSAGE
        msg = Message(help_window, text=help_message,
                      justify=LEFT, relief=RIDGE)
        msg.config(pady=10, padx=10, font='Helvetica 10')
        msg.pack(fill=BOTH)

    def _show_exit_dialog(self):
        answer = messagebox.askyesno(title='Leave',
                                     message='Do you really want to quit?')
        if answer:
            self.connection.close()
            self.destroy()

    def run_sorter(self):
        """Call Sorter operations on the provided values."""
        dst = self.dst_entry.get()
        search_string = ''
        sort_value = bool(self.sort_folders.get())

        if dst == 'optional':
            dst = None

        if bool(self.search_option_value.get()):
            search_string = self.search_entry.get()
            sort_value = True

        report = initiate_operation(src=self.source_entry.get(),
                                    dst=dst,
                                    search_string=search_string,
                                    sort=sort_value,
                                    recur=bool(self.recursive.get()),
                                    types=self.file_types,
                                    status=self.status_bar)

        if report:
            self._show_report(report)

    def _create_canvas(self, window):

        def resize(self, event=None):
            """Resize canvas to fit all contents"""
            canvas.configure(scrollregion=canvas.bbox('all'))

        # Configure canvas
        canvas = Canvas(window)
        hsb = ttk.Scrollbar(window, orient="h", command=canvas.xview)
        vsb = ttk.Scrollbar(window, orient="v", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        canvas.grid(sticky="nsew")
        hsb.grid(row=1, column=0, stick="ew")
        vsb.grid(row=0, column=1, sticky="ns")

        window.grid_rowconfigure(0, weight=1)
        window.grid_columnconfigure(0, weight=1)

        canvas.configure(scrollregion=(0, 0, 1250, 10000))
        canvas.bind('<Configure>', resize)

        return canvas

    def _show_report(self, report):
        def quit(window):
            window.destroy()

        # Configure Report window
        window = self._create_window('Sorter Report')
        window.geometry('{0}x{1}+{2}+{3}'.format(900, 600, 100, 80))

        canvas = self._create_canvas(window)

        frame = Frame(canvas)
        frame.pack(side=LEFT)

        canvas.create_window(0, 0, anchor=NW, window=frame)
        PADX, PADY, IPADX, IPADY = 1, 5, 5, 5

        # Add items to canvas
        llabel = ttk.Label(frame, text='Undo', anchor=N,
                           background=self.bg, borderwidth=0)
        llabel.grid(row=0, column=0, sticky="nsew", padx=PADX)
        llabel = ttk.Label(frame, text='Action', anchor=N,
                           background=self.bg, borderwidth=0)
        llabel.grid(row=0, column=1, sticky="nsew", padx=PADX)
        llabel = ttk.Label(frame, text='Filename', anchor=N,
                           background=self.bg, borderwidth=0)
        llabel.grid(row=0, column=2, sticky="nsew", padx=PADX)
        llabel = ttk.Label(frame, text='From', anchor=N,
                           background=self.bg, borderwidth=0)
        llabel.grid(row=0, column=3, sticky="nsew", padx=PADX)
        llabel = ttk.Label(frame, text='To', anchor=N,
                           background=self.bg, borderwidth=0)
        llabel.grid(row=0, column=4, sticky="nsew", padx=PADX)

        buttons = {}
        ROW_COUNT = 2

        def reverse_action(origin, current_path, button_index, commit=True):
            """Undo the conducted Sorter operation."""
            recreate_path(os.path.dirname(origin))
            try:
                shutil.move(current_path, origin)
            except FileNotFoundError:
                pass
            else:
                query = 'UPDATE {tn} SET {ok}="0" WHERE {src}="{srcv}" AND {dst}="{dstv}"'.format(
                    tn=PATHS_TABLE, ok=IS_OKAY_FIELD_NAME, src=SRC_FIELD_NAME, dst=DST_FIELD_NAME,
                    srcv=origin, dstv=current_path)
                self.cursor.execute(query)
                buttons[button_index].config(state='disabled')
                del buttons[button_index]
                if commit:
                    self.connection.commit()

        def reverse_all(report):
            """Undo all the conducted Sorter operations in the current instance."""
            if buttons:
                for count, value in enumerate(report, ROW_COUNT):
                    reverse_action(value[1], value[2], count, commit=False)
                self.connection.commit()

        for count, value in enumerate(report, ROW_COUNT):
            buttons[count] = ttk.Button(frame, text='Undo',
                                        command=lambda origin=value[1], current_path=value[2], i=count: reverse_action(
                                            origin, current_path, i))
            buttons[count].grid(row=count, column=0, padx=PADX,
                                pady=PADY)

            action_label = Message(frame, width=400, relief=RAISED, text=value[
                3], anchor=CENTER, background=self.bg, borderwidth=0)
            action_label.grid(row=count, column=1, padx=PADX, pady=PADY,
                              ipadx=IPADX, ipady=IPADY, sticky="nsew")

            filename_label = Message(frame, width=400, relief=RAISED, text=value[
                0], anchor=W, background=self.bg, borderwidth=0)
            filename_label.grid(row=count, column=2, padx=PADX, pady=PADY,
                                ipadx=IPADX, ipady=IPADY, sticky="nsew")

            from_label = Message(frame, width=400, relief=RAISED, text=value[
                1], anchor=W, background=self.bg, borderwidth=0)
            from_label.grid(row=count, column=3, padx=PADX, pady=PADY,
                            ipadx=IPADX, ipady=IPADY, sticky="nsew")

            to_label = Message(frame, width=400, relief=RAISED, text=value[
                2], anchor=W, background=self.bg, borderwidth=0)
            to_label.grid(row=count, column=4, padx=PADX, pady=PADY,
                          ipadx=IPADX, ipady=IPADY, sticky="nsew")

            # Hack: Alter height to refit contents to canvas
            h = canvas.winfo_height()
            canvas.configure(height=h + 1)

        last_row = len(report) + ROW_COUNT

        accept_button = ttk.Button(
            frame, text='Accept', command=lambda: quit(window))
        accept_button.grid(row=last_row, column=1)
        reverse_button = ttk.Button(
            frame, text='Undo All', command=lambda report=report: reverse_all(report))
        reverse_button.grid(row=last_row, column=2)

    def _show_diag(self, text):
        dir_ = filedialog.askdirectory()
        if text == 'source':
            self.source_entry.delete(0, END)
            self.source_entry.insert(0, dir_)
        if text == 'destination':
            self.dst_entry.delete(0, END)
            self.dst_entry.config(state='normal')
            self.dst_entry.insert(0, dir_)

    def tk_run(self):
        """Run the GUI."""
        self.mainloop()
