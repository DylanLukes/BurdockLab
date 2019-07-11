from asyncio import Future
from typing import Dict, Awaitable, Tuple

from ipython_genutils.py3compat import string_types
from jupyter_client import KernelManager
from jupyter_client.client import validate_string_dict
from jupyter_client.session import Session
from jupyter_client.threaded import ThreadedZMQSocketChannel, ThreadedKernelClient
from tornado.platform.asyncio import BaseAsyncIOLoop
from traitlets import Type
from zmq import Socket
from zmq.eventloop.zmqstream import ZMQStream


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

    def call_handlers(self, msg):
        # pprint.pprint(msg, indent=4)  # for debugging

        request_id = msg['parent_header']['msg_id']
        reply_msg_type = msg['header']['msg_type']

        if (request_id, reply_msg_type) in self.reply_futures:
            reply_future = self.reply_futures[(request_id, reply_msg_type)]
            reply_future.set_result(msg)


class BurdockKernelClient(ThreadedKernelClient):
    iopub_channel_class = Type(BurdockChannel)
    shell_channel_class = Type(BurdockChannel)
    stdin_channel_class = Type(BurdockChannel)

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

    async def request_execute(self, code, silent=False, store_history=True,
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

        result_future = self.iopub_channel.register_future(msg_id, 'execute_result')
        self.shell_channel.send(msg)

        # todo: handle checking if execute_reply is OK

        return await result_future
