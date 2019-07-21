import uuid

from tornado import httputil
from tornado.web import HTTPError

from burdock.lab.errors.kernel import IPythonExecuteException


class KernelNotFound(HTTPError):
    status_code = 404
    msg = "Kernel with id {kernel_id} not found."

    def __init__(self, kernel_id: str):
        status_code = KernelNotFound.status_code
        msg = KernelNotFound.msg.format(kernel_id=kernel_id)
        reason = httputil.responses.get(status_code, 'Unknown')

        super(KernelNotFound, self).__init__(status_code=status_code,
                                             log_message=msg,
                                             reason=reason)


class KernelNotIPython(HTTPError):
    status_code = 400
    msg = "Kernel with id {kernel_id} is not IPython."

    def __init__(self, kernel_id: str):
        status_code = KernelNotIPython.status_code
        msg = KernelNotIPython.msg.format(kernel_id=kernel_id)
        reason = httputil.responses.get(KernelNotIPython.status_code, 'Unknown')

        super(KernelNotIPython, self).__init__(status_code=status_code,
                                               log_message=msg,
                                               reason=reason)


class KernelExecutionError(HTTPError):
    status_code = 500
    msg = "Kernel execution threw exception {exception.name}: {exception.value}"

    def __init__(self, exception: IPythonExecuteException):
        status_code = KernelExecutionError.status_code
        msg = KernelExecutionError.msg.format(exception=exception)
        reason = httputil.responses.get(KernelExecutionError.status_code, 'Unknown')

        super(KernelExecutionError, self).__init__(status_code=status_code,
                                                   log_message=msg,
                                                   reason=reason)