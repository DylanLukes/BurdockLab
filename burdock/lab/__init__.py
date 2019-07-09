from notebook.notebookapp import NotebookWebApplication
from notebook.utils import url_path_join

from burdock.lab.handlers import default_handlers
from burdock.lab.manager import BurdockRootManager

__all__ = [
    'load_jupyter_server_extension'
]


def load_jupyter_server_extension(nb_server_app: NotebookWebApplication):
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """

    root_manager = BurdockRootManager()

    # noinspection PyUnresolvedReferences
    web_app = nb_server_app.web_app
    base_url = web_app.settings['base_url']

    web_app.add_handlers(r'.*$', [
        (url_path_join(base_url, handler[0]), handler[1], {
            'root_manager': root_manager
        })
        for handler in default_handlers
    ])
