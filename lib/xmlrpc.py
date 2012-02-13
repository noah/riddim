import os, re, copy, time

from lib.logger import log
from lib.data import RiddimData
from lib.playlist import RiddimPlaylist

class RiddimRPCRegisters(object):
    """
        These are the commands that the local server accepts via XMLRPC
        from remote clients
    """

    def __init__(self,server):
        #self.server = server
        self.data = RiddimData()

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
        RiddimPlaylist(),
        )

    def uptime(self):
        return time.strftime('%H:%M:%S',time.gmtime(time.time()-self.data['started_on']))

    def index(self,index):
        try:
            self.data['index'] = int(index)-1
            self.data['index_changed'] = True
        except ValueError:
            return "``%s'' is not an integer" % index

        return self.query()

    def clear(self,regex=None):

        if regex:       # user passed in a regex
            regex           = re.compile(regex,re.IGNORECASE)
            data            = self.data
            old_playlist    = data['playlist']
            pl_keys         = sorted(old_playlist.keys())
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

            log.debug("done looping ")

            lpl = len(new_playlist.keys())
            if data['index'] >= lpl: data['index'] = 0
            data['playlist'] = new_playlist
            self.data = data

        else:
            # Clear everything
            self.data['playlist'] = {}

        return self.query()

    def song(self):
        return self.data['song']

    def status(self):
        return self.data['status']

    def stop(self):
        self.data['status'] = 'stopped'

    #def play(self):
    #    self.data['status'] = 'playing'

    def pause(self):
        self.data['status'] = 'paused'

    def current(self):
        return self.data['playlist'][self.data['index']]['audio'].title()

    # def next(self,n):
    #     lpl = len(self.data['playlist'].keys())
    #     self.data['index'] += int(n)
    #     if self.data['index'] >= lpl: self.data['index'] = lpl-1
    #     self.data['next'] = True
    #     return self.query()

    # def previous(self,n):
    #     self.data['index'] -= int(n)
    #     if self.data['index'] < 0: self.data['index'] = 0
    #     self.data['previous'] = True
    #     return self.query()

    def enqueue(self,path):
        try:
            rp = RiddimPlaylist()
            rp.enqueue(path)
        except Exception, e:
            log.exception(e)

class RiddimRPCClient(object):
    """ XMLRPC client wrappers """

    def query(self):
        return self.rpc.query()

    def clear(self,regex):
        return self.rpc.clear(regex)

    def index(self,i):
        return self.rpc.index(i)

    def stop(self):
        return self.rpc.stop()

    def pause(self):
        return self.rpc.pause()

    #def play(self):
    #    return self.rpc.play()

    #def next(self,n):
    #    return self.rpc.next(n)

    #def previous(self,n):
    #    return self.rpc.previous(n)

    def enqueue(self,path):
        p = os.path.realpath(os.path.relpath(path, self.cwd))
        self.rpc.enqueue(p)
        return self.rpc.query()
