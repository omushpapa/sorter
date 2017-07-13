#! /usr/bin/env python3

import base64
import os
import shutil
import json
import urllib.request
from .icons import icon_string
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from tkinter import TclError
from slib.helpers import InterfaceHelper
from data.filegroups import typeGroups
from webbrowser import get
from tkinter import font
from . import descriptions
from data.version import SORTER_VERSION


class TkGui(Tk):
    """Sorter tkinter GUI class"""

    def __init__(self, operations, logger):
        super(TkGui, self).__init__()
        self.title('Sorter')
        self.protocol("WM_DELETE_WINDOW", self._show_exit_dialog)

        # Configure icon
        icondata = base64.b64decode(icon_string)  # utf-8 encoded
        self.icon = PhotoImage(data=icondata)
        self.tk.call('wm', 'iconphoto', self._w, self.icon)

        # Configure main window
        self.resizable(width=False, height=False)
        self.maxsize(550, 380)
        self.minsize(550, 200)
        self.geometry('{0}x{1}+{2}+{3}'.format(550, 300, 200, 200))
        self.operations = operations
        self.logger = logger
        self.db_helper = self.operations.db_helper
        self._init_ui()

    def _init_ui(self):
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
        self.option_add('*Dialog.msg.font', 'Helvetica 10')

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
        file_menu.add_command(label='Quit', command=self._show_exit_dialog,
                              accelerator="Ctrl+Q")

        # View menu item
        view_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label='View', menu=view_menu)
        view_menu.add_command(label='History', command=self._show_history)

        # Help menu item
        help_menu = Menu(menu, tearoff=False)
        menu.add_cascade(label='Help', menu=help_menu)
        help_menu.add_command(
            label='Help', command=self._show_help, accelerator='F1')
        usage_link = descriptions.HOMEPAGE + '#usage'
        help_menu.add_command(
            label='Tutorial', command=lambda link=usage_link: self._open_link(link))
        help_menu.add_command(label='Refresh', command=self._delete_db)
        help_menu.add_command(
            label='Update', command=lambda: self._check_for_update(user_checked=True))
        help_menu.add_command(label='About', command=self._show_about)
        self.bind_all('<F1>', self._show_help)
        self.bind_all(
            '<Control-q>', lambda event=None: self._show_exit_dialog())

        # Create main frames
        self.top_frame = ttk.Frame(self, style='My.TFrame')
        self.top_frame.pack(side=TOP, expand=YES, fill=X)
        self.mid_frame = ttk.Frame(self, style='My.TFrame')
        self.mid_frame.pack(side=TOP, expand=YES, fill=BOTH)

        self.progress_text = Text(self, height=1,
                                  font='Helvetica 9', relief=FLAT)
        self.progress_text.pack(side=TOP, fill=X, pady=5, padx=5)
        self.progress_text.tag_config(
            "hyperlink", foreground="#778899", underline=1)
        self.progress_text.tag_bind("hyperlink", "<Enter>", lambda event,
                                    widget=self.progress_text: widget.config(cursor="hand2"))
        self.progress_text.tag_bind("hyperlink", "<Leave>", lambda event,
                                    widget=self.progress_text: widget.config(cursor=""))
        self.progress_text.tag_bind("hyperlink", "<Button-1>",
                                    lambda event: self._enable_progress_text())
        self.progress_text.insert(END, 'show progress info', 'hyperlink')
        self.progress_text.config(state=DISABLED)

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

        # Variables
        self.sort_folders = IntVar()
        self.recursive = IntVar()
        types_value = IntVar()
        self.file_types = ['*']
        self.by_extension = IntVar()
        self.cleanup = IntVar()

        # Configure Options frame
        options_frame = LabelFrame(self.mid_frame, text='Options')
        options_frame.pack(fill=BOTH, expand=YES, padx=5, pady=10)

        frame_left = ttk.Frame(options_frame, style="My.TFrame")
        frame_left.pack(side=LEFT, fill=Y, anchor=W, padx=20)

        frame_right = ttk.Frame(options_frame, style="My.TFrame")
        frame_right.pack(side=LEFT, fill=Y, anchor=W, padx=10)

        # For frame_right
        group_separator = ttk.Separator(frame_left)
        group_separator.grid(row=0, column=0, pady=1)

        self.search_string = StringVar()
        search_entry = ttk.Entry(
            frame_left, width=15, state='disabled', textvariable=self.search_string)
        search_entry.grid(row=1, column=1, padx=5, pady=2)

        self.search_option_value = IntVar()
        search_option = Checkbutton(
            frame_left, text='Search for:',
            variable=self.search_option_value, anchor=E,
            command=lambda: self._enable_search_entry(search_entry,
                                                      self.search_option_value))
        search_option.grid(row=1, column=0, pady=3, sticky=W, padx=5)

        self.group_folder_name = StringVar()
        group_folder_entry = ttk.Entry(
            frame_left, width=15, state='disabled', textvariable=self.group_folder_name)
        group_folder_entry.grid(row=2, column=1, padx=5, pady=2, sticky=S)

        self.group_folder_value = IntVar()
        group_folder_option = Checkbutton(
            frame_left, text='Group into folder',
            variable=self.group_folder_value,
            command=lambda: self._enable_search_entry(group_folder_entry, self.group_folder_value))
        group_folder_option.grid(row=2, column=0, pady=3, sticky=W, padx=5)

        extension_button = Checkbutton(
            frame_left, text='Group by file type',
            variable=self.by_extension)
        extension_button.grid(row=3, column=0, pady=3, sticky=W, padx=5)

        # For frame_left
        other_separator = ttk.Separator(frame_right)
        other_separator.grid(row=0, column=0)
        recursive_option = Checkbutton(
            frame_right, text='Look into sub-folders', variable=self.recursive)
        recursive_option.grid(row=1, column=0, sticky=W, pady=3)

        self.types_window = None
        self.items_option = Checkbutton(frame_right, text='Select file types',
                                        variable=types_value,
                                        command=lambda: self._show_types_window(types_value))
        self.items_option.grid(row=2, column=0, sticky=W, pady=3)
        cleanup_option = Checkbutton(frame_right, text='Perform cleanup',
                                     variable=self.cleanup)
        cleanup_option.grid(row=3, column=0, sticky=W, pady=3)
        cleanup_option.select()

        # Configure action buttons
        self.run_button = ttk.Button(self.bottom_frame,
                                     text='Run',
                                     command=self._run_sorter)
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
            update_idletasks=self.update_idletasks, status_config=self.status_bar.config,
            messagebox=messagebox, progress_text=self.progress_text)
        self.logger.info('Finished GUI initialisation. Waiting...')

    def _enable_progress_text(self):
        self.resizable(width=False, height=True)
        self.geometry('{0}x{1}'.format(550, 370))
        self.progress_text.config(state=NORMAL, height=4, background="#D3D3D3")
        self.progress_text.delete('1.0', END)
        self.resizable(width=False, height=False)

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
                             text=message)
        msg_widget.config(pady=10, padx=10, font='Helvetica 9')
        msg_widget.pack(side=TOP, fill=X)
        self.update()
        msg_widget.after(0, lambda msg_widget=msg_widget, window=update_window: self._github_connect(
            msg_widget, user_checked, window))

    def _github_connect(self, msg_widget, user_checked, window):
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
            if latest_tag.strip('v') > SORTER_VERSION:
                items.get('html_url')
                body = items.get('body')
                features = body.replace('*', '')
                message = 'Update available!\n\nSorter {tag}.\n\n{feat} ....\n\nMore information on the'.format(
                    tag=latest_tag, feat=features[:500])
                msg_widget.config(text=message)
                self._official_website_label(master=window, window=window)
            else:
                if user_checked:
                    message = 'No update found.\n\nYou have the latest version installed. Always stay up-to-date with fixes and new features.\n\nStay tuned for more!'
                    msg_widget.config(text=message, relief=FLAT)

    @classmethod
    def _official_website_label(cls, master, window):
        link_label = Label(master, justify=CENTER, foreground='blue',
                           text='Official Website (click)', font='Helvetica 9', cursor="hand2")
        link_label.pack(side=BOTTOM, fill=X, ipady=2, ipadx=10)
        underlined_font = font.Font(link_label, link_label.cget("font"))
        underlined_font.configure(underline=True)
        link_label.configure(font=underlined_font)
        link_label.bind('<Button-1>', lambda event=None, link=descriptions.HOMEPAGE,
                        window=window: cls._open_link(link, event, window))

    def _delete_db(self):
        db_path = os.path.abspath(self.db_helper.DB_NAME)
        try:
            os.remove(db_path)
        except PermissionError:
            messagebox.showwarning(
                title='Success', message='Error refreshing database!\nDelete file at "%s" once the program closes.' % db_path)
            self.logger.warning(
                'Error refreshing database file at %s', db_path)
        else:
            messagebox.showinfo(
                title='Success', message='Database refreshed!\n\nRestart application to continue!')
            self.logger.info('Database refreshed. Closing... %s', db_path)
        self.destroy()

    def _enable_search_entry(self, entry_widget, value):
        if bool(value.get()):
            entry_widget.config(state='normal')
            entry_widget.insert(0, 'Enter name here')
        else:
            entry_widget.delete(0, END)
            entry_widget.config(state='disabled')

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
        toplevel_window.lift()
        try:
            toplevel_window.grab_set()
        except TclError:
            pass
        return toplevel_window

    @classmethod
    def _open_link(cls, link, event=None, window=None):
        if window is not None:
            window.destroy()
        get().open(link)

    def _show_about(self):
        about_window = self._create_window('About Sorter')
        about_window.resizable(height=False, width=False)
        about_window.geometry('+{0}+{1}'.format(300, 150))

        frame = Frame(about_window, relief=SUNKEN)
        frame.pack(side=LEFT, fill=Y)

        about_text = Text(frame, background="white")
        about_text.config(pady=5, padx=10, font='Helvetica 9')
        about_text.pack(side=TOP, fill=X)
        about_text.tag_configure("center", justify='center')
        about_text.tag_configure('big', font=('Helvetica', 20, 'bold'))
        about_text.tag_configure('medium', font=('Helvetica', 12, 'bold'))
        about_text.tag_add("center", 1.0, "end")
        about_text.tag_config("hyperlink", foreground="blue", underline=1)
        about_text.tag_bind("hyperlink", "<Enter>", lambda event,
                            widget=about_text: widget.config(cursor="hand2"))
        about_text.tag_bind("hyperlink", "<Leave>", lambda event,
                            widget=about_text: widget.config(cursor=""))
        about_text.tag_bind("homepage", "<Button-1>", lambda event: self._open_link(
            descriptions.HOMEPAGE, window=about_window))
        about_text.tag_bind("source", "<Button-1>", lambda event: self._open_link(
            descriptions.SOURCE_CODE, window=about_window))

        about_text.insert(END, 'Sorter\n', 'center big')
        about_text.image_create(END, image=self.icon)
        about_text.insert(END, '\n\nv{}'.format(
            SORTER_VERSION), 'center medium')
        about_text.insert(END, '\n{}More information on '.format(
            descriptions.COPYRIGHT_MESSAGE), 'center')
        about_text.insert(END, '{}\n\n'.format(
            descriptions.HOMEPAGE), 'center hyperlink homepage')
        about_text.insert(END, 'Source code at ', 'center')
        about_text.insert(END, '{}\n\n'.format(
            descriptions.SOURCE_CODE), 'center hyperlink source')
        about_text.insert(END, '{:-^40}\n\n'.format(''), 'center medium')
        about_text.insert(END, descriptions.LICENSE)

        scrollbar = ttk.Scrollbar(about_window)
        scrollbar.pack(side=RIGHT, fill=Y)
        scrollbar.config(command=about_text.yview)
        about_text.config(yscrollcommand=scrollbar.set, state="disabled")

    def _show_help(self, info=None):
        help_window = self._create_window('Help')
        help_window.resizable(height=False, width=False)
        help_window.geometry('+{0}+{1}'.format(240, 50))
        help_message = descriptions.HELP_MESSAGE
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

    def _run_sorter(self):
        """Call Sorter operations on the provided values."""
        kwargs = {'send_message': self.interface_helper.message_user}
        kwargs['src'] = self.source_entry.get()
        kwargs['dst'] = self.dst_entry.get()
        kwargs['file_types'] = self.file_types
        kwargs['by_extension'] = bool(self.by_extension.get())
        cleanup = bool(self.cleanup.get())

        search_string = self.search_string.get().strip()
        if bool(self.search_option_value.get()) and search_string and search_string != 'Enter name here':
            kwargs['search_string'] = search_string

        group_folder_name = self.group_folder_name.get().strip()
        if bool(self.group_folder_value.get()) and group_folder_name and group_folder_name != 'Enter name here':
            kwargs['group_folder_name'] = group_folder_name

        kwargs['recursive'] = bool(self.recursive.get())

        if any([kwargs.get('group_folder_name'), kwargs.get('search_string'), kwargs.get('by_extension')]):
            kwargs['group'] = True

        self.logger.info(
            'Sorter operations initiated. Values: %s', tuple(kwargs.items()))
        self.update()

        if self.db_helper.initialise_db():
            report = self.operations.start(**kwargs)

            try:
                ops_length = len(report)
            except TypeError:
                ops_length = 0
            self.logger.info('%s operations done.', ops_length)

            if report is not None:
                if ops_length:
                    self.interface_helper.message_user(through=['status', 'progress_bar', 'dialog'], msg='Sorting finished',
                                                       weight=1, value=100)
                    self._show_report(report, kwargs.get('src'), cleanup)
                else:
                    self.interface_helper.message_user(
                        through=['status', 'progress_bar', 'dialog', 'progress_text'], msg='Files matching search options not found.')
            self.interface_helper.message_user()

        else:
            self.interface_helper.message_user(
                through=['status', 'dialog'], msg='Database initialisation failed.')
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

    def _show_report(self, report, source_path, cleanup):
        # Configure Report window
        window = self._create_window('Sorter Report')
        window.geometry('{0}x{1}+{2}+{3}'.format(900, 600, 100, 80))
        window.protocol("WM_DELETE_WINDOW", lambda: messagebox.showwarning(
            parent=window, message='Press Accept button'))

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

            os.makedirs(os.path.dirname(origin), exist_ok=True)
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
                self.update_idletasks()
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

        def _after_destroy():
            """Destroy window then do some cleanup."""
            window.destroy()
            if cleanup:
                self.interface_helper.message_user(
                    msg='Performing cleanup...', weight=1)
                self.operations.perform_cleanup(source_path)
                self.interface_helper.message_user()

        accept_button = ttk.Button(
            buttons_label, text='Accept', command=_after_destroy)
        accept_button.grid(row=0, column=0, padx=10, pady=40, sticky="ns")

        reverse_button = ttk.Button(
            buttons_label, text='Undo All', command=lambda report=report: reverse_all(report))
        reverse_button.grid(row=0, column=1, padx=10, pady=40, sticky="ns")

    def _show_diag(self, text):
        dir_ = filedialog.askdirectory()
        if dir_:
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
