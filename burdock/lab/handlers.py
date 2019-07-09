import json

from jupyter_client.jsonutil import date_default
from notebook.base.handlers import APIHandler

from burdock.lab.errors import KernelNotFound
from burdock.lab.manager import BurdockManager, BurdockRootManager
from burdock.lab.typing import KernelId


class BaseBurdockHandler(APIHandler):
    root_manager: BurdockRootManager

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
    def head(self, kernel_id: KernelId):
        if kernel_id not in self.kernel_manager:
            raise KernelNotFound(kernel_id)

        self.finish()

    def get(self, kernel_id: KernelId):
        if kernel_id not in self.kernel_manager:
            raise KernelNotFound(kernel_id)

        model = self.kernel_manager.kernel_model(kernel_id)

        self.finish(json.dumps(model, default=date_default))


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
