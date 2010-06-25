import time
from lib.data import RiddimData
from lib.playlist import RiddimPlaylist

class RiddimRPCRegisters(object):
    """ 
        These are the commands that the local server accepts via XMLRPC
        from remote clients
    """

    def __init__(self,server):
        self.server = server
        self.data = RiddimData()

    def query(self):
        return """-=[RiDDiM]=-  uptime:  %s
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

    def enqueue(self,path):
        rp = RiddimPlaylist()
        rp.enqueue(path)

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

    def enqueue(self,path):
        self.rpc.enqueue(path)
