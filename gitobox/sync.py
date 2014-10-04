from __future__ import unicode_literals

import logging

from gitobox.utils import unicode_
from gitobox.watch import DirectoryWatcher


class Synchronizer(object):
    def __init__(self, folder, repository, branchname, timeout):
        self._watcher = DirectoryWatcher(folder,
                                         self._directory_changed,
                                         timeout)
        #self._repository = GitRepository(repository, branchname)

    def run(self):
        self._watcher.run()

    def _directory_changed(self, paths):
        logging.warning("Paths changed: %s",
                        " ".join(unicode_(p) for p in paths))


def synchronize(folder, repository, branchname, timeout):
    sync = Synchronizer(folder, repository, branchname, timeout)
    sync.run()
