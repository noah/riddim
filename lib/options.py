import re
from optparse import OptionParser

class RiddimOptions:
    def __init__(self):
        self.op = OptionParser()
        self.op.disable_interspersed_args() # unix-style
        self.op.add_option('-k','--signal',help='signal stop/start/status')
        self.op.add_option('-P','--port',help='port number to try')
        self.flags = {
                # server booleans
                '-p' : ['--play',       'start playback'],
                '-u' : ['--pause',      'pause playback'],
                '-s' : ['--stop',       'stop playback'],
                '-n' : ['--next',       'proceed to next track'],
                '-r' : ['--prev',       'go back to previous track'],
                '-R' : ['--repeat',     'toggle repeat'],
                '-S' : ['--shuffle',    'toggle shuffle'],
                '-Q' : ['--query',      'display server state'],
                '-c' : ['--clear',      'clear playlist'],
                # only with signals
                '-f' : ['--foreground', 'don\'t for the server'],
                # non-bool
                '-e' : ['--enqueue',    'enqueue track(s) onto playlist'],
        }
        for short,v in self.flags.iteritems():
            long,help = v
            self.op.add_option(short,long,action='store_true',help=help)

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
        # we can get away with using eval here because of the strict input
        # checking.  right?  ;)
        try:
            return [flag for flag in valid_flags if eval("self.options.%s" % flag)][0]
        except IndexError:
            self.op.print_help()
            return False
