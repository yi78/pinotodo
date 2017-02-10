# Pino ToDo
Pino ToDo is a To-Do list written in Python. It runs in the console.

## Commands
_legend: {required} [optional]_

* **quit** 	exit the program _(aliases: q, exit, bye)_
* **Q**	exit the program without asking for confirmation
* **add [-!] {str}**	adds a task to the list with str as its description. If the -! parameter is provided, the task will be marked as critical (i.e. will display a ! mark) _(aliases: a)_
* **delete {id}**	deletes the task. ID is the number shown on the left _(aliases: d, del, -)_
* **complete {id}**	mark a task as completed. Does not delete the task, just marks it with a x. _(aliases: c, x, com, markcomplete)_
* **markcritical {id}**	toggles the "!" mark of a task (aliases: !, markcritical, critical, cri)
* **sort**	sorts the tasks by ID
* **dwipe**	discards all tasks, no questions asked
* **dminid**	sets the next new task ID to the lowest unused possibility. For example, if you added tasks 0, 1 and 2, the next ID will normally be 3 even if you delete the others. But if you delete 1, for example, this command will set the next ID to 1. The next ID will be the
* **debug**	does nothing
