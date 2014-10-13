from __future__ import unicode_literals

import logging
from threading import Semaphore, Thread

from gitobox.git import GitRepository
from gitobox.server import Server
from gitobox.utils import unicode_, make_unique_bytestring
from gitobox.watch import DirectoryWatcher


class Synchronizer(object):
    """Main application logic: synchronizes folder with Git repo.
    """
    def __init__(self, folder, repository, branchname, timeout):
        self._lock = Semaphore(1)
        self._watcher = DirectoryWatcher(folder,
                                         self._directory_changed,
                                         self._lock,
                                         timeout)
        # Make up a random password
        self.password = make_unique_bytestring()
        self._hook_server = Server(2, self._hook_triggered)
        self._repository = GitRepository(repository, folder, branchname,
                                         self.password,
                                         self._hook_server.port)

    def run(self):
        watcher_thread = Thread(target=self._watcher.run)
        watcher_thread.setDaemon(True)
        self._watcher.assume_all_changed()
        watcher_thread.start()

        try:
            self._hook_server.run()
        except KeyboardInterrupt:
            logging.warning("Got KeyboardInterrupt, exiting...")
        except Exception:
            logging.critical("Exiting after unhandled exception!")
            raise

    def _directory_changed(self, paths=None):
        # We got called back though the ResettableTimer, so the lock is held
        if paths is None:
            logging.warning("Assuming all paths changed")
        else:
            logging.warning("Paths changed: %s",
                            " ".join(unicode_(p) for p in paths))
        self._repository.check_in(paths)

    def _hook_triggered(self, data, conn, addr):
        passwd, ref = data
        if passwd != self.password:
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
                self._repository.check_out(ref)
                conn.send(b"synced directory updated!\n")
                logging.info("Directory updated to %s",
                             ref.decode('ascii')[:7])
            finally:
                self._lock.release()

            if self._repository.has_changes(ref):
                # The lock has been released, changes now happening in DropBox
                # will start DirectoryWatcher's timer as usual.
                # However, while we were copying files from Git into the
                # directory, it might have been changed (i.e. DropBox might
                # have conflicted). In this case, a new commit will happen in a
                # few seconds
                logging.info("Conflict detected during directory update")
                self._watcher.assume_all_changed()
                # Tell the pusher about it, so he can fetch
                conn.send(b"WARNING: DROPBOX CONFLICT\n"
                          b"the directory was updated while changes were "
                          b"being written from Git to the directory; "
                          b"leave DropBox time to sync then fetch again\n")

            conn.send(b"OK\n")


def synchronize(folder, repository, branchname, timeout):
    sync = Synchronizer(folder, repository, branchname, timeout)
    sync.run()
