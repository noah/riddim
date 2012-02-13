import os
import re
from optparse import OptionParser
#from lib.logger import log

from lib.config import RiddimConfig

class RiddimOptions(object):
    def __init__(self):
        self.config = RiddimConfig().config
        self.op = OptionParser()
        self.op.disable_interspersed_args() # unix-style
        # boolean flags
        self.flags = {
                # only with signals
                '-f' : ['--foreground','don\'t fork the server','store_true',False],
                # server booleans
                '-p' : ['--play','start playback','store_true',False],
                '-u' : ['--pause','pause playback','store_true',False],
                '-s' : ['--stop','stop playback','store_true',False],
                '-R' : ['--repeat','toggle repeat','store_true',False],
                '-S' : ['--shuffle','toggle shuffle','store_true',False],
                '-q' : ['--query','display server state','store_true',False],
                # non-booleans
                '-i' : ['--index','set song index to value','store',False],
                '-k' : ['--signal','signal stop/start/status','store',False],
                '-e' : ['--enqueue','enqueue track(s) onto playlist','store',False],
                '-c' : ['--clear','clear playlist with optional regex','store',None],
                # this gets pruned from the flags
                '-P' : ['--port','port number to try','store',18944]
        }

        for short,v in self.flags.iteritems():
            long, help, action, default = v
            self.op.add_option(short,long,action=action,help=help,default=default)
        prune = ['-P']
        for p in prune:
            del self.flags[p]

        self.options, self.args = self.op.parse_args()
        self.signal = self.check_signal()

        if self.signal:
            self.foreground = self.options.foreground
            self.port = self.options.port
        else:
            self.flag = self.check_flag()

    def check_signal(self):
        valid_signals = ['stop','start','restart','status']
        if self.options.signal and self.options.signal in valid_signals:
            return self.options.signal
        else:
            return False

    def check_flag(self):
        valid_flags = [re.sub('\-\-','',f[0]) for f in self.flags.values()]
        # we can get away with using eval here 
        #   . . . right?  ;)
        try:
            return [flag for flag in valid_flags if eval("self.options.%s" % flag)][0]
        except IndexError:
            self.op.print_help()
            return False
