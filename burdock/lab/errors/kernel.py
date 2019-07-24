import abc
from dataclasses import dataclass
from typing import List


class IPythonExecuteException(Exception, abc.ABC):
    pass


@dataclass
class FancyPingFailed(IPythonExecuteException):
    output: List[str]


@dataclass
class ExecuteAbort(IPythonExecuteException):
    pass


@dataclass
class ExecuteError(IPythonExecuteException):
    name: str
    value: str
    traceback: List[str]
