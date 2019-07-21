from asyncio import Future
from typing import Dict, Tuple

from ipython_genutils.py3compat import string_types
from jupyter_client import KernelManager
from jupyter_client.client import validate_string_dict
from jupyter_client.session import Session
from jupyter_client.threaded import ThreadedZMQSocketChannel, ThreadedKernelClient
from tornado.platform.asyncio import BaseAsyncIOLoop
from traitlets import Type
from zmq import Socket
from zmq.eventloop.zmqstream import ZMQStream

from burdock.lab.errors.kernel import ExecuteError, ExecuteAbort


class BurdockChannel(ThreadedZMQSocketChannel):
    session: Session
    socket: Socket
    ioloop: BaseAsyncIOLoop
    stream: ZMQStream

    reply_futures: Dict[Tuple[str, str], Future]

    def __init__(self, socket, session, loop):
        super().__init__(socket, session, loop)
        self.reply_futures = dict()

    def register_future(self, request_id, msg_type) -> Future:
        future = Future()

        def cleanup_future(_future):
            self.unregister_future(request_id, msg_type)

        future.add_done_callback(cleanup_future)

        self.reply_futures[(request_id, msg_type)] = future
        return future

    def unregister_future(self, request_id, msg_type):
        del self.reply_futures[(request_id, msg_type)]

    def call_handlers(self, msg: dict):
        # pprint.pprint(msg, indent=4)  # for debugging
        header = msg.get('header', None)
        parent_header = msg.get('parent_header', None)

        if not (header and parent_header):
            return

        request_id = parent_header['msg_id']
        reply_msg_type = header['msg_type']

        if (request_id, reply_msg_type) in self.reply_futures:
            reply_future = self.reply_futures[(request_id, reply_msg_type)]
            reply_future.set_result(msg)


class BurdockKernelClient(ThreadedKernelClient):
    iopub_channel_class = Type(BurdockChannel)
    shell_channel_class = Type(BurdockChannel)
    stdin_channel_class = Type(BurdockChannel)

    # Typing hints to enhance IDE support.
    iopub_channel: BurdockChannel
    shell_channel: BurdockChannel
    stdin_channel: BurdockChannel

    @staticmethod
    def make(km: KernelManager, **kwargs) -> 'BurdockKernelClient':
        kw = {}
        kw.update(km.get_connection_info(session=True))
        kw.update(dict(
            connection_file=km.connection_file,
            parent=km,
        ))

        # add kwargs last, for manual overrides
        kw.update(kwargs)
        return BurdockKernelClient(**kw)

    async def execute_async(self, code, silent=False, store_history=True,
                            user_expressions=None, allow_stdin=None, stop_on_error=True):
        """
        Similar to KernelClient.execute, but with asynchronous goodness.
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

        reply_future = self.shell_channel.register_future(msg_id, 'execute_reply')
        result_future = self.iopub_channel.register_future(msg_id, 'execute_result')
        self.shell_channel.send(msg)

        # If the execute_reply we get is `error` or `abort`, we need to cancel/exception
        # the future awaiting the execute_request (because it's never happening...)
        def reply_done_callback(_reply_future):
            # noinspection PyBroadException
            try:
                reply = _reply_future.result()
                if reply['content']['status'] == 'error':
                    exn = ExecuteError(name=reply['content']['ename'],
                                       value=reply['content']['evalue'],
                                       traceback=reply['content']['traceback'])

                    result_future.set_exception(exn)
                if reply['content']['status'] == 'abort':
                    result_future.set_exception(ExecuteAbort())
            except Exception:
                # todo this probably isn't quite right...
                result_future.set_exception(ExecuteAbort())

        reply_future.add_done_callback(reply_done_callback)

        return await result_future
