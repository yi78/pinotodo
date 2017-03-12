# Pino ToDo
Pino ToDo is a To-Do list written in Python. It runs in the console.

## Commands
_legend: {required} [optional]_

* **quit** 	exit the program _(aliases: q, exit, bye)_
* **Q**	exit the program without asking for confirmation
* **add [-!] {str}**	adds a task to the list with str as its description. If the -! parameter is provided, the task will be marked as critical (i.e. will display a ! mark) _(aliases: a)_
* **delete {id}**	deletes the task. ID is the number shown on the left _(aliases: d, del, -)_
* **edit {id} {str}** replaces the description of the task {id} with {str}. _(alias: e)_
* **complete {id}**	mark a task as completed. Does not delete the task, just marks it with a x. _(aliases: c, x, com, markcomplete)_
* **markcritical {id}**	toggles the "!" mark of a task (aliases: !, markcritical, critical, cri)
* **sort**	sorts the tasks by ID
* **set [setting][=value]**	change settings (e.g. '_set show_completed=False_') or display settings with their values if called without arguments. If [value]is not specified, then returns the value of [setting]. If both [setting] and [value] are not specified, lists all settings with their set values.
* **dbfile [file name]** if [file name] is not specified, returns the name of the file where the database will be read from and written to (without .json extension). Otherwise, sets the database file name to [file name].json.
* **dwipe**	discards all tasks, no questions asked
* **dminid**	sets the next new task ID to the lowest unused possibility. For example, if you added tasks 0, 1 and 2, the next ID will normally be 3 even if you delete the others. But if you delete 1, for example, this command will set the next ID to 1.
* **debug**	does nothing

	Note: the commands complete, delete and markcritical accept multiple IDs at once by providing them separated by commas, for example: 1,2,3
