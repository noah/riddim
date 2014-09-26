# -*- coding: utf-8 -*-
import os
import sys
import time
import errno
import socket
import signal
import codecs

from lib.config import Config
from lib.server import Server
from lib.logger import log
from lib.data import set_data


class Control(object):

    def __init__(self, port):
        self.port    = port
        self.pidpath = Config.pidpath( port )

    def read_pid(self):
        try:
            with codecs.open(self.pidpath, u'r') as f:
                return int( f.read().strip() )
        except:
            return False

    def write_pid(self, pid):
        with codecs.open(self.pidpath, u'w') as f:
            f.write( unicode(pid) )

    def start(self):
        pid = self.read_pid()
        if pid:
            log.error(u"Server already running, pid %s." % pid)
            sys.exit( -1 )
        else:
            self.write_pid( os.getpid() )

        try:
            time.sleep(0.001)
            Server((Config.hostname, self.port))
            # will never reach this line
        except socket.error, se:
            if se.errno == errno.EACCES:
                log.warn(u"Bad port: %s" % self.port)
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
                set_data(self.port, u'running', False)
                #os.kill( pid, signal.SIGTERM)
            except OSError:  # already dead
                pass
            except socket.error, se:
                if se.errno == errno.ECONNREFUSED:
                    log.warn(u"not running")
            self.write_pid(u"")

    def restart(self):
        self.stop()
        time.sleep(1)
        self.start()
