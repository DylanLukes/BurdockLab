import uuid
from typing import Dict

from jupyter_client import KernelManager


class BurdockManager:
    """
    A manager which keeps track of a single instance of Burdock and its
    associated kernel.
    """
    kernel_manager: KernelManager

    def __init__(self, kernel_manager: KernelManager):
        self.kernel_manager = kernel_manager

    def _ensure_agent(self):
        """
        Check if a BurdockAgent is installed in the kernel, and if not,
        install one.
        """
        pass


class BurdockRootManager:
    """
    A manager which keeps track of all extant BurdockManagers and their
    associated kernel managers.
    """
    burdock_managers: Dict[str, BurdockManager]

    def __init__(self):
        self.burdock_managers = dict()
