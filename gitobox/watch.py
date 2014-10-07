from __future__ import unicode_literals

import logging
import pyinotify
from rpaths import Path

from gitobox.timer import ResettableTimer


mask = (pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO |
        pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_CLOSE_WRITE)

manager = pyinotify.WatchManager()


class DirectoryWatcher(pyinotify.ProcessEvent):
    def __init__(self, folder, callback, lock, timeout):
        self.__callback = callback

        self.notifier = pyinotify.Notifier(manager, self)

        self.__folder = folder
        self.__dirs = {}
        self.__dirs[folder] = manager.add_watch(str(folder), mask)
        for path in folder.recursedir():
            if path.is_dir():
                self.__dirs[path] = manager.add_watch(str(path), mask)
        self.__changes = set()

        self.__timer = ResettableTimer(timeout, self._timer_expired,
                                       lock=lock)

    def run(self):
        self.notifier.loop()

    def _timer_expired(self):
        changes = self.__changes
        self.__changes = set()
        self.__callback(changes)

    def __add(self, path, moved):
        logging.info("%s %s: %s",
                     "Directory" if path.is_dir() else "File",
                     "moved in" if moved else "created",
                     path)
        self.__changes.add(path)
        if path.is_dir():
            res = manager.add_watch(str(path), mask)
            assert len(res) == 1
            wd = next(iter(res.values()))
            self.__dirs[path] = wd
        self.__timer.start()

    def __remove(self, path, moved):
        logging.info("%s %s: %s",
                     "Directory" if path.is_dir() else "File",
                     "moved out" if moved else "removed",
                     path)
        self.__changes.add(path)
        if moved and path in self.__dirs:
            wd = self.__dirs.pop(path)
            manager.rm_watch(wd)
        self.__timer.start()

    def __changed(self, path):
        logging.info("File changed: %s", path)
        self.__changes.add(path)
        self.__timer.start()

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
