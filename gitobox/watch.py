"""Directory-watching logic.

Contains :class:`~gitobox.watch.DirectoryWatcher`, the class that monitors the
directory for changes. Uses `pyinotify`, so it's only available on Linux.
"""

from __future__ import unicode_literals

import logging
import pyinotify
from rpaths import Path

from gitobox.timer import ResettableTimer


mask = (pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO |
        pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_CLOSE_WRITE)

manager = pyinotify.WatchManager()


class DirectoryWatcher(pyinotify.ProcessEvent):
    ALL_CHANGED = None

    def __init__(self, folder, callback, lock, timeout):
        self._callback = callback

        self.notifier = pyinotify.Notifier(manager, self)

        self._folder = folder
        self._changes = set()
        self._dirs = {}
        self._dirs[folder] = manager.add_watch(str(folder), mask)
        for path in folder.recursedir():
            if path.is_dir():
                self._dirs[path] = manager.add_watch(str(path), mask)

        self._timer = ResettableTimer(timeout, self._timer_expired,
                                       lock=lock)

    def assume_all_changed(self):
        self._changes.add(DirectoryWatcher.ALL_CHANGED)
        self._timer.start()

    def run(self):
        self.notifier.loop()

    def _timer_expired(self):
        changes = self._changes
        self._changes = set()
        logging.info("Directory stable, syncing...")
        if DirectoryWatcher.ALL_CHANGED in changes:
            self._callback()
        else:
            self._callback(changes)

    def __add(self, path, moved):
        logging.info("%s %s: %s",
                     "Directory" if path.is_dir() else "File",
                     "moved in" if moved else "created",
                     path)
        self._changes.add(path)
        if path.is_dir():
            res = manager.add_watch(str(path), mask)
            assert len(res) == 1
            wd = next(iter(res.values()))
            self._dirs[path] = wd
        self._timer.start()

    def __remove(self, path, moved):
        logging.info("%s %s: %s",
                     "Directory" if path.is_dir() else "File",
                     "moved out" if moved else "removed",
                     path)
        self._changes.add(path)
        if moved and path in self._dirs:
            wd = self._dirs.pop(path)
            manager.rm_watch(wd)
        self._timer.start()

    def __changed(self, path):
        logging.info("File changed: %s", path)
        self._changes.add(path)
        self._timer.start()

    def process_IN_CREATE(self, event):
        path = Path(event.pathname)
        self.__add(path, moved=False)

    def process_IN_MOVED_TO(self, event):
        path = Path(event.pathname)
        self.__add(path, moved=True)

    def process_IN_DELETE(self, event):
        path = Path(event.pathname)
        self.__remove(path, moved=False)

    def process_IN_MOVED_FROM(self, event):
        path = Path(event.pathname)
        self.__remove(path, moved=True)

    def process_IN_CLOSE_WRITE(self, event):
        path = Path(event.pathname)
        self.__changed(path)
