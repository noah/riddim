import os
import sys
import time
import threading

from lib.daemonize import daemonize
from lib.options import RiddimOptions
from lib.client import RiddimClient
from lib.server import RiddimServer

def start_server(port):
    MINUTE=60
    INTERVAL=30
    for retry in range(1, (int(5 * MINUTE) / INTERVAL)):
        try:
            riddim_server = RiddimServer(('localhost',int(port)))
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
            print "Will try to start again in %d seconds." % 30
            time.sleep(INTERVAL)
    return (riddim_server, riddim_server_thread)

def hello():
    print """
        RiDDiM v0.1
    """

def pid(p):
    try:
        return open(p,'r').read().strip()
    except IOError:
        return False

if __name__ == '__main__':
    w = os.getcwd()
    L = os.path.join(w,'riddim.log')
    p = os.path.join(w,'riddim.pid')
    o = RiddimOptions()

    pid = pid(p)
    if o.signal == 'start':
        hello()

        if pid:
            print "RiDDiM already running;  PID:  %s" % pid
            sys.exit()
        else:
            if not o.foreground:
                daemonize(stderr=L,stdout=L)
            pid = os.getpid()
            print "forked, PID: %d" % pid
            open(p,'w').write(str(pid))

        try:
            port = o.port
        except:
            port = 18944
        print port
        server, thread = start_server(port)
        
    if o.signal == "stop":
        open(p,'w')
        if pid:
            import signal
            try:
                os.kill(int(pid),signal.SIGTERM)
                print "killed %s" % pid
            except OSError: # already died
                pass
        print "RiDDiM is stopped."
        #TODO s = xmlrpclib.ServerProxy('http://localhost:18944')
        #s.shutdown()

    #else:
    #    if riddim_options.flag:
    #        #print "running %s flag" % riddim_options.flag
    #        sys.exit(0)
