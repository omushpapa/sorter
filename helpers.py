#! /usr/bin/env python3.4


class InterfaceHelper(object):
    """Handles the messaging to the user."""

    def __init__(self, progress_bar, progress_var, update_idletasks, status_config):
        progress_bar.configure(maximum=100)
        self.progress_bar = progress_bar
        self.progress_var = progress_var
        self.update_idletasks = update_idletasks
        self.status_config = status_config

    def message_user(self, through='status', msg='Ready', weight=0, value=0):
        """Show a message to the user."""
        if through == 'status':
            self._use_status(msg, weight)
        if through == 'progress_bar':
            self._use_progress_bar(weight, value)
        if through == 'both':
            self._use_status(msg, weight)
            self._use_progress_bar(weight, value)

    def _use_status(self, msg, weight):
        if weight == 0:
            self.status_config(foreground='black', text=' {}'.format(str(msg)))
        if weight == 1:
            self.status_config(foreground='blue', text=' {}'.format(str(msg)))
        if weight == 2:
            self.status_config(foreground='red',
                               text=' {}'.format(str(msg)))

    def _use_progress_bar(self, weight, value):
        color = 'blue'
        if weight == 1:
            color = 'green'
        self.progress_var.set(value)
        self.progress_bar.configure(
            style="{}.Horizontal.TProgressbar".format(color))
        self.update_idletasks()
