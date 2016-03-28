Gitobox
=======

This program synchronizes a DropBox directory (or any directory) with a Git repository. Any change in the directory will create a new commit on a specified branch, and a push to that branch will update the directory.

Note that this is different from putting your .git folder inside your DropBox. Here, you don't have anything git-related in DropBox, Gitobox gives you a separate, 2-way-synced Git repository that you can use instead of DropBox (or just keep using DropBox and have the Git history for future reference).

Deployment Guide
----------------

First, this is intended to be deployed on some kind of server or "always on" machine. While it will work correctly in other setups, Gitobox cannot detect and record versions that happen while it is offline, so you would get a single "big commit" when synchronization resumes, making the history less useful.

Installing Gitobox is easy if you have Python and `pip <https://pip.pypa.io/>`_ installed::

    $ pip install gitobox

Simply create a Git repository that will be synced::

    $ git init dropbox-project

The automatic commits will be created with the local identity, so you might want to set that as well::

    $ pushd dropbox-project
    $ git config user.name "dropbox"
    $ git config user.email "gitobox@my-own-server"
    $ popd

then start Gitobox::

    $ gitobox ~/Dropbox/my-project dropbox-project/.git

You can then clone that repository and tada! You get to work with Git instead of Dropbox::

    $ git clone my-working-copy dropbox-project

FAQ
---

Why make Gitobox?
'''''''''''''''''

Because we all have friends/colleagues who don't know how to use Git, and sometimes you have to work with them.

Does it work?
'''''''''''''

Yes! Although not very thoroughly (and automatically?) tested yet, it does work.

Can I use something else than Linux?
''''''''''''''''''''''''''''''''''''

Yes! Through the use of `watchdog <https://github.com/gorakhargosh/watchdog>`__, all platforms should now be supported.

Can I use something else than Git?
''''''''''''''''''''''''''''''''''

Any version control system that can notify Gitobox when new changes come in should work; you just have to write a replacement for the notification, check in, and check out code. I have no intention of doing that myself, but patches are welcome!

Can I use something else than DropBox?
''''''''''''''''''''''''''''''''''''''

Yes, Gitobox has no knowledge of what DropBox is, it just watches a directory. Whether this gets changed by rsync, FTP, DropBox, Google Drive or Bittorrent Sync does not matter.

It would probably be cool to try and get metadata from the syncing system (i.e. the name of the user who made the change), but this is not written yet.

Are conflicts possible?
'''''''''''''''''''''''

Yes; this is because DropBox has no locking mechanism. The Git repository will not accept pushes while the directory is changing, and the usual "non fast-forward; pull first" behavior will happen for conflicts on the Git side. However, if somebody changes the DropBox while Git is writing to it, conflicts will happen and will be resolved by DropBox's own mechanisms. This will in turn create a new commit in Git, so you can fix that from Git (but conflicted files will be side-by-side, the DropBox way). Gitobox also tries to detect that and give you a warning when you push, so read these "remote:" messages!
