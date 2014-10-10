from __future__ import unicode_literals

import logging
from threading import Semaphore, Thread

from gitobox.server import Server
from gitobox.utils import unicode_
from gitobox.watch import DirectoryWatcher


class Synchronizer(object):
    """Main application logic: synchronizes folder with Git repo.
    """
    def __init__(self, folder, repository, branchname, timeout):
        self._lock = Semaphore(1)
        self._watcher = DirectoryWatcher(folder,
                                         self._directory_changed,
                                         self._lock,
                                         timeout,
                                         assume_changed=True)
        self._hook_server = Server(5055, 2, self._hook_triggered)
        #self._repository = GitRepository(repository, branchname)

    def run(self):
        watcher_thread = Thread(target=self._watcher.run)
        watcher_thread.setDaemon(True)
        watcher_thread.start()

        self._hook_server.run()

    def _directory_changed(self, paths=None):
        # We got called back though the ResettableTimer, so the lock is held
        if paths is None:
            logging.warning("Assuming all paths changed")
        else:
            logging.warning("Paths changed: %s",
                            " ".join(unicode_(p) for p in paths))
        # TODO : Create Git commit changing these files

    def _hook_triggered(self, data, conn, addr):
        passwd, ref = data
        if passwd != b"notsosecret":
            logging.debug("Got invalid message on hook server from %s",
                          addr)
            conn.send(b"hook auth failed\nERROR\n")
            return
        logging.info("Hook triggered from %s", addr, )
        if not self._lock.acquire(blocking=False):
            logging.info("Lock is held, failing...")
            conn.send(b"update is in progress, try again later\nERROR\n")
        else:
            try:
                conn.send(b"updating directory to %s...\n" % ref[:7])
                # TODO : Write files to directory
                conn.send(b"synced directory updated!\nOK\n")
                logging.info("Directory updated to %s",
                             ref.decode('ascii')[:7])
            finally:
                self._lock.release()


def synchronize(folder, repository, branchname, timeout):
    sync = Synchronizer(folder, repository, branchname, timeout)
    sync.run()
