import os
import sys
import fnmatch
import itertools

from lib.mp3 import RiddimMP3
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
Playlist: %s:  %s
%s tracks %s
%s
""" %   ( 
        self.status(),
        self.song(),
        len(self.data['playlist']),
        30 * '*',
        playlist,
        )

    def playlist(self):
        index = self.data['index']
        pl = self.data['playlist']
        new_pl = []
        for i in range(len(pl)):
            leader = "* " if int(i) == index and self.data['status'] == 'playing' else "  "
            new_pl.append(''.join([leader,pl[i]['mp3'].title()]))
        return "\n".join(new_pl)

    def clear(self):
        self.data['playlist'] = {}

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
        return self.data['playlist'][self.data['index']]['mp3'].title()

    def next(self):
        if self.data['index']+1 != len(self.data['playlist'].keys()):
            self.data['index'] += 1
        else:
            self.data['index'] = 0
        self.data['next'] = True
        return self.query()

    def previous(self):
        if self.data['index']-1 != len(self.data['playlist'].keys()):
            self.data['index'] -= 1
        else:
            self.data['index'] = 0
        self.data['previous'] = True
        return self.query()

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

    #def play(self):
    #    return self.rpc.play()

    def next(self):
        return self.rpc.next()

    def previous(self):
        return self.rpc.previous()

    #def enqueue(self,path):
    #    self.rpc.enqueue(path)
