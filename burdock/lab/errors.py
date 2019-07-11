from tornado import httputil
from tornado.web import HTTPError

from burdock.lab.typing import KernelId


class KernelNotFound(HTTPError):
    status_code = 404
    msg = "Kernel with id {kernel_id} not found."

    def __init__(self, kernel_id: KernelId):
        status_code = KernelNotFound.status_code
        msg = KernelNotFound.msg.format(kernel_id=kernel_id)
        reason = httputil.responses.get(status_code, 'Unknown')

        super(KernelNotFound, self).__init__(status_code=status_code,
                                             log_message=msg,
                                             reason=reason)


class KernelNotIPython(HTTPError):
    status_code = 400
    msg = "Kernel with id {kernel_id} is not IPython."

    def __init__(self, kernel_id: KernelId):
        status_code = KernelNotIPython.status_code
        msg = KernelNotIPython.msg.format(kernel_id=kernel_id)
        reason = httputil.responses.get(KernelNotIPython.status_code, 'Unknown')

        super(KernelNotFound, self).__init__(status_code=status_code,
                                             log_message=msg,
                                             reason=reason)
