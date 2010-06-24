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
        self.data = RiddimData()
        cwd = os.getcwd()
        self.config = RiddimConfig(cwd).config
        # FIXME config
        self.logfile = os.path.join(cwd,'log',self.config.get('riddim','logfile'))
        self.pidfile = os.path.join(cwd,'var','run',self.config.get('riddim','pidfile'))
        self.o = RiddimOptions()

        self.rpc = xmlrpclib.ServerProxy('http://%s:%s' % (self.data['hostname'],self.data['port']), allow_none=True)

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
                print("RiddimServer running at http://%s:%s, in thread:%s" %
                        (self.ip,str(self.port),riddim_server_thread.getName()))
                self.data['started_on'] = time.time()
                self.data['port'] = self.port
                self.data['hostname'] = self.ip
                self.data['song'] = ''
                self.data['status'] = 'stopped'
                if self.data['index'] is None: self.data['index'] = 0
                if self.data['playlist'] is None: self.data['playlist'] = {}
                break
            # FIXME make this not suck at error handling
            # socket busy OK; permission denied (low port) NOT
            except Exception as e:
                print "RiddimServer not running %s" % e
                print "Will try to start again in %d seconds." % INTERVAL
                time.sleep(INTERVAL)
        return (riddim_server, riddim_server_thread)

    def pid(self):
        try:
            return open(self.pidfile,'r').read().strip()
        except IOError:
            return False

    def start(self):
        pid = self.pid()
        if pid:
            print "RiDDiM already running;  PID:  %s" % pid
            print "If you think RiDDiM is not running, delete %s" % self.config.get('riddim','pidfile')
            sys.exit()
        else:
            if not self.o.foreground:
                daemonize(stderr=self.logfile,stdout=self.logfile)
            pid = os.getpid()
            print "forked, PID: %d" % pid
            open(self.pidfile,'w').write(str(pid))

        port = self.o.port
        if port is None:
            port=18944
        server,thread = self.kickoff(port)
        sys.exit(0)

    def stop(self):
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
    if cli.o.signal == 'stop':      cli.stop()
    if cli.o.signal == 'restart':   cli.stop(); cli.start();
    if cli.o.signal == 'status':    cli.status()

    # handle flags
    opts = cli.o.options
    if cli.o.flag:
        flag = cli.o.flag
        if flag == 'enqueue':
            cli.enqueue(opts.enqueue)
        elif flag == 'query':
            print cli.query()
        elif flag == 'clear':
            cli.clear()

    sys.exit(0)
