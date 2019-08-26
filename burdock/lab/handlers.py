import json
import uuid

from jupyter_client import MultiKernelManager, KernelManager
from notebook.base.handlers import APIHandler
from tornado import web

from burdock.lab.errors.http import KernelNotFound, KernelNotIPython, BurdockNotFound, \
    BurdockAlreadyExists
from burdock.lab.manager import MultiBurdockManager, BurdockManager


class BaseBurdockHandler(APIHandler):
    multi_burdock_manager: MultiBurdockManager

    @property
    def multi_kernel_manager(self) -> MultiKernelManager:
        """ Somewhat clearer name, to disambiguate from 'normal' KernelManagers.
            Also adds some typing assistance. """
        return self.kernel_manager

    def _get_kernel_manager(self, kernel_id) -> KernelManager:
        multi_km = self.multi_kernel_manager

        if kernel_id not in multi_km:
            raise KernelNotFound(kernel_id)

        km: KernelManager = multi_km.get_kernel(kernel_id)

        if not km.ipykernel:
            raise KernelNotIPython(kernel_id)

        return km

    def _get_burdock_manager(self, kernel_id) -> BurdockManager:
        multi_bm = self.multi_burdock_manager

        if kernel_id not in multi_bm:
            raise BurdockNotFound(kernel_id)

        bm: BurdockManager = multi_bm.get_instance(kernel_id)

        return bm

    def data_received(self, chunk):
        # This override exists because PyCharm won't stop complaining
        # about the class being abstract without it...
        raise NotImplementedError()

    # noinspection PyMethodOverriding
    def initialize(self, multi_burdock_manager: MultiBurdockManager):
        super().initialize()
        self.multi_burdock_manager = multi_burdock_manager


# noinspection PyAbstractClass
class MultiBurdockHandler(BaseBurdockHandler):
    async def get(self, *args, **kwargs):
        multi_bm = self.multi_burdock_manager
        response = json.dumps(multi_bm.list_instances())
        return self.finish(response)

    @web.authenticated
    async def post(self, *args, **kwargs):
        multi_bm = self.multi_burdock_manager

        body = json.loads(self.request.body)
        kernel_id = body.get('kernel_id')

        _ = self._get_kernel_manager(kernel_id)

        if kernel_id in multi_bm:
            raise BurdockAlreadyExists(kernel_id)

        multi_bm.create_instance(kernel_id)
        bm = self._get_burdock_manager(kernel_id)

        return self.finish(await bm.install())


# noinspection PyAbstractClass
class BurdockHandler(BaseBurdockHandler):
    @web.authenticated
    async def head(self, kernel_id: str):
        _ = self._get_kernel_manager(kernel_id)
        _ = self._get_burdock_manager(kernel_id)

        return self.finish()

    @web.authenticated
    async def get(self, kernel_id: uuid):
        _ = self._get_kernel_manager(kernel_id)
        bm = self._get_burdock_manager(kernel_id)

        response = json.dumps(bm.is_installed)

        return self.finish(response)


_kernel_id_re = r"(?P<kernel_id>\w+-\w+-\w+-\w+-\w+)"

default_handlers = [
    (r"/api/burdock/?", MultiBurdockHandler),
    (r"/api/burdock/%s" % _kernel_id_re, BurdockHandler),
]
