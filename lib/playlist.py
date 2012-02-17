import re, os, sys, time, fnmatch, itertools, random, pprint

from lib.logger import log
from lib.audio import Audio
from lib.config import Config
from lib.data import DataManager

class Playlist(object):

    def __init__(self):

        self.config = Config()

        # get data from manager (see lib/server.py)
        DataManager.register('get_data')
        manager = DataManager(address=('', 18945), authkey="riddim")
        manager.connect()
        self.data = manager.get_data()

        # set default playlist data
        default_data = {
                'playlist'      : {},
                'continue'      : True,
                'repeat'        : False,
                'shuffle'       : False,
                'status'        : 'stopped',
                'index'         : 0,
                'song'          : None,
                'skip'          : False
        }
        for k, v in default_data.items():
            try:
                if self.data[k] is None:
                    self.data[k] = default_data[k]
            except KeyError:
                self.data[k] = default_data[k]

        # self.playlist   = sorted(self.data['playlist'].keys())

    def __str__(self):
        index = self.data['index']
        pl = self.data['playlist']
        new_pl = []
        for i,track in pl.iteritems():
            # leader = "*" if int(i) == index and self.data['status'] == 'playing' else " "
            pre = post = " "
            if int(i) == index:
                pre     = "*" * len(pre)
                post    = " "
            new_pl.append(' '.join([pre, '%0*d' % (len(pl[len(pl)-1]),i+1),"[", track['audio']['mimetype'],"] ",track['audio']['title'], post]))

        return '\n'.join(new_pl)

    def __getitem__(self,key):
        return self.data[key]

    def __setitem__(self,key,value):
        self.data[key] = value

    def get_song(self):
        playlist = self.data['playlist']
        if playlist is None:
            return alse
        if self.data['index'] is None:
            self.next()

        try:
            song = playlist[self.data['index']]
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
            return False

    def files_by_pattern(self, path, pattern):
        results = []
        for base, dirs, files in os.walk(path):
            matches = fnmatch.filter(files, pattern)
            results.extend(os.path.realpath(os.path.join(base, m)) for m in matches)
        return results

    def enqueue_list(self, path):
        results = []
        return self.files_by_pattern(path, '*.[mM][pP]3') + self.files_by_pattern(path, '*.[fF][lL][aA][cC]')

    def enqueue(self, paths):
        tracks = 0
        pl = self.data['playlist']
        for path in paths:
            log.info("adding %s" % path)
            eL = self.enqueue_list(path)
            eL.sort()
            track_count = int(len(pl))
            if track_count == 0:    last = 0
            else:                   last = sorted(pl.keys())[-1] + 1

            for i in range(len(eL)):
                ra = Audio(eL[i])
                if ra.corrupt: continue
                pl[i+last] = {
                        'path'      : eL[i],
                        'audio'     : ra.data()
                }
                print ". ",
                sys.stdout.flush()
            print
            tracks += int(len(pl)) - track_count

        self.data['playlist'] = pl
        return "Enqueued %s tracks in %s directories." % (tracks, len(paths))

    def remove(self, index):
        del(self.data[index])

    def status(self):
        return self.data['status']

    def clear(self, regex=None):

        removed = []
        if regex:       # user passed in a regex
            regex           = re.compile(regex,re.IGNORECASE)
            data            = self.data
            old_playlist    = data['playlist']
            pl_keys         = sorted(old_playlist.keys())
            old_index       = data['index']
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
                else:
                    removed.append(pl_key)
                    print "x ",
                    sys.stdout.flush()

            if len(removed) > 0:
                # Then we may need to adjust now-playing pointer.  There
                # are a few possibilities for mutating the playlist:
                #
                #   1) We clobbered the track at the index.  Reset
                #   now-playing to the beginning of the playlist.
                #
                if old_index in removed:
                    data['index'] = 0
                    data['status'] = 'stopped'
                    data['song'] = ''
                    data['skip'] = True
                else:
                #
                #   2) We removed n tracks coming before the index.
                #   Shift now-playing index back n indices.
                #   list or if we clobbered whatever it was pointing to in the
                #   middle of the list.
                    data['index'] = (old_index) - len([t for t in removed if t < old_index])
                #
                #   3) We removed n tracks coming after the index.
                #   No re-ordering necessary

            data['playlist'] = new_playlist
            self.data = data

        else:
            # clear everything
            self.data['playlist'] = {}

        return "%s tracks removed." % len(removed)
        #return self.query()

    def song(self):
        return self.data['song']

    #def current(self):
    #    return self.data['playlist'][self.data['index']]['audio'].title()

    def query(self):

        return """[riddim]  uptime:  %s
%s:  %s
shuffle: %s repeat: %s continue: %s
%s tracks
%s
%s
""" %   (
        self.uptime(),
        self.status(), self.song(),
        self.data['shuffle'], self.data['repeat'], self.data['continue'],
        len(self.data['playlist']),
        30 * '*',
        str(self)
        )

    def index(self, index):

        if index == "+1": # corresponds to arg -n
            self.next()
        else:
            try:
                self.data['index'] = int(index)-1
            except ValueError:
                return "``%s'' is not an integer" % index

        self.data['skip'] = True

        return self.query()

    def uptime(self):
        return time.strftime('%H:%M:%S', time.gmtime(time.time()-self.data['started_at']))

    def kontinue(self):
        self.toggle('continue')

    def repeat(self):
        self.toggle('repeat')

    def shuffle(self):
        self.toggle('shuffle')
        return self.query()

    def next(self):
        if self.data['shuffle']:
            self.data['index'] = random.choice( self.data['playlist'].keys() )
        elif self.data['repeat']:
            pass
        else:
            self.data['index'] += 1

    def toggle(self, key):
        self.data[key] = not(bool(self.data[key]))

if __name__ == '__main__':
    print Playlist()
