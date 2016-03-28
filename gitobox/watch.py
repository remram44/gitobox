"""Directory-watching logic.

Contains :class:`~gitobox.watch.DirectoryWatcher`, the class that monitors the
directory for changes. Uses `pyinotify`, so it's only available on Linux.
"""

from __future__ import unicode_literals

import logging
from rpaths import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from gitobox.timer import ResettableTimer


class DirectoryWatcher(FileSystemEventHandler):
    ALL_CHANGED = None

    def __init__(self, folder, callback, lock, timeout):
        self._callback = callback

        self.observer = Observer()

        self._folder = folder
        self._changes = set()
        self.observer.schedule(self, str(folder), recursive=True)

        self._timer = ResettableTimer(timeout, self._timer_expired,
                                       lock=lock)

    def assume_all_changed(self):
        self._changes.add(DirectoryWatcher.ALL_CHANGED)
        self._timer.start()

    def run(self):
        self.observer.start()

    def _timer_expired(self):
        changes = self._changes
        self._changes = set()
        logging.info("Directory stable, syncing...")
        if DirectoryWatcher.ALL_CHANGED in changes:
            self._callback()
        else:
            self._callback(changes)

    def on_moved(self, event):
        what = 'directory' if event.is_directory else 'file'
        logging.info("Moved %s: from %s to %s", what, event.src_path,
                     event.dest_path)
        self._changes.add(event.src_path)
        self._changes.add(event.dest_path)
        self._timer.start()

    def on_created(self, event):
        what = 'directory' if event.is_directory else 'file'
        logging.info("Created %s: %s", what, event.src_path)
        self._changes.add(event.src_path)
        self._timer.start()

    def on_deleted(self, event):
        what = 'directory' if event.is_directory else 'file'
        logging.info("Deleted %s: %s", what, event.src_path)
        self._changes.add(event.src_path)
        self._timer.start()

    def on_modified(self, event):
        what = 'directory' if event.is_directory else 'file'
        logging.info("Modified %s: %s", what, event.src_path)
        self._changes.add(event.src_path)
        self._timer.start()
