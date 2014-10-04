from __future__ import unicode_literals

import logging
from threading import RLock, Thread

from gitobox.server import Server
from gitobox.utils import unicode_
from gitobox.watch import DirectoryWatcher


class Synchronizer(object):
    """Main application logic: synchronizes folder with Git repo.
    """
    def __init__(self, folder, repository, branchname, timeout):
        self._watcher = DirectoryWatcher(folder,
                                         self._directory_changed,
                                         timeout)
        self._hook_server = Server(5055, self._hook_triggered)
        self._lock = RLock()
        #self._repository = GitRepository(repository, branchname)

    def run(self):
        # TODO : Check that current Git tree matches directory contents

        watcher_thread = Thread(target=self._watcher.run)
        watcher_thread.setDaemon(True)
        watcher_thread.start()

        self._hook_server.run()

    def _directory_changed(self, paths):
        if self._lock.acquire(blocking=False):
            try:
                logging.warning("Paths changed: %s",
                                " ".join(unicode_(p) for p in paths))
                # TODO : Create Git commit changing these files
            finally:
                self._lock.release()

    def _hook_triggered(self, data, conn, addr):
        if data != b"notsosecret":
            logging.debug("Got invalid message on hook server from %s",
                          addr)
            conn.send(b"hook auth failed\nERROR\n")
            return
        logging.info("Hook triggered from %s", addr)
        if not self._lock.acquire(blocking=False):
            logging.info("Lock is held, failing...")
            conn.send(b"update is in progress, try again later\nERROR\n")
        else:
            try:
                conn.send(b"updating directory...\n")
                # TODO : Write files to directory
                conn.send(b"synced directory updated!\nOK\n")
                logging.info("Directory updated")
            finally:
                self._lock.release()


def synchronize(folder, repository, branchname, timeout):
    sync = Synchronizer(folder, repository, branchname, timeout)
    sync.run()
