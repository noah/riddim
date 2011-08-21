import os
import fnmatch
import itertools

from lib.logger import log
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

    def __getitem__(self,key):
        return self.data[key]

    def __setitem__(self,key,value):
        self.data[key] = value

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
            #log.exception("No song at index %s" % I)
            self.data['index'] = 0
            return False
        except KeyError:
            self.data['index'] = 0
            #log.exception("No song at index %s" % I)
            return False
        except Exception, e:
            log.exception(e)

    def files_by_pattern(self, path, pattern):
        results = []
        for base, dirs, files in os.walk(path):
            matches = fnmatch.filter(files, pattern)
            results.extend(os.path.realpath(os.path.join(base, m)) for m in matches)
        return results

    def enqueue_list(self, path):
        results = []
        return self.files_by_pattern(path, '*.[mM][pP]3') + self.files_by_pattern(path, '*.[fF][lL][aA][cC]')

    def enqueue(self, path):
        eL = self.enqueue_list(path)
        eL.sort()
        playlist = self.data['playlist']
        if playlist is None: playlist = {}
        if len(playlist) == 0:  last = 0
        else:                   last = sorted(playlist.keys())[-1] + 1
        #allowable_mimetypes = ['audio/mpeg', 'audio/x-flac']
        for i in range(len(eL)):
            ra = RiddimAudio(eL[i])
            if ra.corrupt: continue
            playlist[i+last] = {
                    'path'      : eL[i],
                    'audio'     : ra.data()
            }
        self.data['playlist'] = playlist

    def remove(self, index):
        # omfg this sucks FIXME
        playlist = self.data['playlist']
        del(playlist[index])
        self.data['playlist'] = playlist

#if __name__ == '__main__':
#    print RiddimPlaylist()
