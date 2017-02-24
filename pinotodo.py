import os # cls()
import sys # file handling
import json # database serializing
import shutil # terminal size
import time # task metadata
import math # ceil() to round number of lines

class PinoToDo:
	db = dict() # Tasks database
	dbschema = { # Database metadata
		'autoincr': 0 # next available id
	}
	rtset = { # Runtime settings
		'show_completed': True,
		'completed_last': True, # no effect if show_completed = False
		'critical_first': True,
	}
	termsize = (80,24) # Viewport size
	linesleft = 0 # vertical space left in number of lines
	vbuffer = list()
	dispstatus = list()

	#not yet implemented
	#lastinput = ('','',[]) # main command, final string/ID and arguments


	theme_lines = ("=","-",".") # indexes represent levels, 0 being the highest
	def __init__(s):
		s.flow()
		pass

#M#
	# Loads database file
	def fileload(s,filename="tasks.json"):
		try:
			with open(filename,"r") as f:
				tmpdbfile = json.load(f)
				if len(tmpdbfile) == 2:   s.db, s.dbschema = tmpdbfile
				elif len(tmpdbfile) == 3: s.db, s.dbschema, s.rtset = tmpdbfile
				else: raise Exception
			return True
		except:
			if len(s.db) == 0:
				with open(filename,"w") as f:
					s.db = dict(PinoToDo.db)
					s.dbschema = dict(PinoToDo.dbschema)
					s.rtset = dict(PinoToDo.rtset)

					json.dump([s.db,s.dbschema,s.rtset],f)
					s.vstatusset(s.vstr('ok_file_createnew'))
				return True
		s.vstatusset(s.vstr('er_file_load'))

		return False

	# Stores database file
	def filewrite(s,db,filename="tasks.json"):
		try:
			with open(filename,"w") as f:
				json.dump([s.db,s.dbschema,s.rtset],f)
				#s.vstatusset(s.vstr('ok_file_write'))
		except:
			s.vstatusset(s.vstr('er_file_write'))
		return None

	# Changes or returns settings values
	def setting(s,setting):
		setting = setting.split('=')
		if   len(setting) == 2: key, value = setting
		elif len(setting) == 1: key, value = (setting[0],None)

		if key == '':
			s.vstatusset(str(s.rtset))
			return True
		elif key not in s.rtset:
			s.vstatusset(s.vstr('er_invalid_id_s') % key)
			return False
		elif value == None:
			s.vstatusset(s.vstr('ok_display_value_ss') % (key, s.rtset[key]))
		elif value in ('0','False','false'):
			s.rtset[key] = False
		elif value in ('1','True','true'):
			s.rtset[key] = True
		s.vstatusset(s.vstr('ok_setting_set_ss') % (key, s.rtset[key]))
		return True

	'''
	"ok_setting_value_ss": "Value of %s is: %s",
	"ok_setting_set_ss": "%s setting changed to %s",
	"er_setting_notset_s": "Error changing setting %s",
	"er_setting_invalidval_ss": "Invalid value for %s. Should be %s",'''

	# Adds a new task
	def tasknew(s,text='',args=[]):
		if len(text) == 0:
			s.vstatusset(s.vstr('er_task_noadd_emptystr'))
			return False
		try:
			taskid = str(s.allocid())

			# Possible arguments to mark as critical
			cri = {"!","critical","markcritical","cri"} #TODO: avoid hardcode
			if len(cri.intersection(args)) > 0:
				critical = 1
			else:
				critical = 0

			created = time.time()
			completed = 0 # zero means not marked as completed
			s.db[taskid] = [created,completed,critical,text]
			s.vstatusset(s.vstr('ok_task_added_s') % taskid)
			return taskid
		except:
			s.vstatusset(s.vstr('er_task_noadd'))
			return False

	# Deletes a task by its ID
	def taskdel(s,idlist):
		if len(idlist) == 0:
			s.vstatusset(s.vstr('er_notaskid'))
			return False
		try:
			idlist = idlist.split(',')
			if s.allidexist(idlist,displayerror=True): # Delete all or none
				for oneid in idlist: del s.db[oneid]
			else:
				return False
			s.vstatusset(s.vstr('ok_task_deleted_s') % ','.join(idlist))
			return True
		except:
			return False

	# check if one or more IDs exist. Be careful not to pass strings as idlist
	def allidexist(s,idlist,displayerror=False):
		if type(idlist) == str: idlist = (idlist,)
		try:
			for oneid in idlist:
				last = oneid
				s.db[oneid] # if index doesn't exist this will raise exception
			return True
		except:
			if displayerror != False:
				s.vstatusset(s.vstr('er_invalid_id_s')   % last)
			return False

	# Toggles complete status between 0 (not completed) and .time() (completed)
	def tasktogglecomplete(s,idlist):
		if len(idlist) == 0:
			s.vstatusset(s.vstr('er_notaskid'))
			return False
		idlist = idlist.split(',')
		if s.allidexist(idlist,displayerror=True):
			for taskid in idlist:
				if s.db[taskid][1] == 0:
					s.db[taskid][1] = time.time()
					s.vstatusset(s.vstr("ok_task_markcomplete_s") % taskid)
				else:
					s.db[taskid][1] = 0
					s.vstatusset(s.vstr("ok_task_marknew_s") % taskid)
			return True
		else:
			return False;

	# Toggles critical (!) status
	def tasktogglecrit(s,idlist):
		if len(idlist) == 0:
			s.vstatusset(s.vstr('er_notaskid'))
			return False
		idlist = idlist.split(',')
		if s.allidexist(idlist,displayerror=True):
			for taskid in idlist:
				if s.db[taskid][2] == 0:
					s.db[taskid][2] = 1
					s.vstatusset(s.vstr("ok_task_markcrit_s") % taskid)
				else:
					s.db[taskid][2] = 0
					s.vstatusset(s.vstr("ok_task_marknocrit_s") % taskid)
			return True
		else:
			return False


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
	def cls(s):
		if sys.platform.startswith('win'): os.system("cls")
		else: os.system("clear")

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
		return "\n".join([theline]*count) if count > 0 else False

	# Title panel
	def vtitle(s,modtitle=""):
		output=""
		output += ' '+s.vstr("program_title")+"\n" if len(modtitle)==0 else modtitle+"\n"
		output += s.vhline(style=0)
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

	# Displays a single task
	def vshowtask(s,taskid):
		limit = s.linesleft
		display = []
		line = ''
		linecount = 0
		_ = display.append
		try:
			task = s.db[taskid]
			critical = ' '+s.vstr('detail_critical') if task[2] else ''
			st = time.gmtime(task[0])
			ed = time.gmtime(task[1]) if task[1] > 0 else 0
			body = s.linebreak(task[3], s.termsize[0], True)
			_('')
			_(s.vstr('detail_taskid_ss') % (taskid,critical))
			_(s.vhline(style=2))
			_(s.vstr('detail_description')+'\n')
			[_(x) for x in s.linebreak(task[3], s.termsize[0], True)]
			_(s.vhline(style=2))
			_(s.vstr('detail_created') % (st[0],st[1],st[2],st[3],st[4]))
			if ed != 0:
				_(s.vstr('detail_completed') % (ed[0],ed[1],ed[2],ed[3],ed[4]))
		except:
			s.vstatusset(s.vstr('er_invalid_id_s') % taskid)
			return False
		s.linesleftset(-len(display))
		return "\n".join(display)

	# Display list of tasks
	def vtasklist(s):
		limit = s.linesleft
		display = [[],[],[]] # Critical (top), normal (middle), ended (bottom)
		line = ''
		linecount = 0


		for key, item in s.db.items():
			if limit <= 0: break
			if item[1] > 0 and s.rtset['show_completed'] == False:
				continue
			line += ' ' # left margin
			line += key.rjust(4)
			line += '![' if item[2] != 0 else ' [' # Critical '!' or not ' '
			line += 'x] ' if item[1] > 0 else ' ] ' # Marked completed or not
			line += item[3]

			display_ind = 1 # default add to middle
			if item[2] == 1 and s.rtset['critical_first'] == True:
				display_ind = 0
			if item[1] > 0 and s.rtset['completed_last'] == True:
				display_ind = 2

			linecount = len([display[display_ind].append(l) for l in s.linebreak(line,s.termsize[0], True)])
			line = ''
			s.linesleftset(-linecount)
			limit -= linecount
		display = display[0]+display[1]+display[2]
		if limit < 0: display = display[:limit]
		# ^ Means that the last entry overflowed the line limit. Maybe should
		# discard the line instead of truncating?

		if linecount > 0:
			return "\n".join(display)
		else:
			return None

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
			s.vbuffer += (item,)
			totallines += item.count("\n")+1
		return totallines

	# outputs the buffer [and clears it by default]
	def vbuffer_dump(s,clear=True):
		for piece in s.vbuffer:
			if type(piece[0]) != str: continue
			print(piece[0],end="\n")
		if clear == True: s.vbuffer_clear()
		return True

	# Resets the buffer
	def vbuffer_clear(s): s.vbuffer = list()

#C#
	def flow(s):
		command = ''
		while command[:1] != 'y':
			while command not in ('q','quit','exit','bye','Q'):
				s.termsizeset()
				s.vbuffer_clear()
				s.cls()
				s.linesleftset(s.termsize[1])
				s.fileload()
				lastcmd = s.parsecmd(command)
				s.docmd(*lastcmd)
				s.filewrite(s.db)
				s.linesleftset(-1) # Reserve space for the footer, including divider

				s.vbuffer_add(
					# Header
					(s.vtitle(),'vtitle')
				)

				# Body

				if lastcmd[0] in ('show',):
					s.vbuffer_add((s.vshowtask(lastcmd[2]),'vshowtask'))
				else:
					s.vbuffer_add((s.vtasklist(),'vtasklist'))

				s.vbuffer_add(
					(s.vhline(width=0,count=s.linesleft),'vhline'),

					# Footer starts
					(s.vhline(style=1),'vhline'),
					(s.vstatusbar(),'vstatusbar')
				)
				s.vbuffer_dump(clear=False) #should leave one empty line
				command = s.vprompt()

			s.cls()
			s.vbuffer_dump()
			if command == 'Q':
				command = 'y'
				s.cls()
				print(s.vstr('ok_exit'))
				continue
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
	def parsecmd(s,rawinput): # eg: User has entered 'add -! Buy food'
		cmdmain = '' # first part of the command
		args = [] # list of arguments preceded by "-"
		fstr = '' # final part of the command -- a task ID, text etc
		# first we try to isolate the first part of the user input.
		# parts of commands are separated by " "
		cmd = rawinput.strip().split(' ',1)
		# if rawinput was '', then cmd will be [''] at this point
		cmdmain = cmd[0] # main part of the command (add, delete etc)
		del cmd[0] # if rawinput was '', then cmd is now []

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
		while len(cmd) > 0:
			if len(cmd[0]) == 0: # probably prevented by 1st rawinput.strip()
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
		return (cmdmain, args, fstr)


	# executes command parsed by parsecmd()
	def docmd(s,cmdmain,args,fstr):
		if len(cmdmain) > 0 and cmdmain not in s.cmdaliases:
			s.vstatusset(s.vstr('er_comm_invalid_s') % cmdmain)
			return False

		switch = s.cmdaliases[cmdmain]
		if switch in ('','qui','Q'): return True
		elif switch == 'start': return True
		elif switch == 'show': return True
		elif switch == 'add': return s.tasknew(fstr,args)
		elif switch == 'delete': return s.taskdel(fstr)
		elif switch == 'markcomplete':
			ret = s.tasktogglecomplete(fstr)
			if ret != False: return True
			else: return False
		elif switch == 'markcritical':
			ret = s.tasktogglecrit(fstr)
			if ret != False: return True
			else: return False
		elif switch == 'sort': s.reorder()
		elif switch == 'debug': print(s.db)
		elif switch == 'debug_minautoincr': s.autoincr_setfirstempty()
		elif switch == 'debug_nextid':
			s.vstatusset("Auto-increment value: %s (not necessarily available)" % s.dbschema['autoincr'])
		elif switch == 'dwipe':
			s.db=dict()
			s.autoincr_setfirstempty()
		elif switch == 'set': s.setting(fstr)
		else:
			s.vstatusset(s.vstr('er_not_implemented')+"; switch: '%s', fstr: %s, cmdmain: %s, args: %s" % (switch, fstr, cmdmain, args))
			return None
		return True

	# Decides what view module to show
	def callview(s,cmd):
		s.vtasklist() #BOGUS

	# Breaks lines
	def linebreak(s,string,width,multiline=False):
		lines = list()
		last = list(string) # last is sliced until empty and put into [lines]
		while len(last) > 0:
			if multiline != False:
				first, last = last[:width], last[width:]
				lines.append(''.join(first))
				continue
			else:
				return [string[:width]]
		return lines

	dialogues = {
		"program_title": "Pino Tasks",
		"prompt": "> ",
		"ok_exit": "Goodbye",
		"er_notaskid": "A valid task ID must be provided",
		"ok_task_added_s": "Task added succesfully (ID %s)",
		"er_task_noadd": "Error when adding task",
		"er_task_noadd_emptystr": "Error: Input must not be empty",
		"ok_task_markcrit_s": "Task marked as critical (ID %s)",
		"ok_task_deleted_s": "Task deleted (ID %s)",
		"ok_task_markcomplete_s": "Task marked as completed (ID %s)",
		"ok_task_marknew_s": "Task marked as new (ID %s)",
		"ok_task_marknocrit_s": "Task marked as not critical (ID %s)",
		"ok_task_markcrit_s": "Task marked as critical (ID %s)",
		"ok_display_value_ss": "Value of %s is: %s",
		"ok_setting_set_ss": "%s setting changed to %s",
		"er_setting_notset_s": "Error changing setting %s",
		"er_setting_invalidval_ss": "Invalid value for %s. Should be %s",
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
		"autoincr_set_s": "Auto-increment value set to %s",
		"detail_taskid_ss": "Task ID: %s%s",
		"detail_critical": " (CRITICAL)",
		"detail_description": "DESCRIPTION:",
		"detail_created":   "  Created: %s-%s-%s %s:%s", # Space added to align with completed
		"detail_completed": "Completed: %s-%s-%s %s:%s"

	}
	cmdaliases = {
		# Default
		'start': 'start',
		'': 'start',
		# quit: exit comands
		'quit': 'quit',
		'q':'quit', 'exit':'quit', 'bye':'quit','Q':'quit!',
		# show: display all task data
		'show': 'show',
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
		# set: change settings
		'set': 'set',
		# SPECIAL
		'debug':'debug', 'dminid': 'debug_minautoincr','dnid': 'debug_nextid',
		'dwipe':'dwipe'
	}

if __name__ == "__main__": PinoToDo()
