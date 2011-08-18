import os, sys, time, threading, xmlrpclib

from lib.daemonize import daemonize
from lib.data import RiddimData
from lib.config import RiddimConfig
from lib.options import RiddimOptions
from lib.server import RiddimServer
from lib.xmlrpc import RiddimRPCRegisters, RiddimRPCClient
from lib.logger import log, fh

class RiddimCLI(RiddimRPCClient):

    def __init__(self):
        self.rc = RiddimConfig()
        self.data = RiddimData()
        #self.logfile = os.path.join(self.rc.cwd,'log',self.rc.config.get('riddim','logfile'))
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
                log.info("RiDDiM running at http://%s:%s" % (self.ip,str(self.port)))
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
                log.exception("RiDDiM not running %s")
                log.exception("Will try to start again in %d seconds." %\
                        INTERVAL)
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
            log.error("RiDDiM already running;  PID:  %s" % pid)
            log.error("If you think RiDDiM is not running, delete %s" % \
                    self.rc.config.get('riddim','pidfile'))
            sys.exit()
        else:
            if not self.o.foreground:
                daemonize(stderr=fh,stdout=fh)
            pid = os.getpid()
            #print "forked, PID: %d" % pid
            open(self.pidfile,'w').write(str(pid))

        #print "starting on %s" % port
        server,thread = self.kickoff(port)
        sys.exit(0)

    def stop(self):
        pid = self.pid()
        open(self.pidfile,'w')
        if pid:
            import signal
            try:
                os.kill(int(pid),signal.SIGTERM)
                log.info("killed %s" % pid)
            except OSError: # already died
                pass
        self.quit()

    def quit(self):
        log.info("RiDDiM is stopped.")
        sys.exit(0)

    def restart(self):
        self.stop()
        self.start()

    def status(self):
        pid = self.pid()
        log.info("RiDDiM running;  PID:  %s " % pid if pid else "RiDDiM not running")
        sys.exit(0)
