import logging
import pyinotify
from rpaths import Path


mask = (pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO |
        pyinotify.IN_DELETE | pyinotify.IN_CREATE)

manager = pyinotify.WatchManager()


class Synchronizer(pyinotify.ProcessEvent):
    def __init__(self, folder):
        self.__folder = folder
        self.__dirs = {}
        self.__files = {}
        self.__dirs[folder] = manager.add_watch(str(folder), mask)
        for path in folder.recursedir():
            if path.is_dir():
                self.__dirs[path] = manager.add_watch(str(path), mask)

    def __add(self, path, moved):
        logging.info("%s %s: %s",
                     "Directory" if path.is_dir() else "File",
                     "moved in" if moved else "created",
                     path)
        if path.is_dir():
            res = manager.add_watch(str(path), mask)
            assert len(res) == 1
            wd = next(iter(res.values()))
            self.__dirs[path] = wd

    def __remove(self, path, moved):
        logging.info("%s %s: %s",
                     "Directory" if path.is_dir() else "File",
                     "moved out" if moved else "removed",
                     path)
        if moved and path in self.__dirs:
            wd = self.__dirs.pop(path)
            manager.rm_watch(wd)

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


def synchronize(folder, repository, branchname):
    folder = Path(folder)
    repository = Path(repository)

    sync = Synchronizer(folder)
    notifier = pyinotify.Notifier(manager, sync)

    notifier.loop()
