import os
import fnmatch
import itertools

from lib.data import RiddimData
from lib.audio import RiddimAudio

class RiddimPlaylist(object):

    def __init__(self):
        self.data = RiddimData()
        self.playlist = sorted(self.data['playlist'].keys())

    def __str__(self):
        index = self.data['index']
        pl = self.data['playlist']
        new_pl = []
        for i,track in pl.iteritems():
            # leader = "*" if int(i) == index and self.data['status'] == 'playing' else " "
            leader = "*" if int(i) == index else " "
            new_pl.append(' '.join([leader,'%0*d' %
                (len(pl[len(pl)-1]),i+1),"[", track['audio']['mimetype'],"] ",track['audio']['title']]))
        return '\n'.join(new_pl)

    def get_song(self):
        playlist = self.data['playlist']
        if playlist is None: return False
        I = self.data['index']
        if I is None or I > len(playlist): I = 0

        try:
            song = playlist[I]
            self.data['status'] = 'playing'
            self.data['song'] = song['audio']['title']
            return song
        except IndexError:
            print "No song at index %s" % I
            return False
        except KeyError:
            print "No song at index %s" % I
            return False

    def files_by_pattern(self,path,pattern):
        results = []
        for base, dirs, files in os.walk(path):
            matches = fnmatch.filter(files, pattern)
            results.extend(os.path.realpath(os.path.join(base, m)) for m in matches)
        return results

    def enqueue_list(self,path):
        results = []
        print "Enqueuing %s" % path
        return self.files_by_pattern(path, '*.[mM][pP]3') + self.files_by_pattern(path, '*.[fF][lL][aA][cC]')

    def enqueue(self,path):
        eL = self.enqueue_list(path)
        eL.sort()
        playlist = self.data['playlist']
        if playlist is None: playlist = {}
        if len(playlist) == 0:
            last = 0
        else:
            last = sorted(playlist.keys())[-1] + 1
        #allowable_mimetypes = ['audio/mpeg', 'audio/x-flac']
        for i in range(len(eL)):
            ra = RiddimAudio(eL[i])
            if ra.corrupt: continue
            playlist[i+last] = {
                    'path'      : eL[i],
                    'audio'     : ra.data()
            }
        self.data['playlist'] = playlist

#if __name__ == '__main__':
#    print RiddimPlaylist()
