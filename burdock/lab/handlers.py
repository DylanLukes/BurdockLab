import json
from concurrent.futures.thread import ThreadPoolExecutor

from jupyter_client import MultiKernelManager
from jupyter_client.jsonutil import date_default
from notebook.base.handlers import APIHandler

from burdock.lab.client import BurdockKernelClient
from burdock.lab.errors import KernelNotFound, KernelNotIPython
from burdock.lab.manager import BurdockRootManager
from burdock.lab.typing import KernelId

# todo: use a less magical number
TIMEOUT = 15


class BaseBurdockHandler(APIHandler):
    root_manager: BurdockRootManager

    @property
    def multi_kernel_manager(self) -> MultiKernelManager:
        """ Somewhat clearer name, to disambiguate from normal KernelManagers. """
        return self.kernel_manager

    def data_received(self, chunk):
        # This override exists because PyCharm won't stop complaining
        # about the class being abstract without it...
        raise NotImplementedError()

    # noinspection PyMethodOverriding
    def initialize(self, root_manager: BurdockRootManager):
        super(APIHandler, self).initialize()
        self.root_manager = root_manager


# noinspection PyAbstractClass
class BurdockRootHandler(BaseBurdockHandler):
    def get(self, *args, **kwargs):
        self.finish(json.dumps({"msg": "nothing here yet!"}))


# noinspection PyAbstractClass
class BurdockKernelHandler(BaseBurdockHandler):
    thread_pool = ThreadPoolExecutor(4)

    def head(self, kernel_id: KernelId):
        if kernel_id not in self.kernel_manager:
            raise KernelNotFound(kernel_id)

        self.finish()

    async def get(self, kernel_id: KernelId):
        multi_km = self.multi_kernel_manager

        if kernel_id not in multi_km:
            raise KernelNotFound(kernel_id)

        km = multi_km.get_kernel(kernel_id)

        if not km.ipykernel:
            raise KernelNotIPython(kernel_id)

        client = BurdockKernelClient.make(km)
        client.start_channels()

        reply = await client.request_execute('sum([1,2,3])')
        return self.finish(json.dumps(reply, default=date_default))


# noinspection PyAbstractClass
class BurdockKernelActionHandler(BaseBurdockHandler):
    def get(self, *args, **kwargs):
        self.finish(json.dumps({"msg": "nope!"}))


_burdock_kernel_id_regex = r"(?P<kernel_id>\w+-\w+-\w+-\w+-\w+)"
_burdock_action_id_regex = r"(?P<action>foo|bar)"

default_handlers = [
    (r"/api/burdock", BurdockRootHandler),
    (r"/api/burdock/%s" % _burdock_kernel_id_regex, BurdockKernelHandler),
    (r"/api/burdock/%s/%s" % (_burdock_kernel_id_regex, _burdock_action_id_regex), BurdockKernelActionHandler)
]
