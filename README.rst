Gitobox
=======

This program synchronizes a DropBox directory (or any directory) with a Git repository. Any change in the directory will create a new commit on a specified branch, and a push to that branch will update the directory.

Currently, only Linux is targeted (because inotify is only available there), but more platforms can probably be added without much efforts. Of course, if collaboration between Git and DropBox users is needed, there only need to be one server translating, which is why this software primarily targets servers.
