from asyncio import Event, Future
from collections import defaultdict
from dataclasses import dataclass, field
from logging import Logger
from typing import Dict, List, Mapping, Optional, Set, Callable, Any, TypeVar, Generic

from jupyter_client.session import Session
from jupyter_client.threaded import ThreadedZMQSocketChannel
from tornado.platform.asyncio import BaseAsyncIOLoop
from zmq import Socket
from zmq.eventloop.zmqstream import ZMQStream

from burdock.lab.message import Message
from burdock.lab.util.finite_queue import FiniteQueue

MessagePredicate = Callable[[Message], bool]


@dataclass(frozen=True)
class EventRecord:
    """Represents the state for a registered event on an AsyncChannel.
       When a message for which predicate(message) comes in, the event
       is set. """
    parent_msg_id: str
    predicate: MessagePredicate
    event: Event = field(default_factory=Event)


@dataclass(frozen=True)
class FutureRecord:
    """Represents the state for a registered future on an AsyncChannel.
       When a message for which predicate(message) comes in, the future
       is resolved with the message as its value. """
    parent_msg_id: str
    predicate: MessagePredicate
    future: Future = field(default_factory=Future)


@dataclass(frozen=True)
class QueueRecord:
    """Represents the state for a registered queue on an AsyncChannel.
       When a message for which predicate(message) comes in, it is enqueued."""
    parent_msg_id: str
    predicate: MessagePredicate
    close_predicate: MessagePredicate
    queue: FiniteQueue = field(default_factory=FiniteQueue)


class AsyncChannel(ThreadedZMQSocketChannel):
    """
    Mostly identical to ThreadedZMQSocketChannel, but with some
    extra type annotations and utility methods for working with
    asyncio primitives (Futures, Queues, Events...).
    """

    session: Session
    socket: Socket
    ioloop: BaseAsyncIOLoop
    stream: ZMQStream

    # Events and futures may be registered for
    events: Dict[str, Set[EventRecord]]
    futures: Dict[str, Set[FutureRecord]]
    queues: Dict[str, Set[QueueRecord]]

    logger: Optional[Logger] = None

    def __init__(self, socket, session, loop, logger=None):
        super().__init__(socket, session, loop)
        self.events = defaultdict(set)
        self.futures = defaultdict(set)
        self.queues = defaultdict(set)
        self.logger = logger

    def register_event(self, parent_msg_id: Optional[str], predicate: MessagePredicate) -> Event:
        """Registers an event to the channel. The event is automatically removed when it is set.
           Note: None _is_ a valid parent_msg_id, namely for messages that are not in reply to anything. """
        record = EventRecord(parent_msg_id, predicate)
        self.events[parent_msg_id] |= {record}
        return record.event

    def unregister_event(self, parent_msg_id: Optional[str], event: Event):
        """Unregisters an event. This should generally not be called, unless the caller
           knows that the registered event will never fire."""
        records = self.events[parent_msg_id]
        for record in records:
            if record.event == event:
                records -= {record}

    def register_future(self, parent_msg_id: Optional[str], predicate: MessagePredicate) -> Future:
        """Registers an event to the channel. The future is automatically removed when its result is set.
           Note: None _is_ a valid parent_msg_id, namely for messages that are not in reply to anything."""
        record = FutureRecord(parent_msg_id, predicate)
        self.futures[parent_msg_id] |= {record}
        return record.future

    def unregister_future(self, parent_msg_id: str, future: Future):
        """Unregisters a a future. This should generally not be called, unless the caller
           knows that the future will never be resolved."""
        records = self.futures[parent_msg_id]
        for record in records:
            if record.future == future:
                records -= {record}

    def register_queue(self, parent_msg_id: str, predicate: MessagePredicate,
                       close_predicate: MessagePredicate) -> FiniteQueue:
        record = QueueRecord(parent_msg_id, predicate, close_predicate)
        self.queues[parent_msg_id] |= {record}
        return record.queue

    def unregister_queue(self, parent_msg_id: str, queue: FiniteQueue):
        records = self.queues[parent_msg_id]
        for record in records:
            if record.queue == queue:
                records -= {record}

    def _handle_events(self, msg: Message):
        parent_msg_id = msg.parent_header.msg_id if msg.parent_header else None

        if parent_msg_id in self.events:
            records = self.events[parent_msg_id]
            removals = set()
            for record in records:
                if record.predicate(msg):
                    record.event.set()
                    removals.add(record)
            records -= removals
            if not records:
                del self.events[parent_msg_id]

    def _handle_futures(self, msg: Message):
        parent_msg_id = msg.parent_header.msg_id if msg.parent_header else None

        if parent_msg_id in self.futures:
            records = self.futures[parent_msg_id]
            removals = set()
            for record in records:
                if record.predicate(msg):
                    record.future.set_result(msg)
                    removals.add(record)
            records -= removals
            if not records:
                del self.futures[parent_msg_id]

    def _handle_queues(self, msg: Message):
        parent_msg_id = msg.parent_header.msg_id if msg.parent_header else None

        if parent_msg_id in self.queues:
            records = self.queues[parent_msg_id]
            removals = set()
            for record in records:
                if record.predicate(msg):
                    record.queue.put_nowait(msg)

                if record.close_predicate(msg):
                    record.queue.close_nowait()
                    removals.add(record)
            records -= removals
            if not records:
                del self.queues[parent_msg_id]

    def call_handlers(self, raw_msg: dict):
        msg = Message(raw_msg)

        parent_msg_id = msg.parent_header.msg_id if msg.parent_header else None

        self._handle_events(msg)
        self._handle_futures(msg)
        self._handle_queues(msg)


class DealerRouterAsyncChannel(AsyncChannel):
    """
    Jupyter's 'shell' and 'stdin' channels are dealer-router, which is
    (roughly) an asynchronous form of request-response style communication.
    """
    pass


class PubSubAsyncChannel(AsyncChannel):
    """
    The 'iopub' channel on the other hand is pub-sub. Messages are pushed
    from the kernel and received here. Communication is mono-directional.
    """
    pass
