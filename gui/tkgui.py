#! /usr/bin/env python3

import base64
import os
import shutil
import sqlite3
import json
import urllib.request
from .icons import icon_string
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from tkinter import TclError
from helpers import InterfaceHelper
from filegroups import typeGroups
from sdir import Folder
from webbrowser import get
from time import sleep
from tkinter import font


class TkGui(Tk):
    HOMEPAGE = "https://giantas.github.io/sorter"
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
    COPYRIGHT_MESSAGE = "Copyright \u00a9 2017\n\nAswa Paul\nAll rights reserved.\n\nFor more information click"
    TAG = "2.2.4"

    def __init__(self, operations, logger):
        super(TkGui, self).__init__()
        self.title('Sorter')

        # Configure icon
        icondata = base64.b64decode(icon_string)  # utf-8 encoded
        self.icon = PhotoImage(data=icondata)
        self.tk.call('wm', 'iconphoto', self._w, self.icon)

        # Configure main window
        self.resizable(width=False, height=False)
        self.maxsize(550, 300)
        self.minsize(550, 200)
        self.geometry('{0}x{1}+{2}+{3}'.format(550, 300, 200, 200))
        self.operations = operations
        self.logger = logger
        self.db_helper = self.operations.db_helper
        self.init_ui()

    def init_ui(self):
        # Configure default theme
        style = ttk.Style(self)
        style.theme_use('clam')
        style.map("TEntry", fieldbackground=[
                  ("active", "white"), ("disabled", "#DCDCDC")])
        self.bg = self.cget('bg')
        style.configure('My.TFrame', background=self.bg)
        style.configure("blue.Horizontal.TProgressbar",
                        background='#778899', troughcolor=self.bg)
        style.configure("green.Horizontal.TProgressbar",
                        background='#2E8B57', troughcolor=self.bg)

        # Configure menubar
        menu = Menu(self)
        self.config(menu=menu)

        # File menu item
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

        # View menu item
        view_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label='View', menu=view_menu)
        view_menu.add_command(label='History', command=self._show_history)

        # Help menu item
        help_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label='Help', menu=help_menu)
        help_menu.add_command(
            label='Help', command=self._show_help, accelerator='F1')
        usage_link = self.HOMEPAGE + '#usage'
        help_menu.add_command(
            label='Tutorial', command=lambda link=usage_link: self._open_homepage(link))
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

        options_frame_left = ttk.Frame(options_frame, style="My.TFrame")
        options_frame_left.pack(side=LEFT, fill=X, anchor=W, padx=20)

        options_frame_right = ttk.Frame(options_frame, style="My.TFrame")
        options_frame_right.pack(side=LEFT, fill=X, anchor=W, padx=40)

        self.sort_folders = IntVar()
        self.recursive = IntVar()
        types_value = IntVar()
        self.file_types = ['*']
        sort_option = Checkbutton(
            options_frame_left, text='Sort folders', variable=self.sort_folders)
        sort_option.pack(side=TOP, anchor=W)
        recursive_option = Checkbutton(
            options_frame_left, text='Include subfolders', variable=self.recursive)
        recursive_option.pack(side=TOP, anchor=W, pady=5)

        self.types_window = None
        self.items_option = Checkbutton(options_frame_right, text='Filter file formats',
                                        variable=types_value,
                                        command=lambda: self._show_types_window(types_value))
        self.items_option.pack(side=TOP, anchor=W)

        # Configure search string option
        search_frame = ttk.Frame(options_frame_right, style="My.TFrame")
        search_frame.pack(side=TOP, anchor=W, pady=5)

        self.search_option_value = IntVar()
        search_option = Checkbutton(
            search_frame, text='Search for:',
            variable=self.search_option_value,
            command=lambda: self._enable_search_entry(self.search_option_value))
        search_option.grid(row=0, column=0)

        self.search_entry = ttk.Entry(
            search_frame, width=15, state='disabled')
        self.search_entry.grid(row=0, column=1, padx=5)

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
        self.status_bar = ttk.Label(self, text=' Ready',
                                    relief=SUNKEN, anchor=W)
        self.status_bar.pack(side=BOTTOM, fill=X)

        # Configure progress bar
        self.progress_var = DoubleVar()
        self.progress_bar = ttk.Progressbar(self.status_bar,
                                            style="blue.Horizontal.TProgressbar", variable=self.progress_var,
                                            orient=HORIZONTAL, length=120)
        self.progress_bar.pack(side=RIGHT, pady=3, padx=5)
        self.progress_var.set(100)

        self.interface_helper = InterfaceHelper(
            progress_bar=self.progress_bar, progress_var=self.progress_var,
            update_idletasks=self.update_idletasks, status_config=self.status_bar.config)
        self.logger.info('Finished GUI initialisation')

    def _on_mousewheel(self, event, canvas, count):
        canvas.yview_scroll(count, "units")

    def _evaluate(self, event, entry_widget, window):
        count = entry_widget.get()
        try:
            num = int(count)
        except ValueError:
            num = 10
        else:
            num = num or 10
        finally:
            window.destroy()
            self._get_history(num)

    def _show_history(self):
        history_window = self._create_window('History')
        history_window.resizable(height=False, width=False)
        history_window.geometry('{0}x{1}+{2}+{3}'.format(200, 90, 300, 150))

        history_label = ttk.Label(
            history_window, text='Enter number: ', background=self.bg)
        history_label.grid(row=0, column=0, padx=5, pady=5)

        history_entry = ttk.Entry(history_window, width=10)
        history_entry.grid(row=0, column=1, padx=5, pady=5)
        history_entry.focus_set()

        help_text = ttk.Label(history_window, text='Number of files (in history) to view.\n\nPress Enter when done.',
                              background=self.bg, foreground="#C0C0C0", anchor=CENTER, justify='center')
        help_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        history_window.bind('<Return>',
                            lambda event, entry_widget=history_entry, window=history_window: self._evaluate(event, entry_widget, window))
        history_window.bind('<KP_Enter>',
                            lambda event, entry_widget=history_entry, window=history_window: self._evaluate(event, entry_widget, window))

    def _get_history(self, count):
        files = self.db_helper.get_history(count)

        if not files:
            error_msg = 'No data found!'
            messagebox.showwarning(title='Warning', message=error_msg)
            self.logger.warning('Error accessing history:: %s', error_msg)
        else:
            history_window = self._create_window('History')
            history_window.geometry(
                '{0}x{1}+{2}+{3}'.format(500, 400, 300, 150))
            canvas = self._create_canvas(history_window)

            frame = Frame(canvas, background="#C0C0C0")
            frame.pack(side=LEFT)

            canvas.create_window(0, 0, anchor=NW, window=frame)

            PADX, PADY, IPADX, IPADY = 1, 1, 1, 1

            # Add items to canvas
            llabel = ttk.Label(frame, text='Filename', anchor=N, relief=SUNKEN,
                               background=self.bg, borderwidth=0)
            llabel.grid(row=0, column=0, sticky="nsew", padx=PADX, pady=3)
            llabel = ttk.Label(frame, text='Original location', anchor=N, relief=SUNKEN,
                               background=self.bg, borderwidth=0)
            llabel.grid(row=0, column=1, sticky="nsew", padx=PADX, pady=3)
            llabel = ttk.Label(frame, text='Current location', anchor=N, relief=SUNKEN,
                               background=self.bg, borderwidth=0)
            llabel.grid(row=0, column=2, sticky="nsew", padx=PADX, pady=3)
            llabel = ttk.Label(frame, anchor=N, relief=SUNKEN,
                               background=self.bg, borderwidth=0)
            llabel.grid(row=0, column=3, sticky="nsew", padx=0, pady=0)

            for count, item in enumerate(files, 1):
                item_path_object = item.filename_path
                original_location = item_path_object.first().source
                current_location = item_path_object.last().destination

                filename_label = Message(frame, width=400, relief=RAISED, text=item.filename,
                                         anchor=CENTER, background=self.bg, borderwidth=0)
                filename_label.grid(row=count, column=0, padx=PADX, pady=PADY,
                                    ipadx=IPADX, ipady=IPADY, sticky="nsew")

                o_loc_label = Message(frame, width=400, relief=RAISED,
                                      text=original_location, anchor=W, background=self.bg, borderwidth=0)
                o_loc_label.grid(row=count, column=1, padx=PADX, pady=PADY,
                                 ipadx=IPADX, ipady=IPADY, sticky="nsew")

                c_loc_label = Message(frame, width=400, relief=SUNKEN,
                                      text=current_location, anchor=W, background=self.bg, borderwidth=0)
                c_loc_label.grid(row=count, column=2, padx=PADX, pady=PADY,
                                 ipadx=IPADX, ipady=IPADY, sticky="nsew")
                button_label = ttk.Label(
                    frame, width=400, relief=RAISED, anchor=W, background=self.bg, borderwidth=0)
                button_label.grid(row=count, column=3, padx=0, pady=0,
                                  ipadx=IPADX, ipady=IPADY, sticky="nsew")
                button = ttk.Button(button_label, text='Open location',
                                    command=lambda location=os.path.dirname(current_location): get().open(location))
                button.grid(sticky="ns", padx=10, pady=10)

                # Hack: Alter height to refit contents to canvas
                h = canvas.winfo_height()
                canvas.configure(height=h + 1)

    def _check_for_update(self, user_checked=False):
        message = 'Checking for updates...'
        update_window = self._create_window('Update!')
        update_window.resizable(height=False, width=False)
        update_window.geometry('+{0}+{1}'.format(310, 250))
        msg_widget = Message(update_window, justify=CENTER,
                             text=message, relief=SUNKEN)
        msg_widget.config(pady=10, padx=10, font='Helvetica 9')
        msg_widget.pack(fill=Y)
        msg_widget.update()
        sleep(2)
        msg_widget.after(7, lambda msg_widget=msg_widget: self._github_connect(
            msg_widget, user_checked))

    def _github_connect(self, msg_widget, user_checked):
        link = 'https://api.github.com/repos/giantas/sorter/releases/latest'
        try:
            with urllib.request.urlopen(link, timeout=5) as response:
                html = response.read()
        except urllib.request.URLError:
            message = 'Update check failed. Could not connect to the Internet.'
            msg_widget.config(text=message, relief=SUNKEN)
            self.logger.warning(message)
        else:
            items = json.loads(html.decode('utf-8'))
            latest_tag = items.get('tag_name')
            if latest_tag.strip('v') > self.TAG:
                url = items.get('html_url')
                body = items.get('body')
                features = body.replace('*', '')
                message = 'Update available!\n\nSorter {tag} found.\n\n{feat}\n\nDownload from {url}'.format(
                    tag=latest_tag, url=url, feat=features)
                msg_widget.config(text=message, relief=SUNKEN)
            else:
                if user_checked:
                    message = 'No update found.\n\nYou have the latest version installed. Always stay up-to-date with fixes and new features.\n\nStay tuned for more!'
                    msg_widget.config(text=message, relief=FLAT)

    def _delete_db(self):
        db_path = os.path.abspath(self.db_helper.DB_NAME)
        db_name = os.path.basename(db_path)
        try:
            os.remove(db_path)
            messagebox.showinfo(title='Success', message='Database refreshed!')
            self.operations.db_ready = False
        except FileNotFoundError:
            error_msg = 'Could not locate "{0}". \n\nCheck application folder and delete "{1}"'.format(
                db_path, db_name)
            messagebox.showwarning(title='Error', message=error_msg)
            self.logger.warning('Error clearing database:: %s', error_msg)
        finally:
            db_ready = self.db_helper.initialise_db()

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
            types_window.geometry('{0}x{1}+0+0'.format(
                types_window.winfo_screenwidth() - 3, types_window.winfo_screenheight() - 3))
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

                for item in typeGroups[key]:
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
        toplevel_window.wm_attributes("-topmost", 1)
        try:
            toplevel_window.grab_set()
        except TclError:
            pass
        return toplevel_window

    def _open_homepage(self, link, event=None, window=None):
        if window is not None:
            window.destroy()
        get().open(link)

    def _show_about(self):
        about_window = self._create_window('About')
        about_window.resizable(height=False, width=False)
        about_window.geometry('+{0}+{1}'.format(300, 150))

        frame = Frame(about_window, relief=SUNKEN)
        frame.pack(fill=BOTH)
        about_message = 'Sorter v' + self.TAG + '\n' + self.COPYRIGHT_MESSAGE
        msg = Message(frame, justify=CENTER,
                      text=about_message)
        msg.config(pady=5, padx=10, font='Helvetica 9')
        msg.pack(side=TOP, fill=X)
        link_label = Label(frame, justify=CENTER, foreground='blue',
                           text='here', font='Helvetica 9', cursor="hand2")
        link_label.pack(side=BOTTOM, fill=X, ipady=5, ipadx=10)
        underlined_font = font.Font(link_label, link_label.cget("font"))
        underlined_font.configure(underline=True)
        link_label.configure(font=underlined_font)
        link_label.bind('<Button-1>', lambda event=None, link=self.HOMEPAGE,
                        window=about_window: self._open_homepage(link, event, window))

    def _show_help(self, info=None):
        help_window = self._create_window('Help')
        help_window.resizable(height=False, width=False)
        help_window.geometry('+{0}+{1}'.format(240, 180))
        help_message = self.HELP_MESSAGE
        msg = Message(help_window, text=help_message,
                      justify=LEFT, relief=RIDGE)
        msg.config(pady=10, padx=10, font='Helvetica 10')
        msg.pack(fill=BOTH)

    def _show_exit_dialog(self):
        answer = messagebox.askyesno(title='Leave',
                                     message='Do you really want to quit?')
        if answer:
            self.logger.info('Exiting...')
            self.destroy()

    def run_sorter(self):
        """Call Sorter operations on the provided values."""
        src = self.source_entry.get()
        dst = self.dst_entry.get()
        search_string = ''
        sort_value = bool(self.sort_folders.get())

        if dst == 'optional':
            dst = None

        if bool(self.search_option_value.get()):
            search_string = self.search_entry.get()
            sort_value = True

        file_types = self.file_types

        if file_types == ['*']:
            types_given = False
        else:
            types_given = True

        recursive_value = bool(self.recursive.get())

        self.logger.info('Sorter operations initiated. Values: src=%s, dst=%s, search_string=%s, sort_value=%s, recursive_value=%s, file_types=%s, types_given=%s',
                         src, dst, search_string, sort_value,
                         recursive_value, file_types, types_given)

        if self.db_helper.initialise_db():
            report = self.operations.initiate_operation(
                src=src, dst=dst,
                send_message=self.interface_helper.message_user,
                search_string=search_string, sort_folders=sort_value,
                recursive=recursive_value,
                file_types=file_types, types_given=types_given)

            try:
                ops_length = str(len(report))
            except TypeError:
                ops_length = 0
            self.logger.info('%s operations done.', ops_length)

            if report:
                self._show_report(report)
        else:
            self.logger.info('DB initialisation failed.')

    def _create_canvas(self, window):
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
        canvas.bind('<Configure>', lambda event,
                    canvas=canvas: self._resize_canvas(event, canvas))
        canvas.bind_all("<Button-4>", lambda event, count=-1,
                        canvas=canvas: self._on_mousewheel(event, canvas, count))
        canvas.bind_all("<Button-5>", lambda event, count=1,
                        canvas=canvas: self._on_mousewheel(event, canvas, count))
        canvas.bind_all("<MouseWheel>", lambda event, count=1,
                        canvas=canvas: self._on_mousewheel(event, canvas, count))

        return canvas

    def _resize_canvas(self, event, canvas):
        """Resize canvas to fit all contents"""
        canvas.configure(scrollregion=canvas.bbox('all'))

    def _show_report(self, report):
        def quit(window):
            window.destroy()

        # Configure Report window
        window = self._create_window('Sorter Report')
        window.geometry('{0}x{1}+{2}+{3}'.format(900, 600, 100, 80))

        canvas = self._create_canvas(window)

        frame = Frame(canvas, background="#C0C0C0")
        frame.pack(side=LEFT)

        canvas.create_window(0, 0, anchor=NW, window=frame)
        PADX, PADY, IPADX, IPADY = 1, 1, 1, 1

        # Add items to canvas
        llabel = ttk.Label(frame, anchor=N,
                           background=self.bg, borderwidth=0)
        llabel.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        llabel = ttk.Label(frame, text='Filename', anchor=N,
                           background=self.bg, borderwidth=0)
        llabel.grid(row=0, column=1, sticky="nsew", padx=PADX, pady=5)
        llabel = ttk.Label(frame, text='From', anchor=N,
                           background=self.bg, borderwidth=0)
        llabel.grid(row=0, column=2, sticky="nsew", padx=PADX, pady=5)
        llabel = ttk.Label(frame, text='To', anchor=N,
                           background=self.bg, borderwidth=0)
        llabel.grid(row=0, column=3, sticky="nsew", padx=PADX, pady=5)

        buttons = {}
        ROW_COUNT = 2

        def reverse_action(origin, current_path, added_at, button_index):
            """Undo the conducted Sorter operation."""

            original = Folder(os.path.dirname(origin))
            original.recreate()
            try:
                shutil.move(current_path, origin)
            except FileNotFoundError:
                return
            else:
                finders = {'source': origin,
                           'destination': current_path, 'added_at': added_at}
                alter_value = {'accepted': False}
                self.db_helper.alter_path(alter_value, finders)
                buttons[button_index].config(state='disabled')
                del buttons[button_index]

        def reverse_all(report):
            """Undo all the conducted Sorter operations in the current instance."""
            if buttons:
                try:
                    ops_length = str(len(report))
                except TypeError:
                    ops_length = 0
                self.logger.info('Reversing %s operations.', ops_length)
                for count, value in enumerate(report, ROW_COUNT):
                    reverse_action(value[1], value[2], value[3], count)

        for count, value in enumerate(report, ROW_COUNT):
            button_label = ttk.Label(
                frame, width=400, relief=RAISED, anchor=W, background=self.bg, borderwidth=0)
            button_label.grid(row=count, column=0, padx=0, pady=0,
                              ipadx=IPADX, ipady=IPADY, sticky="nsew")
            buttons[count] = ttk.Button(button_label, text='Undo',
                                        command=lambda origin=value[1], current_path=value[2], added_at=value[3], i=count: reverse_action(
                                            origin, current_path, added_at, i))
            buttons[count].grid(padx=5, pady=5, sticky="ns")

            filename_label = Message(frame, width=400, relief=RAISED, text=value[
                0], anchor=CENTER, background=self.bg, borderwidth=0)
            filename_label.grid(row=count, column=1, padx=PADX, pady=PADY,
                                ipadx=IPADX, ipady=IPADY, sticky="nsew")

            from_label = Message(frame, width=400, relief=RAISED, text=value[
                1], anchor=W, background=self.bg, borderwidth=0)
            from_label.grid(row=count, column=2, padx=PADX, pady=PADY,
                            ipadx=IPADX, ipady=IPADY, sticky="nsew")

            to_label = Message(frame, width=400, relief=RAISED, text=value[
                2], anchor=W, background=self.bg, borderwidth=0)
            to_label.grid(row=count, column=3, padx=PADX, pady=PADY,
                          ipadx=IPADX, ipady=IPADY, sticky="nsew")

            # Hack: Alter height to refit contents to canvas
            h = canvas.winfo_height()
            canvas.configure(height=h + 1)

        last_row = len(report) + ROW_COUNT

        buttons_label = ttk.Label(
            frame, width=400, relief=RAISED, anchor=W, background=self.bg, borderwidth=0)
        buttons_label.grid(row=last_row, column=0, columnspan=5, padx=0, pady=0,
                           ipadx=IPADX, ipady=IPADY, sticky="nsew")

        accept_button = ttk.Button(
            buttons_label, text='Accept', command=lambda: quit(window))
        accept_button.grid(row=0, column=0, padx=10, pady=40, sticky="ns")
        reverse_button = ttk.Button(
            buttons_label, text='Undo All', command=lambda report=report: reverse_all(report))
        reverse_button.grid(row=0, column=1, padx=10, pady=40, sticky="ns")

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
