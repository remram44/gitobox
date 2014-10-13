from __future__ import unicode_literals

import logging
import os
from rpaths import Path
import subprocess
import sys
import tarfile


def decode_utf8(s):
    if isinstance(s, bytes):
        return s.decode('utf-8', 'replace')
    else:
        return s


def repr_cmdline(cmd):
    return ' '.join(decode_utf8(s) for s in cmd)


class GitRepository(object):
    def __init__(self, repo, workdir, branch):
        if not (repo / 'objects').is_dir() or not (repo / 'refs').is_dir():
            logging.critical("Not a Git repository: %s", repo)
            sys.exit(1)

        self.repo = repo.absolute()
        self.workdir = workdir.absolute()
        self.branch = branch
        self._git = ['git', '--git-dir', self.repo.path,
                     '--work-tree', self.workdir.path]

        self._run(['config', 'receive.denyCurrentBranch', 'ignore'])

    def _run(self, cmd, allow_fail=False, stdout=False):
        logging.debug("Running: %s", repr_cmdline(['git'] + cmd))
        cmd = self._git + cmd

        if allow_fail:
            return subprocess.call(cmd)
        elif stdout:
            return subprocess.check_output(cmd)
        else:
            return subprocess.check_call(cmd)

    def has_changes(self):
        """Determines whether the working copy has changes.
        """
        self._run(['symbolic-ref', 'HEAD', 'refs/heads/%s' % self.branch])
        self._run(['add', '.'])
        status = self._run(['status', '--porcelain'], stdout=True)
        return bool(status.strip())

    def check_in(self, paths=None):
        """Commit changes to the given files (if there are differences).

        If `paths` is None, assumes that any file might have changed.
        """
        self._run(['symbolic-ref', 'HEAD', 'refs/heads/%s' % self.branch])

        self._run(['add', '.'])
        ret = self._run(['commit', '-m', '(gitobox automatic commit)'],
                        allow_fail=True)

        if ret == 0:
            ref = self._run(['rev-parse', 'HEAD'], stdout=True)
            logging.info("Created revision %s", ref.decode('ascii'))
        else:
            logging.info("No revision created")

    def check_out(self, ref):
        """Check out the given revision.
        """
        fd, temptar = Path.tempfile()
        os.close(fd)
        try:
            self._run(['symbolic-ref', 'HEAD', 'refs/heads/%s' % self.branch])

            # Creates an archive from the tree
            self._run(['archive', '--format=tar', '-o', temptar.path, ref])
            tar = tarfile.open(str(temptar), 'r')

            # List the files in the tree
            files = set(self.workdir / m.name
                        for m in tar.getmembers())

            # Remove from the directory all the files that don't exist
            removed_files = False
            for path in self.workdir.recursedir(top_down=False):
                if path.is_file() and path not in files:
                    logging.info("Removing file %s", path)
                    path.remove()
                    removed_files = True
                elif path.is_dir():
                    if not path.listdir() and removed_files:
                        logging.info("Removing empty directory %s", path)
                        path.rmdir()
                    removed_files = False

            # Replace all the files
            tar.extractall(self.workdir.path)

            tar.close()
        finally:
            temptar.remove()
