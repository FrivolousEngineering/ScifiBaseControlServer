
from threading import Timer
from typing import Callable, Optional


class PerpetualTimer:
    """
    A wrapper around the python timer class that keeps executing the target each interval.
    """

    def __init__(self, interval: float, target: Callable) -> None:
        """
        A wrapper around the python timer class that keeps executing the target each interval.
        Note that it simply waits in between the executions. It will therefore *always* be slower than the interval.
        :param interval: How much seconds should be in between the calls.
        :param target: Function that needs to be called
        """
        self._should_continue = False
        self._is_running = False
        self._interval = interval
        self._target = target
        self._thread = None  # type: Optional[Timer]

    def _handleTarget(self) -> None:
        self._is_running = True
        self._target()
        self._is_running = False
        self._startTimer()

    def _startTimer(self) -> None:
        if self._should_continue:
            self._thread = Timer(self._interval, self._handleTarget)
            self._thread.start()

    def start(self) -> None:
        if not self._should_continue and not self._is_running:
            self._should_continue = True
            self._startTimer()

    def cancel(self) -> None:
        if self._thread is not None:
            self._should_continue = False
            self._thread.cancel()
