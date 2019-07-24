from asyncio import Future, Queue
from typing import Callable, Dict, Tuple, Optional

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

Message = dict

MessagePredicate = Callable[[Message], bool]


def filter_none(_msg: Message) -> bool:
    return True


def filter_stdout(msg: Message) -> bool:
    try:
        return msg['msg_type'] == 'stream' \
               and msg['content']['name'] == 'stdout'
    except KeyError as e:
        return False


def filter_stderr(msg: Message) -> bool:
    try:
        return msg['msg_type'] == 'stream' \
               and msg['content']['name'] == 'stderr'
    except KeyError as e:
        return False


def on_execution_idle(msg: Message) -> bool:
    try:
        return msg['msg_type'] == 'status' \
               and msg['content']['execution_state'] == 'idle'
    except KeyError as e:
        return False


class BurdockChannel(ThreadedZMQSocketChannel):
    session: Session
    socket: Socket
    ioloop: BaseAsyncIOLoop
    stream: ZMQStream

    # A channel can await a response of a certain message.
    _recv_futures: Dict[Tuple[str, str], Future]

    # A chanenl can stream (enqueue) all messages of a type until a condition.
    # (e.g. execution state = idle)
    # Value = (queue,
    _recv_queues: Dict[str, Tuple[Queue, MessagePredicate, MessagePredicate]]

    def __init__(self, socket, session, loop):
        super().__init__(socket, session, loop)
        self._recv_futures = dict()
        self._recv_queues = dict()

    def register_future(self, request_id: str, msg_type: str) -> Future:
        key = (request_id, msg_type)
        future = Future()

        def cleanup_future(_future):
            self.unregister_future(*key)

        future.add_done_callback(cleanup_future)

        self._recv_futures[key] = future
        return future

    def unregister_future(self, request_id: str, msg_type: str):
        key = (request_id, msg_type)

        del self._recv_futures[key]

    def register_stream(self,
                        request_id: str,
                        filter_pred: MessagePredicate,
                        close_pred: MessagePredicate) -> 'Queue[Optional[Message]]':
        key = request_id
        queue = Queue()

        self._recv_queues[key] = (queue, filter_pred, close_pred)
        return queue

    def unregister_stream(self, request_id: str):
        del self._recv_queues[request_id]

    def call_handlers(self, msg: Message):
        # pprint.pprint(msg, indent=2)  # for debugging
        header = msg.get('header', None)
        parent_header = msg.get('parent_header', None)

        if not header:
            return

        def header_summary() -> str:
            if parent_header:
                return (f"IN  {header['msg_id']}:{header['msg_type']} ↩︎ "
                        f"    {parent_header['msg_id']}:{parent_header['msg_type']}")
            else:
                return f"IN  {header['msg_id']}:{header['msg_type']} ←"

        def body_summary() -> str:
            return msg['content']

        print("")
        print(header_summary())
        print(body_summary())

        if not parent_header:
            return

        request_id = parent_header['msg_id']
        reply_msg_type = header['msg_type']

        key = (request_id, reply_msg_type)

        if key in self._recv_futures:
            recv_future = self._recv_futures[key]
            recv_future.set_result(msg)

        if request_id in self._recv_queues:
            (queue, filter_pred, close_pred) = self._recv_queues[request_id]

            if filter_pred(msg):
                queue.put_nowait(msg)

            if close_pred(msg):
                queue.put_nowait(None)
                self.unregister_stream(request_id)


class BurdockKernelClient(ThreadedKernelClient):
    iopub_channel_class = Type(BurdockChannel)
    shell_channel_class = Type(BurdockChannel)
    stdin_channel_class = Type(BurdockChannel)

    # Typing hints to enhance IDE support.
    iopub_channel: BurdockChannel
    shell_channel: BurdockChannel
    stdin_channel: BurdockChannel

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
                          user_expressions=None, allow_stdin=None, stop_on_error=True,
                          ) -> 'Queue[Optional[dict]]':
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

        stream_queue = self.iopub_channel.register_stream(msg_id, filter_pred, close_pred)

        self.shell_channel.send(msg)
        print("")
        print(f"OUT {msg['header']['msg_id']}:{msg['header']['msg_type']}")

        return stream_queue

    def execute_async(self, code, silent=False, store_history=True,
                      user_expressions=None, allow_stdin=None, stop_on_error=True) -> 'Future[dict]':
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

        reply_future = self.shell_channel.register_future(msg_id, 'execute_reply')
        result_future = self.iopub_channel.register_future(msg_id, 'execute_result')
        # todo: detect 'idle' and add predicates to determine if the future should be resolved.
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

        # todo: handle `stream` reply (for functions returning unit)
        # todo: handle `status: idle` reply.

        reply_future.add_done_callback(reply_done_callback)

        return result_future
