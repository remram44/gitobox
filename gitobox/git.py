class GitRepository(object):
    def __init__(self, repo, workdir, branch):
        self.repo = repo
        self.workdir = workdir
        self.branch = branch

    def check_in(self, paths=None):
        """Commit changes to the given files (if there are differences).

        If `paths` is None, assumes that any file might have changed.
        """
        # TODO : Commit changed files

    def check_out(self, ref):
        """Check out the given revision.
        """
        # TODO : Delete missing files
        # TODO : Check out other files
