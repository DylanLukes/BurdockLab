from jupyter_client import KernelManager
from jupyter_client.threaded import ThreadedKernelClient
from traitlets import Type

from burdock.lab.message import Message
from burdock.lab.util.channels import MessagePredicate, PubSubAsyncChannel, DealerRouterAsyncChannel
from burdock.lab.errors.kernel import ExecuteError, ExecuteAbort
from burdock.lab.util.finite_queue import FiniteQueue


class BurdockKernelClient(ThreadedKernelClient):
    iopub_channel_class = Type(PubSubAsyncChannel)
    shell_channel_class = Type(DealerRouterAsyncChannel)
    stdin_channel_class = Type(DealerRouterAsyncChannel)

    # Typing hints to enhance IDE support.
    iopub_channel: PubSubAsyncChannel
    shell_channel: DealerRouterAsyncChannel
    stdin_channel: DealerRouterAsyncChannel

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

    def execute_output(self, code,
                       filter_pred: MessagePredicate = None,
                       close_pred: MessagePredicate = None,
                       *args, **kwargs) -> FiniteQueue:
        """
        Similar to KernelClient.execute, but with asynchronous goodness.
        This is intended only for shell channel request/reply style messages.
        """

        raw_msg, reply_future = self.shell_channel.prepare_request(code, self.session, *args, **kwargs)
        msg_id = raw_msg['header']['msg_id']
        queue = self.iopub_channel.register_queue(msg_id, filter_pred, close_pred)
        self.shell_channel.send(raw_msg)

        return queue

    async def execute_retval(self, code, *args, **kwargs) -> Message:
        """
        Similar to KernelClient.execute, but returns a Future for the execution result.
        This is intended only for shell channel request/reply style messages.
        """

        raw_msg, reply_future = self.shell_channel.prepare_request(code, self.session, *args, **kwargs)
        msg_id = raw_msg['header']['msg_id']
        result_future = self.iopub_channel.result(msg_id)
        self.shell_channel.send(raw_msg)

        reply = await reply_future

        if reply.content['status'] == 'error':
            result_future.set_exception(ExecuteError(
                name=reply.content['ename'],
                value=reply.content['evalue'],
                traceback=reply.content['traceback']
            ))

        if reply.content['status'] == 'abort':
            result_future.set_exception(ExecuteAbort())

        return await result_future
