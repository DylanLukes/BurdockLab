import asyncio
from asyncio import Event, Queue
from typing import Any, TypeVar, Generic

T = TypeVar('T')


class FiniteQueue(Queue, Generic[T]):
    """
    A queue intended to have a finite (but unknown) number of elements
    placed on it. A FiniteQueue has a unique "sentinel" object. When
    this element is enqueued (using the close method), the queue should
    not have anything else placed on it, and is "closed".
    """
    closed: Event
    sentinel: Any

    def __init__(self):
        super().__init__()
        self.closed = Event()
        self.sentinel = object()

    async def close(self):
        await self.put(self.sentinel)

    def close_nowait(self):
        self.put_nowait(self.sentinel)

    async def put(self, item):
        if self.closed.is_set():
            raise RuntimeError("Attempted to put onto closed FiniteQueue.")

        await super().put(item)
        if item == self.sentinel:
            self.closed.set()

    def put_nowait(self, item):
        if self.closed.is_set():
            raise RuntimeError("Attempted to put onto closed FiniteQueue.")

        super().put_nowait(item)
        if item == self.sentinel:
            self.closed.set()

    async def get(self) -> T:
        if self.closed.is_set() and self.empty():
            raise RuntimeError("Attempted to put onto closed and empty FiniteQueue.")

        return await super().get()

    def get_nowait(self) -> T:
        if self.closed.is_set() and self.empty():
            raise RuntimeError("Attempted to put onto closed and empty FiniteQueue.")

        return super().get_nowait()

    async def join(self):
        # Default behavior is to await 0 remaining tasks.
        # We additionally also wait until the closed event is set.
        await asyncio.wait([
            super().join(), self.closed.wait()
        ])
