from abc import ABCMeta, abstractmethod
from types import TracebackType
from typing import Callable, Coroutine, Optional, Type, TypeVar

from anyio._core._compat import DeprecatedAsyncContextManager, DeprecatedAwaitable

T_Retval = TypeVar('T_Retval')


class TaskStatus(metaclass=ABCMeta):
    @abstractmethod
    def started(self, value=None) -> None:
        """
        Signal that the task has started.

        :param value: object passed back to the starter of the task
        """


class TaskGroup(metaclass=ABCMeta):
    """
    Groups several asynchronous tasks together.

    :ivar cancel_scope: the cancel scope inherited by all child tasks
    :vartype cancel_scope: CancelScope
    """

    cancel_scope: 'CancelScope'

    @abstractmethod
    def spawn(self, func: Callable[..., Coroutine], *args, name=None) -> DeprecatedAwaitable:
        """
        Launch a new task in this task group.

        :param func: a coroutine function
        :param args: positional arguments to call the function with
        :param name: name of the task, for the purposes of introspection and debugging
        """

    @abstractmethod
    async def start(self, func: Callable[..., Coroutine], *args, name=None) -> None:
        """
        Launch a new task and wait until it signals for readiness.

        :param func: a coroutine function
        :param args: positional arguments to call the function with
        :param name: name of the task, for the purposes of introspection and debugging
        :return: the value passed to ``task_status.started()``
        :raises RuntimeError: if the task finishes without calling ``task_status.started()``

        .. versionadded:: 3.0
        """

    @abstractmethod
    async def __aenter__(self) -> 'TaskGroup':
        """Enter the task group context and allow starting new tasks."""

    @abstractmethod
    async def __aexit__(self, exc_type: Optional[Type[BaseException]],
                        exc_val: Optional[BaseException],
                        exc_tb: Optional[TracebackType]) -> Optional[bool]:
        """Exit the task group context waiting for all tasks to finish."""


class CancelScope(DeprecatedAsyncContextManager):
    @abstractmethod
    def cancel(self) -> DeprecatedAwaitable:
        """Cancel this scope immediately."""

    @property
    @abstractmethod
    def deadline(self) -> float:
        """
        The time (clock value) when this scope is cancelled automatically.

        Will be ``float('inf')`` if no timeout has been set.
        """

    @property
    @abstractmethod
    def cancel_called(self) -> bool:
        """``True`` if :meth:`cancel` has been called."""

    @property
    @abstractmethod
    def shield(self) -> bool:
        """
        ``True`` if this scope is shielded from external cancellation.

        While a scope is shielded, it will not receive cancellations from outside.
        """

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]) -> Optional[bool]:
        pass
