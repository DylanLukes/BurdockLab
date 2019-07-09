from jupyter_client import KernelClient
from tornado.concurrent import Future


# Notes:
# There are four channels associated with each kernel:
#
# shell: for request/reply calls to the kernel.
# iopub: for the kernel to publish results to frontends.
# hb: for monitoring the kernel’s heartbeat.
# stdin: for frontends to reply to raw_input calls in the kernel.


class BurdockClientWrapper:
    def __init__(self, client: KernelClient):
        self._client = client

    # --------------------------------------------------------------------------
    # Burdock management methods
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Channel proxy methods - Delegated to KernelClient
    # --------------------------------------------------------------------------

    def get_shell_msg(self, *args, **kwargs):
        return self._client.get_shell_msg(*args, **kwargs)

    def get_iopub_msg(self, *args, **kwargs):
        return self._client.get_iopub_msg(*args, **kwargs)

    def get_stdin_msg(self, *args, **kwargs):
        return self._client.get_stdin_msg(*args, **kwargs)

    # --------------------------------------------------------------------------
    # Channel management methods – Delegated to KernelClient
    # --------------------------------------------------------------------------

    def start_channels(self, shell=True, iopub=True, stdin=True, hb=True):
        return self._client.start_channels(shell=shell, iopub=iopub, stdin=stdin, hb=hb)

    def stop_channels(self):
        return self._client.stop_channels()

    @property
    def channels_running(self):
        return self._client.channels_running

    @property
    def shell_channel(self):
        return self._client.shell_channel

    @property
    def iopub_channel(self):
        return self._client.iopub_channel

    @property
    def stdin_channel(self):
        return self._client.stdin_channel

    @property
    def hb_channel(self):
        return self._client.hb_channel

    def is_alive(self):
        return self._client.is_alive()
