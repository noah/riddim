import re
import os
import sys
import time
import errno
import socket
import threading

from lib.data import Data
from lib.config import Config
from lib.server import Server
from lib.logger import log
from lib.playlist import Playlist

class Riddim():

    def __init__(self, args):

        self.args       = args
        self.config     = Config()
        self.data       = Data()

        #self.rpc = xmlrpclib.ServerProxy('http://%s:%s' %
        #        (self.data['hostname'],self.o.args.port), allow_none=True)

    def kickoff(self, port):
        INTERVAL=2
        for retry in range(1, (int(5 * 60) / INTERVAL)):
            try:
                time.sleep(0.001)
                server      = Server((self.config.hostname, int(port)))
                (ip, port)  = server.server_address
                log.info("server running at http://%s:%s" % (ip, str(port)))
                server_thread = threading.Thread(target=server.serve_forever)
                server_thread.setDaemon(False)
                server_thread.start()
                break
            except socket.error, se:
                if se.errno == errno.EACCES:
                    log.warn("Bad port: %s" % port)
                    sys.exit( se.errno )
            #except Exception as e:
            #    log.exception("Startup exception.  Will try to start again in %d seconds." % INTERVAL)
            #    time.sleep(INTERVAL)
        return server

    def pid(self):
        try:
            return open(self.config.pidpath, 'r').read().strip()
        except IOError:
            return False

    def start(self):
        port = self.config.port

        pid = self.pid()
        if pid:
            log.error("Server already running;  PID:  %s" % pid)
            log.error("Try: rm %s" % self.config.pidpath)
            sys.exit(-1)
        else:
            pid = os.getpid()
            open(self.config.pidpath, 'w').write(str(pid))

        server = self.kickoff( port )
        sys.exit(0)

    def stop(self):
        pid = self.pid()
        open(self.config.pidpath,'w')
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

    def enqueue(self, paths):
        tracks = 0
        try:
            playlist = Playlist()
            for path in paths:
                log.debug("adding %s" % path)
                tracks += playlist.enqueue(path)
        except Exception, e:
            log.exception(e)
        return "Enqueued %s tracks in %s directories." % (tracks,
                len(self.args.enqueue))

    def status(self):
        return self.data['status']

    def clear(self, regex=None):

        removed = []
        if regex:       # user passed in a regex
            regex           = re.compile(regex,re.IGNORECASE)
            data            = self.data
            old_playlist    = data['playlist']
            pl_keys         = sorted(old_playlist.keys())
            old_index       = data['index']
            new_playlist    = {}

            i = 0
            for pl_key in pl_keys:
                title = old_playlist[pl_key]['audio']['title']
                # If the track does not match the removal regex (i.e.,
                # should be kept), then append it and increment the
                # index
                if not re.search(regex, title):
                    new_playlist[i] = old_playlist[pl_key]
                    i = i+1
                else:
                    removed.append(pl_key)
                    print "x ",
                    sys.stdout.flush()

            if len(removed) > 0:
                # Then we may need to adjust now-playing pointer.  There
                # are a few possibilities for mutating the playlist:
                #
                #   1) We clobbered the track at the index.  Reset
                #   now-playing to the beginning of the playlist.
                #
                if old_index in removed: data['index'] = 0
                else:
                #
                #   2) We removed n tracks coming before the index.
                #   Shift now-playing index back n indices.
                #   list or if we clobbered whatever it was pointing to in the
                #   middle of the list.
                    data['index'] = (old_index) - len([t for t in removed if t < old_index])
                #
                #   3) We removed n tracks coming after the index.
                #   No re-ordering necessary

            data['playlist'] = new_playlist
            self.data = data

        else:
            # clear everything
            self.data['playlist'] = {}

        return "%s tracks removed." % len(removed)
        #return self.query()

    def song(self):
        return self.data['song']

    #def current(self):
    #    return self.data['playlist'][self.data['index']]['audio'].title()

    def query(self):

        return """[riddim]  uptime:  %s
%s:  %s
%s tracks %s
%s
""" %   (
        self.uptime(),
        self.status(),
        self.song(),
        len(self.data['playlist']),
        30 * '*',
        Playlist(),
        )

    def index(self, index):
        try:
            self.data['index'] = int(index)-1
            self.data['index_changed'] = True
        except ValueError:
            return "``%s'' is not an integer" % index

        return self.query()

    def uptime(self):
        return time.strftime('%H:%M:%S',time.gmtime(time.time()-self.data['started_on']))
