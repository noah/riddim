import os
import sys
import fnmatch
import itertools

from lib.data import RiddimData

class RiddimRPCClient(object):
    """ XMLRPC client wrappers """

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
        else:
            playlist = eval(playlist)
        for path in eL:
            # TODO:  metadata in v, sorting, blah
            playlist[path] = {}
        self.data['playlist'] = playlist


    def query(self):
        return self.rpc.query()

    def clear(self):
        return self.rpc.clear()


class RiddimRPCRegisters(object):
    """ The commands that the server accepts via XMLRPC"""

    def __init__(self,server):
        self.server = server
        self.data = RiddimData()

    def query(self):
        return """
%s:  %s
%s
%s
""" %   ( 
        self.status(),
        self.song(),
        20 * '*',
        self.playlist(),
        )

    def playlist(self):
        pl = eval(self.data['playlist'])
        paths = pl.keys()
        return sorted(paths)

    def clear(self):
        self.data['playlist'] = '{}'

    def song(self):
        return self.data['song']
    
    def status(self):
        return self.data['status']
