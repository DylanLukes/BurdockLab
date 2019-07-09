from typing import Type, Set, List

from IPython import InteractiveShell


class BurdockAgent:
    """
    A Burdock "agent" is installed into an IPython kernel, and is used
    to fulfill requests for information.
    """
    shell: InteractiveShell
    _df_vars: List[str]

    def __init__(self, shell: InteractiveShell):
        self.shell = shell
        self._df_vars = list()

        self._install_in_shell()
        self._register_events()
        self._update_df_vars()

    # --------------------------------------------------------------------------
    # Voodoo
    # --------------------------------------------------------------------------
    def _install_in_shell(self):
        self.shell.user_ns_hidden['__burdock__'] = self

    # --------------------------------------------------------------------------
    # DataFrame variable tracking
    # --------------------------------------------------------------------------

    @property
    def data_frame_variables(self):
        return self._df_vars

    def _get_df_vars(self):
        user_ns = self.shell.user_ns
        user_ns_hidden = self.shell.user_ns_hidden

        # This can never be in user_ns (unique), so `is` will always fail.
        unique_object = object()

        out = [i for i in user_ns
               if not i.startswith('_')
               and (user_ns[i] is not user_ns_hidden.get(i, unique_object))
               and (type(user_ns[i]).__name__ == 'DataFrame')]

        out.sort()
        return out

    def _update_df_vars(self):
        self._df_vars = self._get_df_vars()

    # --------------------------------------------------------------------------
    # IPython Events
    # --------------------------------------------------------------------------

    def _register_events(self):
        self.shell.events.register('post_execute', self.post_execute)

    def post_execute(self):
        self._update_df_vars()
