import json

from jupyter_client.jsonutil import date_default
from notebook.base.handlers import APIHandler
from notebook.notebookapp import NotebookWebApplication
from notebook.utils import url_path_join


# noinspection PyAbstractClass
class MainBurdockHandler(APIHandler):
    pass


# noinspection PyAbstractClass
class BurdockHandler(APIHandler):
    def _check_kernel_id(self, kernel_id):
        if kernel_id not in self.kernel_manager:
            raise KeyError(f'Kernel with id not found: {kernel_id}')

    def get(self, kernel_id):
        km = self.kernel_manager
        self._check_kernel_id(kernel_id)

        model = km.kernel_model(kernel_id)

        self.finish(json.dumps(model, default=date_default))


_kernel_id_regex = r'(?P<kernel_id>\w+-\w+-\w+-\w+-\w+)'

default_handlers = [
    (f'/api/burdock/{_kernel_id_regex}', BurdockHandler)
]


def load_jupyter_server_extension(nb_server_app: NotebookWebApplication):
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """

    web_app = nb_server_app.web_app
    base_url = web_app.settings['base_url']

    web_app.add_handlers(r'.*$', [
        (url_path_join(base_url, handler[0]), handler[1])
        for handler in default_handlers
    ])
