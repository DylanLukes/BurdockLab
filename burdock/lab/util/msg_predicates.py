from burdock.lab.message import Message


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