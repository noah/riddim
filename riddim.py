import os
import sys
import time
import threading

from lib.daemonize import daemonize
from lib.options import RiddimOptions
from lib.client import RiddimClient
from lib.server import RiddimServer

class Riddim:
    def __init__(self):
        self.cwd = os.getcwd()
        self.media_dir = os.path.join(self.cwd,'mp3')
        self.logfile = os.path.join(self.cwd,'riddim.log')
        self.pidfile = os.path.join(self.cwd,'riddim.pid')
        self.o = RiddimOptions()

    def start_server(self,port):
        MINUTE=60
        INTERVAL=2
        for retry in range(1, (int(5 * MINUTE) / INTERVAL)):
            try:
                time.sleep(0.001)
                riddim_server = RiddimServer(('0.0.0.0',int(port)),self.media_dir)
                ip, port = riddim_server.server_address
                riddim_server_thread = threading.Thread(
                        target=riddim_server.serve_forever)
                riddim_server_thread.setDaemon(False)
                riddim_server_thread.start()
                print("RiddimServer running at http://%s:%s, in thread:%s" %
                        (ip,str(port),riddim_server_thread.getName()))
                break
            # FIXME make this not suck at error handling
            # socket busy OK; permission denied (low port) NOT
            except Exception as e:
                print "RiddimServer not running %s" % e
                print "Will try to start again in %d seconds." % INTERVAL
                time.sleep(INTERVAL)
        return (riddim_server, riddim_server_thread)

    def hello(self):
        print """
            RiDDiM
        """

    def pid(self):
        try:
            return open(self.pidfile,'r').read().strip()
        except IOError:
            return False

    def start(self):
        pid = self.pid()
        if pid:
            print "RiDDiM already running;  PID:  %s" % pid
            print "If you think RiDDiM is not running, delete riddim.pid"
            sys.exit()
        else:
            print "RiDDiM running on http://localhost:%s" % self.o.port
            if not self.o.foreground:
                daemonize(stderr=self.logfile,stdout=self.logfile)
            pid = os.getpid()
            print "forked, PID: %d" % pid
            open(self.pidfile,'w').write(str(pid))

        server, thread = self.start_server(self.o.port)

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
        print "RiDDiM is stopped."

    def status(self):
        pid = self.pid()
        print "RiDDiM running;  PID:  %s " % pid if pid else "RiDDiM not running"

if __name__ == '__main__':
    
    riddim = Riddim()
    if riddim.o.signal == 'start':     riddim.start()
    if riddim.o.signal == "stop":      riddim.stop()
    if riddim.o.signal == 'restart':   riddim.stop(); riddim.start();
    if riddim.o.signal == 'status':    riddim.status()

    #    if riddim_options.flag:
    #        #print "running %s flag" % riddim_options.flag
    #        sys.exit(0)
