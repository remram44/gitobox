"""Logic for handling Git repositories.

Contains the :class:`~gitobox.git.GitRepository` class.
"""

from __future__ import unicode_literals

import logging
import os
import pkg_resources
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


def shell_quote(s):
    """Given bl"a, returns "bl\\"a".

    Returns bytes.
    """
    if not isinstance(s, bytes):
        s = s.encode('utf-8')
    if any(c in s for c in b' \t\n\r\x0b\x0c*$\\"\''):
        return b'"' + (s.replace(b'\\', b'\\\\')
                        .replace(b'"', b'\\"')
                        .replace(b'$', b'\\$')) + b'"'
    else:
        return s


class GitRepository(object):
    def __init__(self, repo, workdir, branch, password, port):
        if not (repo / 'objects').is_dir() or not (repo / 'refs').is_dir():
            logging.critical("Not a Git repository: %s", repo)
            sys.exit(1)

        self.repo = repo.absolute()
        self.workdir = workdir.absolute()
        self.branch = branch
        self._git = ['git', '--git-dir', self.repo.path,
                     '--work-tree', self.workdir.path]

        self._run(['config', 'receive.denyCurrentBranch', 'ignore'])

        # Installs hook
        update_hook = self.repo / 'hooks' / 'update'
        if update_hook.exists():
            with update_hook.open('rb') as fp:
                line = fp.readline().rstrip()
                if line.startswith(b'#!'):
                    line = fp.readline().rstrip()
                if line != b'# Gitobox hook: do not edit!':
                    logging.critical("Repository at %s already has an update "
                                     "hook; not overriding!\n"
                                     "Please delete it and try again\n",
                                     self.repo)
                    sys.exit(1)
                else:
                    logging.debug("Replacing update hook")
        else:
            logging.debug("Installing update hook")
        template = pkg_resources.resource_stream('gitobox', 'hooks/update')
        with update_hook.open('wb') as fp:
            for line in template:
                if line.find(b'{{') != -1:
                    line = (line
                            .replace(b'{{PASSWORD}}', shell_quote(password))
                            .replace(b'{{PORT}}', shell_quote(str(port)))
                            .replace(b'{{BRANCH}}', shell_quote(branch)))
                fp.write(line)
        template.close()
        update_hook.chmod(0o755)

    def _run(self, cmd, allow_fail=False, stdout=False):
        logging.debug("Running: %s", repr_cmdline(['git'] + cmd))
        cmd = self._git + cmd

        if allow_fail:
            return subprocess.call(cmd)
        elif stdout:
            return subprocess.check_output(cmd)
        else:
            return subprocess.check_call(cmd)

    def has_changes(self, ref):
        """Determines whether the working copy has changes, compared to `ref`.
        """
        self._run(['update-ref', '--no-deref', 'HEAD', ref])
        self._run(['add', '--all', '.'])
        status = self._run(['status', '--porcelain'], stdout=True)
        self._run(['symbolic-ref', 'HEAD', 'refs/heads/%s' % self.branch])
        return bool(status.strip())

    def check_in(self, paths=None):
        """Commit changes to the given files (if there are differences).

        If `paths` is None, assumes that any file might have changed.
        """
        self._run(['symbolic-ref', 'HEAD', 'refs/heads/%s' % self.branch])

        self._run(['add', '--all', '.'])
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
            tar.extractall(str(self.workdir))

            tar.close()
        finally:
            temptar.remove()
