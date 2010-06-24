from lib.data import RiddimData

class RiddimPlaylist(object):

    def __init__(self):
        self.data = RiddimData()
        self.playlist = sorted(eval(self.data['playlist']).keys())

    def get_song(self):
        playlist = eval(self.data['playlist']).keys()
        if playlist is None: return False
        I = int(self.data['index'])
        if I is None: I = 0
    
        try:
            song = playlist[I]
            self.data['status'] = 'playing'
            self.data['song'] = song
            return song
        except IndexError:
            print "No song at index %s" % I
            return False
    
        # self.data['index'] = str(I)
        # idx = int(self.data['index'])
        # self.data['index'] = idx + 1
        # self.data['status'] = 'stopped'
        # self.data['song'] = ''
