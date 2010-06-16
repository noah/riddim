import sys
import socket
import threading


from lib.options import RiddimOptions
from lib.client import RiddimClient
from lib.server import RiddimServer



if __name__ == '__main__':
    riddim_options = RiddimOptions()
    if riddim_options.signal:
        if riddim_options.signal == "start":
            print """
                RiDDiM v0.1
            """

            riddim_server = RiddimServer(('localhost',18449)).server
            ip, port = riddim_server.server_address

            t = threading.Thread(target=riddim_server.serve_forever)
            t.setDaemon(not riddim_options.foreground)
            t.start()

            print "Server started at http://localhost:%s" % port

        # if riddim_options.signal == "stop":
        #     s = xmlrpclib.ServerProxy('http://localhost:18944')
        #     s.shutdown()

    #else:
    #    if riddim_options.flag:
    #        #print "running %s flag" % riddim_options.flag
    #        sys.exit(0)
