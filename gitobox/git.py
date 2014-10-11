import logging
import subprocess


def decode_utf8(s):
    if isinstance(s, unicode):
        return s
    else:
        return s.decode('utf-8', 'replace')


def repr_cmdline(cmd):
    return ' '.join(decode_utf8(s) for s in cmd)


class GitRepository(object):
    def __init__(self, repo, workdir, branch):
        self.repo = repo.absolute()
        self.workdir = workdir.absolute()
        self.branch = branch
        self._git = ['git', '--git-dir', self.repo.path,
                     '--work-tree', self.workdir.path]

        cmd = self._git + ['symbolic-ref', 'HEAD', 'refs/heads/%s' % branch]
        logging.debug("Running: %s", repr_cmdline(cmd))
        subprocess.check_call(cmd)

        cmd = self._git + ['config', 'receive.denyCurrentBranch', 'ignore']
        logging.debug("Running: %s", repr_cmdline(cmd))
        subprocess.check_call(cmd)

    def check_in(self, paths=None):
        """Commit changes to the given files (if there are differences).

        If `paths` is None, assumes that any file might have changed.
        """
        cmd = (self._git + ['add'] +
               (['.'] if paths is None
                else [p.path for p in paths]))
        logging.debug("Running: %s", repr_cmdline(cmd))
        subprocess.check_call(cmd, cwd=self.workdir.path)

        cmd = self._git + ['commit', '-m', '(gitobox automatic commit)']
        logging.debug("Running: %s", repr_cmdline(cmd))
        ret = subprocess.call(cmd)

        cmd = self._git + ['rev-parse', 'HEAD']
        logging.debug("Running: %s", repr_cmdline(cmd))
        ref = subprocess.check_output(cmd).strip()

        if ret == 0:
            logging.info("Created revision %s", ref.decode('ascii'))
        else:
            logging.info("No revision created, still at %s",
                         ref.decode('ascii'))

    def check_out(self, ref):
        """Check out the given revision.
        """
        # TODO : Delete missing files
        # TODO : Check out other files
