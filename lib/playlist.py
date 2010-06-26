import os
import magic
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
        for i in range(len(pl)):
            leader = "* " if int(i) == index and self.data['status'] == 'playing' else "  "
            new_pl.append(''.join([leader,pl[i]['audio']['title']]))
        return "\n".join(new_pl)

    def get_song(self):
        playlist = self.data['playlist']
        if playlist is None: return False
        I = self.data['index']
        if I is None: I = 0

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
    
    def enqueue_list(self,path):
        results = []
        for base, dirs, files in os.walk(path):
            mp3 = fnmatch.filter(files,'*.[mM][pP]3')
            # TODO flac
            results.extend(os.path.realpath(os.path.join(base, f)) for f in mp3)
        return results

    def enqueue(self,path):
        print "path is %s " % path
        eL = self.enqueue_list(path)
        print eL
        eL.sort()
        playlist = self.data['playlist']
        if playlist is None: playlist = {}
        if len(playlist) == 0:
            last = 0
        else:
            last = sorted(playlist.keys())[-1] + 1

        allowable_mimetypes = ['audio/mpeg', 'audio/x-flac']
        m = magic.open(magic.MAGIC_MIME)
        m.load()
        for i in range(len(eL)):
            mimetype = False
            try:
                mimetype = m.file(eL[i]).split(';')[0]
            except:
                pass
            if not mimetype or mimetype not in allowable_mimetypes:
                print "couldn't process %s.  mimetype:  %s" % (eL[i],mimetype)
                continue
            playlist[i+last] = {
                    'path'      : eL[i],
                    'audio'     : RiddimAudio(eL[i],mimetype).data()
            }
        self.data['playlist'] = playlist
