import os, json, shutil, time

class PinoToDo:
	db = dict() # Tasks database
	dbschema = { # Database metadata
		'autoincr': None # next available id
	}
	termsize = (80,24) # Viewport size
	linesleft = 0 # vertical space left in number of lines
	vbuffer = list()
	dispstatus = list()


	theme_lines = ("=","-",".") # indexes represent levels, 0 being the highest
	def __init__(s):
		s.flow()
		pass

#M#
	# Loads database file
	def fileload(s,filename="tasks.json"):
		try:
			with open(filename,"r") as f:
				s.db,s.dbschema = json.load(f)
				#s.vstatusset(s.vstr('ok_file_load'))
			return True
		except:
			if len(s.db) == 0:
				with open(filename,"w") as f:
					s.db = dict()
					s.dbschema = {'autoincr': 0}
					json.dump([s.db,s.dbschema],f)
					s.vstatusset(s.vstr('ok_file_createnew'))
				return True
		s.vstatusset(s.vstr('er_file_load'))

		return False

	# Stores database file
	def filewrite(s,db,filename="tasks.json"):
		try:
			with open(filename,"w") as f:
				json.dump([s.db,s.dbschema],f)
				#s.vstatusset(s.vstr('ok_file_write'))
		except:
			s.vstatusset(s.vstr('er_file_write'))
		return None

	# Adds a new task
	def tasknew(s,text='',args=[]):
		if len(text) == 0:
			s.vstatusset(s.vstr('er_task_noadd_emptystr'))
			return False
		taskid = str(s.allocid())
		s.vstatusset("Args: %s" % str(args))
		critical = 1 if '!' in args else 0
		created = time.time()
		completed = 0 # zero means not marked as completed
		s.db[taskid] = [created,completed,critical,text]
		s.vstatusset(s.vstr('ok_task_added_s') % taskid)
		return taskid

	# Deletes a task by its ID
	def taskdel(s,taskid):
		try:
			del s.db[taskid]
			return True
		except:
			return False

	# Toggles complete status between 0 (not completed) and .time() (completed)
	def tasktogglecomplete(s,taskid):
			try:
				if s.db[taskid][1] == 0:
					s.db[taskid][1] = time.time()
					s.vstatusset(s.vstr("ok_task_markcomplete_s") % taskid)
				else:
					s.db[taskid][1] = 0
					s.vstatusset(s.vstr("ok_task_marknew_s") % taskid)
				return True
			except:
				s.vstatusset(s.vstr('er_invalid_id_s') % taskid)

	# Toggles critical (!) status
	def tasktogglecrit(s,taskid):
		try:
			if s.db[taskid][2] == 0:
				s.db[taskid][2] = 1
				s.vstatusset(s.vstr("ok_task_markcrit_s") % taskid)
			else:
				s.db[taskid][2] = 0
				s.vstatusset(s.vstr("ok_task_marknocrit_s") % taskid)
		except:
			s.vstatusset(s.vstr('er_invalid_id_s') % taskid)

	# Sets auto-increment value to smallest available index (NOT the highest)
	def autoincr_setfirstempty(s):
		tryval = 0
		for i in range(len(s.db)+1):
			if str(tryval) in s.db:
				tryval += 1
				continue
			else:
				s.dbschema['autoincr'] = tryval
				s.vstatusset(s.vstr('autoincr_set_s') % tryval)
				break
		return tryval

	# returns the next available ID based on s.dbschema['autoincr'] value
	def allocid(s):
		if str(s.dbschema['autoincr']) not in s.db:
			ret = s.dbschema['autoincr']
			s.dbschema['autoincr'] += 1
		else:
			while True:
				if str(s.dbschema['autoincr']) in s.db:
					s.dbschema['autoincr'] += 1
					continue
				else:
					ret = s.dbschema['autoincr']
					s.dbschema['autoincr'] += 1
					break
		if type(ret) != int: raise Exception('Hole in the loop!')
		else: return ret

	def reorder(s):
		dbsorted = dict()
		for key in sorted([int(x) for x in s.db]):
			dbsorted[str(key)] = s.db[str(key)]
		print(dbsorted)
		s.db = dbsorted
		return True

#V#
	# defines the terminal size
	def termsizeset(s,width=0, height=0): #DONE
		if width > 0 and height > 0:
			w, h = width, height
			s.termsize = (w,h)
		else:
			s.termsize = shutil.get_terminal_size((80,24))[:]
		return s.termsize

	# Returns number of empty lines or subtract from current number
	def linesleftset(s,lines=0): # DONE
		if   lines == 0: pass
		elif lines <  0: s.linesleft += lines
		elif lines >  0: s.linesleft  = lines
		return s.linesleft

	# Clears the screen
	# TODO: make screen clearing cross-platform
	def cls(s): os.system("cls")

	# Retrieves string for display
	def vstr(s,index=None,pre="",pos=""):
		return pre+s.dialogues[index]+pos if index in s.dialogues else "???"

	# Builds a horizontal line
	# For blank line, style=" "
	# IDEA: fill argument; fills all empty space with blank lines
	def vhline(s,style=None,width=None,count=1):
		vis = s.theme_lines[0] # Fallback
		theline = "" # Fallback

		if   type(style) == str: vis = style
		elif type(style) == int: vis = s.theme_lines[style]

		if width == None: width = s.termsize[0] # defaults to full width

		theline = (vis*int((width/len(vis))+1))[:width]

		s.linesleftset(-count)
		return "\n".join([theline]*count)

	# Title panel
	def vtitle(s,modtitle=""):
		output=""
		output += ' '+s.vstr("program_title")+"\n" if len(modtitle)==0 else modtitle+"\n"
		output += ' '+s.vhline(style=2,width=len(output)-2)
		s.linesleftset(-2)
		return output

	# Status bar
	def vstatusbar(s):
		#s.linesleftset(-len(s.dispstatus)) # set by vstatusset()
		for k,v in enumerate(s.dispstatus):
			s.dispstatus[k] = v.rjust(s.termsize[0])
		ret = "\n".join(s.dispstatus) if len(s.dispstatus) > 0 else None
		s.dispstatus = list()
		return ret

	# Adds a string to be displayed in the status bar
	def vstatusset(s,msg):
		s.dispstatus += [msg]
		linecount = s.linesleftset(-(msg.count("\n")+1))
		return linecount

	# Display list of tasks
	def vtasklist(s):
		hspaceleft = s.termsize[0]
		limit = s.linesleft
		lines = 0
		display = []
		line = ''

		#idcolalign = len(str(max(s.db))) if len(s.db) > 0 else 1

		for key in s.db:
			if limit <= 0: break
			print (s.db[key])
			line += ' ' # left margin
			line += key.rjust(4)
			line += '![' if s.db[key][2] != 0 else ' [' # Critical '!' or not ' '
			line += 'x] ' if s.db[key][1] > 0 else ' ] ' # Marked completed or not
			line += s.db[key][3][:s.termsize[0]-len(line)]
			display += [line]
			line = ''
			s.linesleftset(-1)
			limit -= 1
		return "\n".join(display)
	# Command prompt
	# TODO: Way of preparing before actual prompt
	def vprompt(s,altprompt="",preorder=False):
		promptstr = altprompt if len(altprompt) > 0 else s.vstr("prompt")
		s.linesleftset(-1) # tecnhically this should zero s.linesleft
		return input(promptstr)

	# adds text to the buffer; returns number of lines added
	# IDEA: add "repeat" parameter; buffers the same string #repeat times
	# IDEA: automatic line break; prevents overflowing and counts extra line
	def vbuffer_add(s,*inputs):
		totallines = 0
		for key, item in enumerate(inputs):
			#inputstr[key]= item[0].strip()
			s.vbuffer += (item,)
			totallines += item.count("\n")+1
		return totallines

	# outputs the buffer [and clears it by default]
	# IDEA: make smart display; called last and automatically fills all space
	def vbuffer_dump(s,clear=True):
		for piece in s.vbuffer:
			if type(piece[0]) != str: continue
			print(piece[0],end="\n")
		if clear == True: s.vbuffer_clear()
		return True

	# Resets the buffer
	# IDEA: is PinoToDo passed by reference or value?
	def vbuffer_clear(s): s.vbuffer = list()

#C#
	def flow(s):
		command = ''
		while command[:1] != 'y':
			while command not in ('q','quit','exit','bye','Q'):
				s.termsizeset()
				s.vbuffer_clear()
				s.cls()
				s.linesleftset(s.termsize[1]-1)
				s.fileload()
				s.parsecmd(command)
				s.filewrite(s.db)
				#s.linesleftset(-1) # Reserve space for the footer, including divider

				s.vbuffer_add(
					# Header
					(s.vtitle(),'vtitle'),

					# Body
					(s.vtasklist(),'vtasklist'),
					(s.vhline(count=s.linesleft,width=0),'vhline'),

					# Footer starts
					(s.vhline(style='- '),'vhline'),
					#(s.vhline(width=0),'vhline') # status bar reserved space
					(s.vstatusbar(),'vstatusbar')
				)
				s.vbuffer_dump(clear=False) #should leave one empty line
				command = s.vprompt()
			s.cls()
			s.vbuffer_dump()
			if command == 'Q': command = 'y'
			command = s.vprompt('Are you sure: [y/n]')
			if command not in ['y','n'] or command == 'y':
				s.filewrite(s.db)
				s.cls()
				print(s.vstr('ok_exit'))
			elif command == 'n':
				command = ''
		pass

	# parses user command
	# rawinput: The user input
	# cmdmain: first/main part of the command (eg. add, del etc)
	# cmd: User input stripped part by part until empty
	# args: list containing the arguments preceded by "-"; can be empty
	# fstr: final argument of the command, unique, not preceded by "-"
	#       fstr can be empty
	def parsecmd(s,rawinput): # eg: User has entered 'add -! Buy food'             rawinput: 'add -! Buy food'
		args = [] # list of arguments preceded by "-"
		fstr = '' # Final part of the command -- an ID or text
		# first we try to isolate the first part of the user input
		cmd = rawinput.strip().split(' ',1) # parts of commands are separated by " "       cmd: ['add', '-! Buy food']
		# if rawinput was '', then cmd will be [''] at this point
		cmdmain = cmd[0] # main part of the command (add, delete etc)              cmdmain: 'add'
		del cmd[0] # if rawinput was '', then cmd is now []                        cmd: ['-! Buy food']

		if len(cmdmain) > 0 and cmdmain not in s.cmdaliases:
			s.vstatusset(s.vstr('er_comm_invalid_s') % cmdmain)
			return False

		# This loop splits and distributes the parts of the raw user input
		# into the appropriate variables:
		# cmdmain: The main part of the command
		# args: list of arguments (i.e. parts of the raw input preceded by "-"
		#       that don't contain spaces)
		# fstr: The final part of the command; might be the ID of the task to be
		#       manipulated, the string to be entered as task description, or an
		#       empty string if no command was inserted
		# cmd: This object continues to be sliced part by part until it becomes
		#      an empty list, representing that all the parts of the original
		#      input were already parsed
		while True:
			if len(cmd) == 0: # check for anything after the main command          cmd: ['-! Buy food']//['Buy food']//[]
				break # There was nothing apart from the main command              cmd was ['']
			elif len(cmd[0]) == 0: # probably prevented by 1st rawinput.strip()
				del cmd[0]
				break
			elif cmd[0][0] == '-': # "-" as first character so it's an argument
				cmd = cmd[0].split(' ',1) # sepparates the 1st/next argument       cmd:  ['-!', 'Buy food']
				args += [cmd[0][1:]] # first part of the split without 1st chr     args: ['!']
				del cmd[0] # eliminate first argument                              cmd:  ['Buy food']
				continue # Will try for another argument
			elif len(cmd) == 1:
				fstr = cmd[0] # fstr is to be used as task descript                fstr = 'Buy food'
				del cmd[0]
				break # Arrived at last part;
			else:
				raise Exception("Shouldn't arrive here! cmd is %s" % str(cmd))
		switch = s.cmdaliases[cmdmain]

		# Start switch
		if switch in ('','qui','qui!'):
			return True
		elif switch == 'start':
			return True
		elif switch == 'add':
			s.vstatusset(str(args))
			taskid = s.tasknew(fstr,args)
			if str(taskid) != str(False):
				s.vstatusset(s.vstr('ok_task_added_s') % taskid)
			else:
				s.vstatusset(s.vstr('er_task_noadd'))
			return True
		elif switch == 'delete':
			if len(fstr) == 0: # fstr is the task id
				s.vstatusset(s.vstr('er_invalid_id_s') % fstr)
				return False
			else:
				ret = s.taskdel(fstr)

				if ret:
					s.vstatusset(s.vstr('ok_task_deleted_s') % fstr)
				else:
					s.vstatusset(s.vstr('er_invalid_id_s')   % fstr)
				return True
		elif switch == 'markcomplete':
			ret = s.tasktogglecomplete(fstr)
			if ret != False: return True
			else: return False
		elif switch == 'markcritical':
			ret = s.tasktogglecrit(fstr)
			if ret != False: return True
			else: return False
		elif switch == 'sort':
			s.reorder()
			return True
		elif switch == 'debug':
			print(s.db)
			return True
		elif switch == 'debug_minautoincr':
			s.autoincr_setfirstempty()
			return True
		elif switch == 'debug_nextid':
			s.vstatusset("Auto-increment value: %s (not necessarily available)" % s.dbschema['autoincr'])
		elif switch == 'dwipe':
			s.db=dict()
			s.autoincr_setfirstempty()
		else:
			s.vstatusset(s.vstr('er_not_implemented')+"; switch: '%s', cmd: %s, cmdmain: %s" % (switch, cmd, cmdmain))
			return None


		pass

	dialogues = {
		"program_title": "Pino Afazer",
		"prompt": "command: ",
		"ok_exit": "Goodbye",
		"ok_task_added_s": "Task added succesfully (ID %s)",
		"er_task_noadd": "Error when adding task",
		"er_task_noadd_emptystr": "Error: Input must not be empty",
		"ok_task_markcrit_s": "Task marked as critical (ID %s)",
		"ok_task_deleted_s": "Task deleted (ID %s)",
		"ok_task_markcomplete_s": "Task marked as completed (ID %s)",
		"ok_task_marknew_s": "Task marked as new (ID %s)",
		"ok_task_marknocrit_s": "Task marked as not critical (ID %s)",
		"ok_task_markcrit_s": "Task marked as critical (ID %s)",
		"er_invalid_id_s": "Invalid ID! Received: %s",
		"er_comm_invalid_s": "Invalid command: %s",
		"er_not_implemented": "Not implemented",
		"er_processing": "Error processing command",
		"er_file_load": "Error when loading database",
		"ok_file_load": "Database loaded from file",
		"er_file_write": "Error when writing database to disk",
		"ok_file_createnew": "Starting with a blank database",
		"ok_file_write": "Database written to file",
		"autoincr_already_minimal": "Auto-increment value is already the lowest possible",
		"autoincr_set_s": "Auto-increment value set to %s"
	}
	cmdaliases = {
		# Default
		'start': 'start',
		'': 'start',
		# quit: exit comands
		'quit': 'quit',
		'q':'quit', 'exit':'quit', 'bye':'quit','Q':'quit',
		# add: Add task
		'add':'add',
		'a':'add', '+':'add',
		# delete: Delete a task
		'delete': 'delete',
		'd':'delete', 'del':'delete', '-':'delete',
		# markcomplete: Complete a task
		'complete': 'markcomplete',
		'markcomplete': 'markcomplete',
		'c': 'markcomplete', 'com': 'markcomplete', 'x': 'markcomplete',
		# markcritical: Mark as critical
		'markcritical': 'markcritical',
		'!': 'markcritical', 'cri': 'markcritical', 'critical': 'critical',
		'sort':'sort',
		# SPECIAL
		'debug':'debug', 'dminid': 'debug_minautoincr','dnid': 'debug_nextid',
		'dwipe':'dwipe'
	}
