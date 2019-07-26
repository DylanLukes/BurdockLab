from asyncio import Future, Queue
from typing import Optional

from ipython_genutils.py3compat import string_types
from jupyter_client import KernelManager
from jupyter_client.client import validate_string_dict
from jupyter_client.threaded import ThreadedKernelClient
from traitlets import Type

from burdock.lab.message import Message
from burdock.lab.util.channels import AsyncChannel, MessagePredicate
from burdock.lab.errors.kernel import ExecuteError, ExecuteAbort
from burdock.lab.util.finite_queue import FiniteQueue


def filter_none(_msg: Message) -> bool:
    return True


def filter_stdout(msg: Message) -> bool:
    try:
        return msg.header.msg_type == 'stream' \
               and msg.content['name'] == 'stdout'
    except KeyError:
        return False


def filter_stderr(msg: Message) -> bool:
    try:
        return msg.header.msg_type == 'stream' \
               and msg.content['name'] == 'stderr'
    except KeyError:
        return False


def on_execution_idle(msg: Message) -> bool:
    try:
        return msg.header.msg_type == 'status' \
               and msg.content['execution_state'] == 'idle'
    except KeyError:
        return False


class BurdockKernelClient(ThreadedKernelClient):
    iopub_channel_class = Type(AsyncChannel)
    shell_channel_class = Type(AsyncChannel)
    stdin_channel_class = Type(AsyncChannel)

    # Typing hints to enhance IDE support.
    iopub_channel: AsyncChannel
    shell_channel: AsyncChannel
    stdin_channel: AsyncChannel

    burdock_channel: AsyncChannel

    @staticmethod
    def create(km: KernelManager, **kwargs) -> 'BurdockKernelClient':
        kw = {}
        kw.update(km.get_connection_info(session=True))
        kw.update(dict(
            connection_file=km.connection_file,
            parent=km,
        ))

        # add kwargs last, for manual overrides
        kw.update(kwargs)
        return BurdockKernelClient(**kw)

    def execute_stream_io(self, code,
                          filter_pred: MessagePredicate = None,
                          close_pred: MessagePredicate = None,
                          silent=False, store_history=True,
                          user_expressions=None, allow_stdin=None, stop_on_error=True) -> FiniteQueue:
        """
            Similar to KernelClient.execute, but with asynchronous goodness.
            This is intended only for shell channel request/reply style messages.
        """

        if filter_pred is None:
            filter_pred = filter_none
        if close_pred is None:
            close_pred = on_execution_idle

        if user_expressions is None:
            user_expressions = {}
        if allow_stdin is None:
            allow_stdin = self.allow_stdin

        if not isinstance(code, string_types):
            raise ValueError(f"code {code!r} must be a string")
        validate_string_dict(user_expressions)

        content = dict(code=code, silent=silent, store_history=store_history,
                       user_expressions=user_expressions, allow_stdin=allow_stdin,
                       stop_on_error=stop_on_error)

        msg = self.session.msg('execute_request', content)
        msg_id = msg['header']['msg_id']

        stream_queue = self.iopub_channel.register_queue(msg_id, filter_pred, close_pred)

        self.shell_channel.send(msg)
        print("")
        print(f"OUT {msg['header']['msg_id']}:{msg['header']['msg_type']}")

        return stream_queue

    def execute_async(self, code, silent=False, store_history=True,
                      user_expressions=None, allow_stdin=None, stop_on_error=True) -> Future:
        """
        Similar to KernelClient.execute, but returns a Future for the execution result.
        This is intended only for shell channel request/reply style messages.
        """
        if user_expressions is None:
            user_expressions = {}
        if allow_stdin is None:
            allow_stdin = self.allow_stdin

        if not isinstance(code, string_types):
            raise ValueError(f"code {code!r} must be a string")
        validate_string_dict(user_expressions)

        content = dict(code=code, silent=silent, store_history=store_history,
                       user_expressions=user_expressions, allow_stdin=allow_stdin,
                       stop_on_error=stop_on_error)

        msg = self.session.msg('execute_request', content)
        msg_id = msg['header']['msg_id']

        reply_future = self.shell_channel.register_future(msg_id, lambda m: m.header.msg_type == 'execute_reply')
        result_future = self.iopub_channel.register_future(msg_id, lambda m: m.header.msg_type == 'execute_result')
        # todo: detect 'idle' and add predicates to determine if the future should be resolved.
        self.shell_channel.send(msg)

        # If the execute_reply we get is `error` or `abort`, we need to cancel/exception
        # the future awaiting the execute_request (because it's never happening...)
        def reply_done_callback(_reply_future):
            # noinspection PyBroadException
            try:
                reply = _reply_future.result()
                if reply.content['status'] == 'error':
                    exn = ExecuteError(name=reply.content['ename'],
                                       value=reply.content['evalue'],
                                       traceback=reply.content['traceback'])

                    result_future.set_exception(exn)
                if reply.content['status'] == 'abort':
                    result_future.set_exception(ExecuteAbort())
            except Exception:
                # todo this probably isn't quite right...
                result_future.set_exception(ExecuteAbort())

        # todo: handle `stream` reply (for functions returning unit)
        # todo: handle `status: idle` reply.

        reply_future.add_done_callback(reply_done_callback)

        return result_future
