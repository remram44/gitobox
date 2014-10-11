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

        self._run(['symbolic-ref', 'HEAD', 'refs/heads/%s' % branch])

        self._run(['config', 'receive.denyCurrentBranch', 'ignore'])

    def _run(self, cmd, allow_fail=False, stdout=False):
        cmd = self._git + cmd
        logging.debug("Running: %s", repr_cmdline(cmd))

        if allow_fail:
            return subprocess.call(cmd)
        elif stdout:
            return subprocess.check_output(cmd)
        else:
            return subprocess.check_call(cmd)

    def check_in(self, paths=None):
        """Commit changes to the given files (if there are differences).

        If `paths` is None, assumes that any file might have changed.
        """
        self._run(['add'] + (['.'] if paths is None
                             else [p.path for p in paths]))

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
        # TODO : Delete missing files
        # TODO : Check out other files
