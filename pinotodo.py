import os # cls()
import sys # file handling
import json # database serializing
import shutil # terminal size
import time # task metadata
import math # ceil() to round number of lines
import collections # self.db is an OrderedDict (similar to dict in Python 3.6)

class PinoToDo:
    dbfile = 'tasks' # default database file on disk (without extension)
    dbfile_ext = '.json' # extension for the database file on disk
    termsize = (80,24) # Viewport size
    linesleft = 0 # vertical space left in number of lines
    vbuffer = list()
    dispstatus = list()

    #not yet implemented
    #lastinput = ('','',[]) # main command, final string/ID and arguments


    theme_lines = ("=","-",".") # indexes represent levels, 0 being the highest
    def __init__(self):
        self.flow()
        pass

#M#

    # Loads database file
    def fileload(self,filename=None):
        if not filename: filename = self.dbfile
        try:
            with open('%s%s' % (filename,self.dbfile_ext),"r") as f:
                tmpdbfile = json.load(f, object_pairs_hook=collections.OrderedDict)
                if   len(tmpdbfile) == 2: self.db, self.dbschema = tmpdbfile
                elif len(tmpdbfile) == 3: self.db, self.dbschema, self.rtset = tmpdbfile
                else: raise Exception
            return True
        except:
            self.dbinit()
            self.filewrite()
            self.vstatusset(self.vstr('ok_file_createnew'))
            return True
        self.vstatusset(self.vstr('er_file_load'))

        return False

    # Stores database file
    def filewrite(self):
        try:
            with open('%s%s' % (self.dbfile,self.dbfile_ext),"w") as f:
                json.dump([self.db,self.dbschema,self.rtset],f)
                #self.vstatusset(self.vstr('ok_file_write'))
        except:
            self.vstatusset(self.vstr('er_file_write'))
        return None

    # Sets the database default state
    # Doesn't directly affects the database file
    def dbinit(self):
        self.db = collections.OrderedDict() # Tasks database
        self.dbschema = { # Database metadata
            'autoincr': 0 # next available id
        }
        self.rtset = { # Runtime settings
            'show_completed': True,
            'completed_last': True, # no effect if show_completed = False
            'critical_first': True,
        }
        return None

    # Wipes the content of the working database
    # Doesn't directly affects the database file
    def wipedb(self):
        self.db=collections.OrderedDict()
        self.autoincr_setfirstempty(quiet=True)
        return None

    def setdbfile(self,dbfile=None):
        if not dbfile:
            self.vstatusset(self.vstr('ok_display_value_ss') % ('dbfile',self.dbfile))
        elif dbfile == self.dbfile:
            self.vstatusset(self.vstr('er_dbfile_unchanged'))
        elif type(dbfile) == str:
            self.filewrite()
            self.dbfile = dbfile
            self.wipedb()
            self.fileload()
        return None

    # Changes or returns settings values
    def setting(self,setting):
        setting = setting.split('=')
        if   len(setting) == 2: key, value = setting
        elif len(setting) == 1: key, value = (setting[0],None)

        if key == '':
            self.vstatusset(str(self.rtset))
            return True
        elif key not in self.rtset:
            self.vstatusset(self.vstr('er_invalid_id_s') % key)
            return False
        elif value == None:
            self.vstatusset(self.vstr('ok_display_value_ss') % (key, self.rtset[key]))
        elif value in ('0','False','false'):
            self.rtset[key] = False
        elif value in ('1','True','true'):
            self.rtset[key] = True
        self.vstatusset(self.vstr('ok_setting_set_ss') % (key, self.rtset[key]))
        return True

    '''
    "ok_setting_value_ss": "Value of %s is: %s",
    "ok_setting_set_ss": "%s setting changed to %s",
    "er_setting_notset_s": "Error changing setting %s",
    "er_setting_invalidval_ss": "Invalid value for %s. Should be %s",'''

    # Adds a new task
    def tasknew(self,text='',args=[]):
        if len(text) == 0:
            self.vstatusset(self.vstr('er_task_noadd_emptystr'))
            return False
        try:
            taskid = str(self.allocid())

            # Possible arguments to mark as critical
            cri = {"!","critical","markcritical","cri"} #TODO: avoid hardcode
            if len(cri.intersection(args)) > 0:
                critical = 1
            else:
                critical = 0

            created = time.time()
            completed = 0 # zero means not marked as completed
            self.db[taskid] = [created,completed,critical,text]
            self.vstatusset(self.vstr('ok_task_added_s') % taskid)
            return taskid
        except:
            self.vstatusset(self.vstr('er_task_noadd'))
            return False

    # Deletes a task by its ID
    def taskdel(self,idlist):
        if len(idlist) == 0:
            self.vstatusset(self.vstr('er_notaskid'))
            return False
        try:
            idlist = idlist.split(',')
            if self.allidexist(idlist,displayerror=True): # Delete all or none
                for oneid in idlist: del self.db[oneid]
            else:
                return False
            self.vstatusset(self.vstr('ok_task_deleted_s') % ','.join(idlist))
            return True
        except:
            return False

    def taskedit(self,taskid,value):
        if len(taskid) == 0:
            self.vstatusset(self.vstr('er_notaskid'))
            return False

        if not self.allidexist(taskid,displayerror=True): return False

        self.db[taskid][3] = value
        self.vstatusset(self.vstr('ok_task_edited_s') % taskid)
        return True

    # check if one or more IDs exist. Be careful not to pass strings as idlist
    def allidexist(self,idlist,displayerror=False):
        if type(idlist) == str: idlist = (idlist,)
        try:
            for oneid in idlist:
                last = oneid
                self.db[oneid] # if index doesn't exist this will raise exception
            return True
        except:
            if displayerror != False:
                self.vstatusset(self.vstr('er_invalid_id_s')   % last)
            return False

    # Toggles complete status between 0 (not completed) and .time() (completed)
    def tasktogglecomplete(self,idlist):
        if len(idlist) == 0:
            self.vstatusset(self.vstr('er_notaskid'))
            return False
        idlist = idlist.split(',')
        if self.allidexist(idlist,displayerror=True):
            for taskid in idlist:
                if self.db[taskid][1] == 0:
                    self.db[taskid][1] = time.time()
                    self.vstatusset(self.vstr("ok_task_markcomplete_s") % taskid)
                else:
                    self.db[taskid][1] = 0
                    self.vstatusset(self.vstr("ok_task_marknew_s") % taskid)
            return True
        else:
            return False;

    # Toggles critical (!) status
    def tasktogglecrit(self,idlist):
        if len(idlist) == 0:
            self.vstatusset(self.vstr('er_notaskid'))
            return False
        idlist = idlist.split(',')
        if self.allidexist(idlist,displayerror=True):
            for taskid in idlist:
                if self.db[taskid][2] == 0:
                    self.db[taskid][2] = 1
                    self.vstatusset(self.vstr("ok_task_markcrit_s") % taskid)
                else:
                    self.db[taskid][2] = 0
                    self.vstatusset(self.vstr("ok_task_marknocrit_s") % taskid)
            return True
        else:
            return False


    # Sets auto-increment value to smallest available index (NOT the highest)
    def autoincr_setfirstempty(self,quiet=False):
        tryval = 0
        for i in range(len(self.db)+1):
            if str(tryval) in self.db:
                tryval += 1
                continue
            else:
                self.dbschema['autoincr'] = tryval
                if not quiet:
                    self.vstatusset(self.vstr('autoincr_set_s') % tryval)
                break
        return tryval

    # returns the next available ID based on self.dbschema['autoincr'] value
    def allocid(self):
        if str(self.dbschema['autoincr']) not in self.db:
            ret = self.dbschema['autoincr']
            self.dbschema['autoincr'] += 1
        else:
            while True:
                if str(self.dbschema['autoincr']) in self.db:
                    self.dbschema['autoincr'] += 1
                    continue
                else:
                    ret = self.dbschema['autoincr']
                    self.dbschema['autoincr'] += 1
                    break
        if type(ret) != int: raise Exception('Hole in the loop!')
        else: return ret

    def reorder(self):
        dbsorted = collections.OrderedDict()
        for key in sorted(self.db):
            dbsorted[str(key)] = self.db[str(key)]
        self.db = dbsorted
        return None

#V#
    # defines the terminal size
    def termsizeset(self,width=0, height=0): #DONE
        if width > 0 and height > 0:
            w, h = width, height
            self.termsize = (w,h)
        else:
            self.termsize = shutil.get_terminal_size((80,24))[:]
        return self.termsize

    # Returns number of empty lines or subtract from current number
    def linesleftset(self,lines=0): # DONE
        if   lines == 0: pass
        elif lines <  0: self.linesleft += lines
        elif lines >  0: self.linesleft  = lines
        return self.linesleft

    # Clears the screen
    # TODO: make screen clearing cross-platform
    def cls(self):
        if sys.platform.startswith('win'): os.system("cls")
        else: os.system("clear")

    # Retrieves string for display
    def vstr(self,index=None,pre="",pos=""):
        return pre+self.dialogues[index]+pos if index in self.dialogues else "???"

    # Builds a horizontal line
    # For blank line, style=" "
    # IDEA: fill argument; fills all empty space with blank lines
    def vhline(self,style=None,width=None,count=1):
        vis = self.theme_lines[0] # Fallback
        theline = "" # Fallback

        if   type(style) == str: vis = style
        elif type(style) == int: vis = self.theme_lines[style]

        if width == None: width = self.termsize[0] # defaults to full width

        theline = (vis*int((width/len(vis))+1))[:width]

        self.linesleftset(-count)
        return "\n".join([theline]*count) if count > 0 else False

    # Title panel
    def vtitle(self,modtitle=""):
        output=""
        output += ' ' \
               +  self.vstr("program_title") \
               +  ' | ' \
               +  self.vstr("current_file_ss") % (self.dbfile, self.dbfile_ext) \
               +  "\n" if len(modtitle)==0 else modtitle+"\n"
        output += self.vhline(style=0)
        self.linesleftset(-2)
        return output

    # Status bar
    def vstatusbar(self):
        #self.linesleftset(-len(self.dispstatuself)) # set by vstatusset()
        for k,v in enumerate(self.dispstatus):
            self.dispstatus[k] = v.rjust(self.termsize[0])
        ret = "\n".join(self.dispstatus) if len(self.dispstatus) > 0 else None

        self.dispstatus = list()
        return ret

    # Adds a string to be displayed in the status bar
    def vstatusset(self,msg):
        self.dispstatus += [msg]
        linecount = self.linesleftset(-(msg.count("\n")+1))
        return linecount

    # Displays a single task
    def vshowtask(self,taskid):
        limit = self.linesleft
        display = []
        line = ''
        linecount = 0
        _ = display.append
        try:
            task = self.db[taskid]
            critical = ' '+self.vstr('detail_critical') if task[2] else ''
            st = time.gmtime(task[0])
            ed = time.gmtime(task[1]) if task[1] > 0 else 0
            body = self.linebreak(task[3], self.termsize[0], True)
            _('')
            _(self.vstr('detail_taskid_ss') % (taskid,critical))
            _(self.vhline(style=2))
            _(self.vstr('detail_description')+'\n')
            [_(x) for x in self.linebreak(task[3], self.termsize[0], True)]
            _(self.vhline(style=2))
            _(self.vstr('detail_created') % (st[0],st[1],st[2],st[3],st[4]))
            if ed != 0:
                _(self.vstr('detail_completed') % (ed[0],ed[1],ed[2],ed[3],ed[4]))
        except:
            self.vstatusset(self.vstr('er_invalid_id_s') % taskid)
            return False
        self.linesleftset(-len(display))
        return "\n".join(display)

    # Display list of tasks
    def vtasklist(self):
        limit = self.linesleft
        display = [[],[],[]] # Critical (top), normal (middle), ended (bottom)
        line = ''
        linecount = 0


        for key, item in self.db.items():
            if limit <= 0: break
            if item[1] > 0 and self.rtset['show_completed'] == False:
                continue
            line += ' ' # left margin
            line += key.rjust(4)
            line += '![' if item[2] != 0 else ' [' # Critical '!' or not ' '
            line += 'x] ' if item[1] > 0 else ' ] ' # Marked completed or not
            line += item[3]

            display_ind = 1 # default add to middle
            if item[2] == 1 and self.rtset['critical_first'] == True:
                display_ind = 0
            if item[1] > 0 and self.rtset['completed_last'] == True:
                display_ind = 2

            linecount = len([display[display_ind].append(l) for l in self.linebreak(line,self.termsize[0], True)])
            line = ''
            self.linesleftset(-linecount)
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
    def vprompt(self,altprompt="",preorder=False):
        promptstr = altprompt if len(altprompt) > 0 else self.vstr("prompt")
        self.linesleftset(-1) # tecnhically this should zero self.linesleft
        return input(promptstr)

    # adds text to the buffer; returns number of lines added
    # IDEA: add "repeat" parameter; buffers the same string #repeat times
    # IDEA: automatic line break; prevents overflowing and counts extra line
    def vbuffer_add(self,*inputs):
        totallines = 0
        for key, item in enumerate(inputs):
            self.vbuffer += (item,)
            totallines += item.count("\n")+1
        return totallines

    # outputs the buffer [and clears it by default]
    def vbuffer_dump(self,clear=True):
        for piece in self.vbuffer:
            if type(piece[0]) != str: continue
            print(piece[0],end="\n")
        if clear == True: self.vbuffer_clear()
        return True

    # Resets the buffer
    def vbuffer_clear(self): self.vbuffer = list()

#C#
    def flow(self):
        command = ''
        while command[:1] != 'y':
            while command not in ('q','quit','exit','bye','Q'):
                self.termsizeset()
                self.vbuffer_clear()
                self.cls()
                self.linesleftset(self.termsize[1])
                self.fileload()
                lastcmd = self.parsecmd(command)
                self.docmd(*lastcmd)
                self.filewrite()
                self.linesleftset(-1) # Reserve space for the footer, including divider

                self.vbuffer_add(
                    # Header
                    (self.vtitle(),'vtitle')
                )

                # Body

                if lastcmd[0] in ('show',):
                    self.vbuffer_add((self.vshowtask(lastcmd[2]),'vshowtask'))
                else:
                    self.vbuffer_add((self.vtasklist(),'vtasklist'))

                self.vbuffer_add(
                    (self.vhline(width=0,count=self.linesleft),'vhline'),

                    # Footer starts
                    (self.vhline(style=1),'vhline'),
                    (self.vstatusbar(),'vstatusbar')
                )
                self.vbuffer_dump(clear=False) #should leave one empty line
                command = self.vprompt()

            self.cls()
            self.vbuffer_dump()
            if command == 'Q':
                command = 'y'
                self.cls()
                print(self.vstr('ok_exit'))
                continue
            command = self.vprompt(self.vstr('q_sure_n'))
            if command not in ['y','n'] or command == 'y':
                self.filewrite()
                self.cls()
                print(self.vstr('ok_exit'))
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
    def parsecmd(self,rawinput): # eg: User has entered 'add -! Buy food'
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
    def docmd(self,cmdmain,args,fstr):
        if len(cmdmain) > 0 and cmdmain not in self.cmdaliases:
            self.vstatusset(self.vstr('er_comm_invalid_s') % cmdmain)
            return False

        switch = self.cmdaliases[cmdmain]
        if switch in ('','qui','Q'): return True
        elif switch == 'start': return True
        elif switch == 'show': return True
        elif switch == 'add': return self.tasknew(fstr,args)
        elif switch == 'delete': return self.taskdel(fstr)
        elif switch == 'edit': return self.taskedit(*fstr.split(' ',1))
        elif switch == 'markcomplete':
            ret = self.tasktogglecomplete(fstr)
            if ret != False: return True
            else: return False
        elif switch == 'markcritical':
            ret = self.tasktogglecrit(fstr)
            if ret != False: return True
            else: return False
        elif switch == 'sort': self.reorder()
        elif switch == 'debug': print(self.db)
        elif switch == 'debug_minautoincr': self.autoincr_setfirstempty()
        elif switch == 'debug_nextid':
            self.vstatusset("Auto-increment value: %s (not necessarily available)" % self.dbschema['autoincr'])
        elif switch == 'dwipe': self.wipedb()
        elif switch == 'set': self.setting(fstr)
        elif switch == 'dbfile': self.setdbfile(fstr)
        else:
            self.vstatusset(self.vstr('er_not_implemented')+"; switch: '%s', fstr: %s, cmdmain: %s, args: %s" % (switch, fstr, cmdmain, args))
            return None
        return True

    # Decides what view module to show
    def callview(self,cmd):
        self.vtasklist() #BOGUS

    # Breaks lines
    def linebreak(self,string,width,multiline=False):
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
        "current_file_ss": "File: %s%s",
        "prompt": "> ",
        "ok_exit": "Goodbye",
        "er_notaskid": "A valid task ID must be provided",
        "ok_task_added_s": "Task added succesfully (ID %s)",
        "er_task_noadd": "Error when adding task",
        "er_task_noadd_emptystr": "Error: Input must not be empty",
        "ok_task_markcrit_s": "Task marked as critical (ID %s)",
        "ok_task_deleted_s": "Task deleted (ID %s)",
        "ok_task_edited_s": "Task edited (ID %s)",
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
        "er_dbfile_unchanged": "Database file unchanged",
        "ok_file_createnew": "Starting with a blank database",
        "ok_file_write": "Database written to file",
        "autoincr_already_minimal": "Auto-increment value is already the lowest possible",
        "autoincr_set_s": "Auto-increment value set to %s",
        "q_sure_n": "Are you sure: [y/N]",
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
        # edit: edit a task
        'edit': 'edit',
        'e':'edit',
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
        # dbfile: change database file on disk
        'dbfile': 'dbfile',
        # SPECIAL
        'debug':'debug', 'dminid': 'debug_minautoincr','dnid': 'debug_nextid',
        'dwipe':'dwipe'
    }

if __name__ == "__main__": PinoToDo()
