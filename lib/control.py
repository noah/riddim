import os
import sys
import time
import errno
import socket

from lib.config import Config
from lib.server import Server
from lib.logger import log


class Control():

    @staticmethod
    def read_pid():
        try:
            with open(Config.pidpath, 'r') as f:
                return int( f.read().strip() )
        except:
            return False

    @staticmethod
    def write_pid(pid):
        with open(Config.pidpath, 'w') as f:
            f.write( str(pid) )

    @staticmethod
    def start():
        pid = Control.read_pid()
        if pid:
            log.error("Server already running, pid %s." % pid)
            sys.exit( -1 )
        else:
            Control.write_pid( os.getpid() )

        try:
            time.sleep(0.001)
            Server((Config().hostname, int(Config.port)))
            # will never reach this line
        except socket.error, se:
            if se.errno == errno.EACCES:
                log.warn("Bad port: %s" % Config.port)
                sys.exit( se.errno )
            else:
                log.exception(se)

    @staticmethod
    def stop():
        pid = Control.read_pid()
        if pid:
            import signal
            try:
                os.kill( pid, signal.SIGTERM )
                log.info("killed: %s" % pid)
            except OSError:  # already died
                pass
            Control.write_pid("")

        log.info("RiDDiM is stopped.")
        sys.exit( 0 )
