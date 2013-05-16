import os
import sys
import time
import errno
import socket
import signal

from lib.config import Config
from lib.server import Server
from lib.logger import log
from lib.data import set_data


class Control(object):

    def __init__(self, port):
        self.port = port

    def read_pid(self):
        try:
            with open(Config.pidpath, 'r') as f:
                return int( f.read().strip() )
        except:
            return False

    def write_pid(self, pid):
        with open(Config.pidpath, 'w') as f:
            f.write( str(pid) )

    def start(self):
        pid = self.read_pid()
        if pid:
            log.error("Server already running, pid %s." % pid)
            sys.exit( -1 )
        else:
            self.write_pid( os.getpid() )

        try:
            time.sleep(0.001)
            Server((Config.hostname, self.port))
            # will never reach this line
        except socket.error, se:
            if se.errno == errno.EACCES:
                log.warn("Bad port: %s" % self.port)
                sys.exit( se.errno )
            else:
                log.exception(se)
        except KeyboardInterrupt:
            pass

    def stop(self):
        time.sleep(0.1)
        pid = self.read_pid()
        if pid:
            try:
                set_data(self.port, 'running', False)
                #os.kill( pid, signal.SIGTERM)
            except OSError:  # already dead
                pass
            except socket.error, se:
                if se.errno == errno.ECONNREFUSED:
                    log.warn("not running")
            self.write_pid("")

    def restart(self):
        self.stop()
        time.sleep(1)
        self.start()
