import json
from typing import Dict

from jupyter_client import KernelManager, MultiKernelManager
from jupyter_client.jsonutil import date_default

from burdock.lab.client import BurdockKernelClient, filter_none, on_execution_idle, filter_stdout, filter_stderr
from burdock.lab.errors.http import BurdockNotFound, KernelExecutionError, KernelNotFound
from burdock.lab.errors.kernel import IPythonExecuteException, FancyPingFailed


class BurdockManager:
    """
    A manager which keeps track of a single instance of Burdock and its
    associated kernel.
    """
    kernel_manager: KernelManager
    client: BurdockKernelClient

    is_installed: bool

    def __init__(self, km: KernelManager):
        self.kernel_manager = km
        self.client = BurdockKernelClient.create(km)
        self.client.start_channels()
        self.is_installed = False

    async def _execute(self, code):
        try:
            return await self.client.execute_async(code)
        except IPythonExecuteException as e:
            raise KernelExecutionError(e)

    def _stream(self, code, filter_pred=None, close_pred=None):
        return self.client.execute_stream_io(code, filter_pred, close_pred)

    async def install(self):
        """
        Check if a BurdockAgent is installed in the kernel, and if not,
        install one.
        """
        response = await self._execute((
            "from IPython.core.getipython import get_ipython\n"
            "from burdock.lab.agent import BurdockAgent\n"
            "BurdockAgent(get_ipython())\n"
        ))

        self.is_installed = True
        return json.dumps(response, default=date_default)

    async def ping(self):
        response = await self._execute("'po' + 'ng'")

        return json.dumps(response, default=date_default)

    async def fancy_ping(self):
        queue = self._stream(
            '_ = [print(i) for i in [1,2,3]]',
            filter_pred=lambda msg: filter_stdout(msg) or filter_stderr(msg),
            close_pred=on_execution_idle
        )

        async def _log_output():
            prev_msg = None
            msg = None
            outputs = []

            while True:
                prev_msg = msg
                msg = await queue.get()
                if msg is None:
                    return {'outputs': outputs}
                else:
                    text = msg['content']['text']
                    outputs += text.split("\n")

                    if len(outputs) >= 3 and outputs[0:3] != ["1", "2", "3"]:
                        raise FancyPingFailed(outputs)

        output = await _log_output()

        return json.dumps(output, default=date_default)


class MultiBurdockManager:
    """
    A manager which keeps track of all extant BurdockManagers and their
    associated kernel managers.
    """
    _instances: Dict[str, BurdockManager]

    def __init__(self, multi_kernel_manager: MultiKernelManager):
        self.multi_kernel_manager = multi_kernel_manager
        self._instances = dict()

    def _check_kernel(self, kernel_id):
        """Check a that a kernel_id exists and raise 404 if not."""
        if kernel_id not in self.multi_kernel_manager:
            raise KernelNotFound(kernel_id)

    def _check_burdock(self, kernel_id):
        if kernel_id not in self:
            raise BurdockNotFound(kernel_id)

    def list_kernel_ids(self):
        return list(self._instances.keys())

    def list_instances(self):
        instances = []
        kernel_ids = self.list_kernel_ids()

        for kernel_id in kernel_ids:
            model = self.instance_model(kernel_id)
            instances.append(model)

        return instances

    def has_instance(self, kernel_id: str):
        return kernel_id in self._instances

    def create_instance(self, kernel_id):
        self._check_kernel(kernel_id)

        km = self.multi_kernel_manager.get_kernel(kernel_id)
        self._instances[kernel_id] = BurdockManager(km)

    def get_instance(self, kernel_id: str):
        return self._instances[kernel_id]

    def instance_model(self, kernel_id: str):
        """Return a JSON-safe dict representing a burdock instance.
        For use in representing Burodck instances in the JSON API."""
        self._check_kernel(kernel_id)
        instance = self._instances[kernel_id]

        model = {
            "id": kernel_id,
            "installed": instance.is_installed
        }
        return model

    def __len__(self):
        return len(self._instances.keys())

    def __contains__(self, kernel_id: str):
        return self.has_instance(kernel_id)

    def __getitem__(self, kernel_id: str):
        return self.get_instance(kernel_id)
