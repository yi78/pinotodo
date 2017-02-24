# Pino ToDo changelog

## 2017-02-11
* **New:** Multiple tasks can be deleted, marked as completed or marked as critical by specifying multiple comma-separated ids, for example: 'delete 1,2,5' will delete tasks with ID 1, 2 and 5, while 'complete 3,6,7' will toggle the "complete" status of tasks 3, 6 and 7
* **New:** Details about a single task can be show with the 'show ID' command
* **New:** It is now possible show or hide completed tasks, and also configure them to appear on bottom and critical ones to appear on top. Type 'set' with no arguments to see a list of settings. Settings are modified like this, for example: 'set show_completed=False'
* **Fix:** Removed more debug messages
* Code workflow tweaks

## 2017-02-10
* **New:** Added Q command
* **New:** Screen clearing now works on POSIX systems
* **New:** Task list items now break to next line if width exceeds window size
* **New:** Critical tasks show on top by default
* **New:** Completed tasks show on bottom by default
* Minor layout tweaks
* **Fix:** Blank line makes total height exceed console size when all lines have content
* **Fix:** Removed duplicated messages
* **Fix:** Removed debug messages

## 2017-02-09
* Initial release
* **New:** It's usable
