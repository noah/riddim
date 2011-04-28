#!/usr/bin/env python2

"""
Copyright (c) <2010> <Noah K. Tilton> <noahktilton@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import os
import sys
import time
import threading
import xmlrpclib

from lib.daemonize import daemonize
from lib.data import RiddimData
from lib.config import RiddimConfig
from lib.options import RiddimOptions
from lib.server import RiddimServer
from lib.xmlrpc import RiddimRPCRegisters, RiddimRPCClient

class RiddimCLI(RiddimRPCClient):
    def __init__(self):
        self.rc = RiddimConfig()
        self.data = RiddimData()
        self.logfile = os.path.join(self.rc.cwd,'log',self.rc.config.get('riddim','logfile'))
        self.pidfile = os.path.join(self.rc.cwd,'var','run',self.rc.config.get('riddim','pidfile'))
        self.o = RiddimOptions()
        self.rpc = xmlrpclib.ServerProxy('http://%s:%s' %
                (self.data['hostname'],self.o.options.port), allow_none=True)

    def kickoff(self,port):
        MINUTE=60
        INTERVAL=2
        for retry in range(1, (int(5 * MINUTE) / INTERVAL)):
            try:
                time.sleep(0.001)
                address = ('0.0.0.0',int(port))
                riddim_server = RiddimServer(address)
                self.ip,self.port = riddim_server.server_address
                riddim_server.register_instance(RiddimRPCRegisters(riddim_server))
                riddim_server_thread = threading.Thread(
                        target=riddim_server.serve_forever)
                riddim_server_thread.setDaemon(False)
                riddim_server_thread.start()
                print("RiDDiM running at http://%s:%s" % (self.ip,str(self.port)))
                self.data['started_on'] = time.time()
                self.data['port'] = self.port
                self.data['hostname'] = self.ip
                self.data['song'] = ''
                self.data['status'] = 'stopped'
                self.data['index'] = 0
                if self.data['playlist'] is None: self.data['playlist'] = {}
                break
            # FIXME make this not suck at error handling
            # socket busy OK; permission denied (low port) NOT
            except Exception as e:
                print "RiDDiM not running %s" % e
                print "Will try to start again in %d seconds." % INTERVAL
                time.sleep(INTERVAL)
        return (riddim_server, riddim_server_thread)

    def pid(self):
        try:
            return open(self.pidfile,'r').read().strip()
        except IOError:
            return False

    def start(self):
        port = self.o.port
        if not port:
            port=18944

        pid = self.pid()
        if pid and (port is 18944):
            print "RiDDiM already running;  PID:  %s" % pid
            print "If you think RiDDiM is not running, delete %s" % self.rc.config.get('riddim','pidfile')
            sys.exit()
        else:
            if not self.o.foreground:
                daemonize(stderr=self.logfile,stdout=self.logfile)
            pid = os.getpid()
            #print "forked, PID: %d" % pid
            open(self.pidfile,'w').write(str(pid))

        #print "starting on %s" % port
        server,thread = self.kickoff(port)
        sys.exit(0)

    def shutdown(self):
        pid = self.pid()
        open(self.pidfile,'w')
        if pid:
            import signal
            try:
                os.kill(int(pid),signal.SIGTERM)
                print "killed %s" % pid
            except OSError: # already died
                pass
        self.quit()

    def quit(self):
        print "RiDDiM is stopped."
        sys.exit(0)

    def status(self):
        pid = self.pid()
        print "RiDDiM running;  PID:  %s " % pid if pid else "RiDDiM not running"
        sys.exit(0)


if __name__ == '__main__':

    cli = RiddimCLI()

    # handle init signals
    if cli.o.signal == 'start':     cli.start()
    if cli.o.signal == 'stop':      cli.shutdown()
    if cli.o.signal == 'restart':   cli.shutdown(); cli.start();
    if cli.o.signal == 'status':    cli.status()

    # handle flags
    opts = cli.o.options
    # print opts
    if cli.o.flag:
        flag = cli.o.flag
        print flag
        if flag == 'enqueue':
            if not cli.pid(): cli.quit()
            print cli.enqueue(os.path.realpath(opts.enqueue))
        elif flag == 'index':
            print cli.index(opts.index)
        elif flag == 'clear':
            print cli.clear(opts.clear)
        elif flag == 'pause':
            print "||"
            cli.pause()
        elif flag == 'query':
            print cli.query()
        elif flag == 'stop':
            print "."
            cli.stop()
    sys.exit(0)
