import os
import sys
import fnmatch
import itertools

from lib.data import RiddimData
class RiddimRPCRegisters(object):
    """ 
        These are the commands that the local server accepts via XMLRPC
        from remote clients
    """

    def __init__(self,server):
        self.server = server
        self.data = RiddimData()

    def query(self):
        playlist = self.playlist()
        return """
%s:  %s
%s songs %s
%s
""" %   ( 
        self.status(),
        self.song(),
        len(playlist),
        20 * '*',
        playlist,
        )

    def playlist(self):
        index = self.data['index']
        pl = self.data['playlist'].keys()
        new_pl = []
        for i in range(len(pl)):
            leader = "*" if int(i) == index and self.data['status'] == 'playing' else " "
            new_pl.append(''.join([leader,pl[i]]))
        return "\n".join(new_pl)

    def clear(self):
        self.data['playlist'] = '{}'

    def song(self):
        return self.data['song']
    
    def status(self):
        return self.data['status']

    def stop(self):
        self.data['status'] = 'stopped'

    def play(self):
        self.data['status'] = 'playing'

    def pause(self):
        self.data['status'] = 'paused'

    def current(self):
        print "index is %s" % self.data['index']
        return self.data['playlist'].keys()[self.data['index']]

    def next(self):
        if self.data['index']+1 != len(self.data['playlist'].keys()):
            self.data['index'] += 1
        else:
            self.data['index'] = 0
        self.data['next'] = True
        return self.current()

    def previous(self):
        if self.data['index']-1 != len(self.data['playlist'].keys()):
            self.data['index'] -= 1
        else:
            self.data['index'] = 0
        self.data['previous'] = True
        return self.current()

class RiddimRPCClient(object):
    """ XMLRPC client wrappers """

    def query(self):
        return self.rpc.query()

    def clear(self):
        return self.rpc.clear()

    def stop(self):
        return self.rpc.stop()

    def pause(self):
        return self.rpc.pause()

    def play(self):
        return self.rpc.play()

    def next(self):
        return self.rpc.next()

    def previous(self):
        return self.rpc.previous()

    def enqueue_list(self,path):
        results = []
        for base, dirs, files in os.walk(path):
            goodfiles = fnmatch.filter(files,'*.[mM][pP]3')
            #results.extend(os.path.join(base, f) for f in goodfiles)
            results.extend(os.path.realpath(os.path.join(base, f)) for f in goodfiles)
        return results

    def enqueue(self,path):
        if not self.pid(): self.quit()
        eL = self.enqueue_list(path)
        eL.sort()
        playlist = self.data['playlist']
        if playlist is None: 
            playlist = {}
        for path in eL:
            # TODO:  metadata in v, sorting, blah
            playlist[path] = {}
        self.data['playlist'] = playlist
