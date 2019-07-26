from dataclasses import dataclass, field

from tornado import httputil
from tornado.web import HTTPError


@dataclass(init=False)
class BurdockHTTPError(HTTPError):
    status_code: int = None
    log_message_format: str = "No error message provided."

    log_message: str = field(init=False)
    reason: str = field(init=False)

    def __init__(self, status_code=None, log_message=None, *args, **kwargs):
        if status_code is None:
            status_code = self.status_code

        if log_message is None:
            log_message = self.log_message_format.format(**kwargs)

        if 'reason' not in kwargs:
            kwargs['reason'] = httputil.responses.get(self.status_code, 'Unknown')

        super().__init__(status_code, log_message, *args, **kwargs)


class KernelNotFound(BurdockHTTPError):
    status_code = 404
    log_message_format = "Kernel with id {kernel_id} not found."

    def __init__(self, kernel_id=None, *args, **kwargs):
        super().__init__(kernel_id=kernel_id, *args, **kwargs)


class BurdockNotFound(BurdockHTTPError):
    status_code = 404
    log_message_format = "Burdock instance for id {kernel_id} not found."

    def __init__(self, kernel_id=None, *args, **kwargs):
        super().__init__(kernel_id=kernel_id, *args, **kwargs)


class BurdockAlreadyExists(BurdockHTTPError):
    status_code = 400
    log_message_format = "Burdock instance for id {kernel_id} already exists."

    def __init__(self, kernel_id=None, *args, **kwargs):
        super().__init__(kernel_id=kernel_id, *args, **kwargs)


class KernelNotIPython(BurdockHTTPError):
    status_code = 400
    log_message_format = "Kernel with id {kernel_id} is not IPython."

    def __init__(self, kernel_id=None, *args, **kwargs):
        super().__init__(kernel_id=kernel_id, *args, **kwargs)


class KernelExecutionError(BurdockHTTPError):
    status_code = 500
    log_message_format = "Kernel execution threw exception {exception.name}: {exception.value}"

    def __init__(self, exception=None, *args, **kwargs):
        super().__init__(exception=exception, *args, **kwargs)
