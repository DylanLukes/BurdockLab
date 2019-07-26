from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class MessageHeader:
    raw: dict

    msg_id: str = field(init=False)
    msg_type: str = field(init=False)
    username: str = field(init=False)
    session: str = field(init=False)
    date: datetime = field(init=False)
    version: str = field(init=False)

    def __post_init__(self):
        self.msg_id = self.raw['msg_id']
        self.msg_type = self.raw['msg_type']
        self.username = self.raw['username']
        self.session = self.raw['session']
        if not isinstance(self.raw['date'], datetime):
            self.date = datetime.fromisoformat(self.raw['date'])
        else:
            self.date = self.raw['date']
        self.version = self.raw['version']


@dataclass
class Message:
    raw: dict

    header: MessageHeader = field(init=False)
    parent_header: Optional[MessageHeader] = field(init=False)

    metadata: dict = field(init=False)
    content: dict = field(init=False)
    buffers: list = field(init=False)

    def __post_init__(self):
        raw = self.raw

        self.header = MessageHeader(raw['header'])

        self.parent_header = None
        if 'parent_header' in self.raw:
            raw_parent_header = self.raw['parent_header']
            if raw_parent_header:
                self.parent_header = MessageHeader(raw_parent_header)

        self.metadata = raw.get('metadata', {})
        self.content = raw.get('content', {})
        self.buffers = raw.get('buffers', [])
