from lib.data import RiddimData

class RiddimPlaylist(object):

    def __init__(self):
        self.data = RiddimData()
        self.playlist = sorted(self.data['playlist'].keys())

    def get_song(self):
        playlist = self.data['playlist']
        if playlist is None: return False
        I = self.data['index']
        if I is None: I = 0

        try:
            song = playlist[I]
            self.data['status'] = 'playing'
            self.data['song'] = song['mp3'].title()
            return song
        except IndexError:
            print "No song at index %s" % I
            return False
    
    def enqueue_list(self,path):
        results = []
        for base, dirs, files in os.walk(path):
            goodfiles = fnmatch.filter(files,'*.[mM][pP]3')
            #results.extend(os.path.join(base, f) for f in goodfiles)
            results.extend(os.path.realpath(os.path.join(base, f)) for f in goodfiles)
        return results

    def enqueue(self,path):
        eL = self.enqueue_list(path)
        eL.sort()
        playlist = self.data['playlist']
        if playlist is None: playlist = {}
        if len(playlist) == 0:
            last = 0
        else:
            last = sorted(playlist.keys())[-1] + 1

        for i in range(len(eL)):
            print eL[i]
            mp3 = RiddimMP3(eL[i])
            playlist[i+last] = {
                    'path'  : eL[i],
                    'mp3'   : mp3
            }
        self.data['playlist'] = playlist
        # self.data['index'] = str(I)
        # idx = int(self.data['index'])
        # self.data['index'] = idx + 1
        # self.data['status'] = 'stopped'
        # self.data['song'] = ''
