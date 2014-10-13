Gitobox
=======

This program synchronizes a DropBox directory (or any directory) with a Git repository. Any change in the directory will create a new commit on a specified branch, and a push to that branch will update the directory.

Currently, only Linux is targeted (because inotify is only available there), but more platforms can probably be added without much efforts. Of course, if collaboration between Git and DropBox users is needed, there only need to be one server translating; you don't need to run it on each client. This is why this software primarily targets servers.

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

I use ``inotify(2)``, so supporting other platforms than Linux is just a matter of providing an alternative method of watching a directory. I have no intention of doing that myself, but patches are welcome!

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
