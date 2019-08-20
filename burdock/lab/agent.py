import tempfile
from typing import List

import pandas as pd
from IPython import InteractiveShell
from burdock.core import Burdock
from ipykernel.ipkernel import IPythonKernel
from ipykernel.comm import CommManager, Comm
from jupyter_client.session import Session


class BurdockAgent:
    """
    A Burdock "agent" is installed into an IPython kernel, and is used
    to fulfill requests for information.
    """
    shell: InteractiveShell
    # comm_manager:

    dataframes: List[str]

    def __init__(self, shell: InteractiveShell):
        self.shell = shell

        self.session = Session()
        self.dataframes = list()

        self.install()
        self.update_dataframes()

    # --------------------------------------------------------------------------
    # Delegated Properties
    # --------------------------------------------------------------------------
    @property
    def kernel(self) -> IPythonKernel:
        # This does exist, it's just set by the IPyKernel itself,
        # e.g. as `self.shell.kernel = self`
        # noinspection PyUnresolvedReferences
        return self.shell.kernel

    @property
    def comm_manager(self) -> CommManager:
        return self.kernel.comm_manager

    # --------------------------------------------------------------------------
    # Voodoo
    # --------------------------------------------------------------------------
    def install(self):
        # Place a reference/GC anchor in the user namespace.
        self.shell.user_ns['__burdock__'] = self

        # Register for post_execute events (so that we can update our dataframes).
        self.shell.events.register('post_execute', self.update_dataframes)

        # Establish a comm target to talk to the front end.
        def dummy_target_func(comm: Comm, open_msg):
            print(f"OPEN MESSAGE: {open_msg}")

            @comm.on_msg
            def _recv(msg):
                print(f"RECEIVED MESSAGE: {msg}")

        self.comm_manager.register_target('burdocklab_main_target', dummy_target_func)

    # --------------------------------------------------------------------------
    # DataFrame variable tracking
    # --------------------------------------------------------------------------

    @property
    def data_frame_variables(self):
        return self.dataframes

    def get_dataframes(self):
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

    def update_dataframes(self):
        self.dataframes = self.get_dataframes()

    # --------------------------------------------------------------------------
    # Running Daikon (via Burdock)
    # --------------------------------------------------------------------------

    def analyze(self, name: str) -> (str, str):
        user_ns = self.shell.user_ns
        assert name in user_ns

        df = user_ns.get(name)
        assert isinstance(df, pd.DataFrame)

        burdock = Burdock(name, df)
        burdock.match()
        burdock.expand()

        # todo: don't spew so many tmp files...
        decls_tmp = tempfile.NamedTemporaryFile(mode='w+',
                                                prefix='burdock-',
                                                suffix='.decls',
                                                delete=False)
        burdock.write_decls(decls_tmp)

        dtrace_tmp = tempfile.NamedTemporaryFile(mode='w+',
                                                 prefix='burdock-',
                                                 suffix='.dtrace',
                                                 delete=False)
        burdock.write_dtrace(dtrace_tmp)

        return decls_tmp.name, dtrace_tmp.name
