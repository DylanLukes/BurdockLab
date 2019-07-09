from tornado import httputil
from tornado.web import HTTPError

from burdock.lab.typing import KernelId


class KernelNotFound(HTTPError):
    def __init__(self, kernel_id: KernelId):
        status_code = 404
        msg = f"Kernel with id {kernel_id} not found."
        reason = httputil.responses.get(status_code, 'Unknown')

        super(KernelNotFound, self).__init__(status_code=404,
                                             log_message=msg,
                                             reason=reason)
