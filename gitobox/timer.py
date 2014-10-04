from __future__ import unicode_literals

from threading import Condition, Thread

from gitobox.utils import irange


class ResettableTimer(object):
    """Calls a function a specified number of seconds after the last start().
    """
    IDLE, RESET, PRIMED = irange(3)

    def __init__(self, timeout, function, args=[], kwargs={}):
        self.thread = Thread(target=self._run)
        self.thread.setDaemon(True)
        self.timeout = timeout

        self.function = function
        self.args = args
        self.kwargs = kwargs

        # Only start the thread on the first start()
        self.started = False

        # This protects self.status and is used to wake up self._run()
        self.cond = Condition()
        self.status = ResettableTimer.IDLE

    def start(self):
        """Starts or restarts the countdown.
        """
        with self.cond:
            if self.started:
                self.status = ResettableTimer.RESET
                self.cond.notifyAll()
            else:
                # Go to PRIMED directly, saves self._run() a loop
                self.status = ResettableTimer.PRIMED
                self.started = True
                self.thread.start()

    def cancel(self):
        """Cancels the countdown without calling back.
        """
        with self.cond:
            if self.status != ResettableTimer.IDLE:
                self.status = ResettableTimer.IDLE
                self.cond.notifyAll()

    def _run(self):
        with self.cond:
            while True:
                if self.status == ResettableTimer.PRIMED:
                    self.cond.wait(self.timeout)
                else:
                    self.cond.wait()

                # RESET: go to prime and start counting again
                if self.status == ResettableTimer.RESET:
                    self.status = ResettableTimer.PRIMED
                # Still PRIMED: we timed out without interruption, call back
                elif self.status == ResettableTimer.PRIMED:
                    self.function(*self.args, **self.kwargs)
                    self.status = ResettableTimer.IDLE
