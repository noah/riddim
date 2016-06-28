# -*- coding: utf-8 -*-

from os import walk
from os.path import isfile, realpath, join, isdir
import re
import sys
import math
import codecs
import random
import cPickle as pickle
from datetime import datetime
from socket import error as socket_error

from lib.config     import Config
from lib.logger     import log
from lib.song       import Song
from lib.data       import DataManager
from lib.util       import is_stream, filesizeformat, seconds_to_time

label_bool      = {True: u'on', False: u'off'}
label_status    = {u"stopped" : u".", u"playing" : u">"}


class PlaylistFile(object):

    @staticmethod
    def read():
        try:
            # Read an existing file
            with codecs.open( Config.datapath, u'rb' ) as picklef:
                data = pickle.load( picklef )
                assert type(data) == dict
        except:
            # File non-existent or corrupt.
            PlaylistFile.truncate()
            return {}

        return data

    @staticmethod
    def truncate():
        try:
            codecs.open(Config.datapath, u'wb')
            return True
        except Exception, e:
            log.exception(e)
        return False

    @staticmethod
    def save(data):
        try:
            with codecs.open( Config.datapath, u'wb') as picklef:
                pickle.dump(data, picklef)
            return True
        except Exception, e:
            log.exception(e)
        return False


def crunch(path):
    return Song(path)


class Playlist(object):

    def __init__(self, port, pool):

        self.pool = pool
        self.port = port
        self.set_data()

    def set_data(self):
        try:
            # get data from manager (see lib/server.py)
            DataManager.register('get_data')

            # manager port is one higher than listen port
            manager = DataManager(address=(Config.hostname, self.port + 1),
                    authkey=Config.authkey)
            manager.connect()
        except socket_error as serr:
            import errno
            if serr.errno != errno.ECONNREFUSED: raise serr
            log.error("Connection refused.")
            sys.exit()

        self.data       = manager.get_data()
        playlist_data   = None
        try:                playlist_data = self.data['playlist']
        except KeyError:    playlist_data = PlaylistFile.read()

        if playlist_data is None:
            playlist_data = PlaylistFile.read()

        # set default playlist data
        default_data = {
                u'playlist'      : playlist_data,
                u'continue'      : False,
                u'repeat'        : False,
                u'shuffle'       : False,
                u'status'        : u'stopped',
                u'index'         : 0,
                u'song'          : None,
                u'skip'          : False,
                u'sum_bytes'     : 0,
                u'progress'      : 0,
                u'elapsed'       : 0,
        }
        for k, v in default_data.items():
            try:
                if self.data[k] is None:
                    self.data[k] = default_data[k]
            except KeyError:
                self.data[k] = default_data[k]

    def __str__(self):
        index   = self.data[u'index']
        pl      = self.data[u'playlist']
        new_pl  = []
        pl_len  = len(pl)
        if pl_len > 0:
            pad_digits = int(math.log10(pl_len)) + 1
        else:
            pl_len = 0
        for i, song in pl.iteritems():
            #try:
            pre = post = u" "
            if int(i) == index:
                pre     = u"*" * len(pre)
                post    = u" "
            probable_filetype = Config.audio_types[song.mimetype]
            if probable_filetype == u'?':
                probable_filetype = song.ext
            new_pl.append(' '.join([
                pre,
                u'%*d' % (pad_digits, i + 1),
                u"[", probable_filetype , u"]",
                u"{}".format(song),
                post
            ]))
            #except:
            #    log.exception(song)
        return u'\n'.join(new_pl)

    def __getattr__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def get_song(self):
        song    = None
        index   = self.data[u'index']
        if index == -1: return None
        try:                song = self.song()
        except KeyError:    return None

        self.data[u'status'] = u'playing'
        self.data[u'song']   = song

        return song

    def enqueue_list(self, path, extensions=None):
        if extensions:  wantfile = lambda x: x.endswith(extensions)
        else:           wantfile = lambda _: True
        results = []
        for base, dirs, files in walk(path):
            results.extend( realpath( join(base, f) ) for f in files if wantfile(f) )
        return results

    def enqueue(self, args, extensions=None):
        tracks  = streams = 0
        pl      = self.data[u'playlist']

        for arg in args:

            log.info(u"+ {}".format(arg.decode('utf-8')))
            elist = None

            if isfile( arg ):       elist = [ realpath( arg ) ]
            elif is_stream( arg ):  raise NotImplementedError # TODO
            else:
                try:    assert isdir( arg )
                except: print "{} is not a directory.".format(arg)
                elist = self.enqueue_list( arg, extensions )
                elist.sort()

            if elist is not None:
                track_count = int(len(pl))
                if track_count == 0:    last = 0
                else:                   last = sorted(pl.keys())[-1] + 1

                songs = self.pool.map(crunch, elist)

                for i, song in enumerate( songs ):
                    if song.corrupt: continue
                    pl[i + last] = song
                tracks += int(len(pl)) - track_count

        #try:
        self.data[u'playlist'] = pl
        #except Exception, e:
        #    log.exception(e)

        # reached end of playlist, reset index
        if self.data[u'status'] == u'stopped' and int(self.data[u'index']) == - 1:
            self.data[u'index'] = 0

        return u"Enqueued %s tracks in %s directories (%s streams)." % (tracks,
                                                                       len(args), streams)

    def remove(self):
        index = int(self.data[u'index'])
        pl = self.data[u'playlist']
        del pl[index]
        self.data[u'playlist'] = pl
        self.next()

    # TODO clear() should call remove(); cli should call remove to strip
    # would also be nice to return a list of *artists* whose tracks were
    # removed
    # by int
    def clear(self, userregex=None, extensions=None):

        try:
            removed = []
            if userregex:           # user passed in a regex
                regex           = re.compile(userregex, re.IGNORECASE)
                data            = self.data
                old_playlist    = data[u'playlist']
                pl_keys         = sorted(old_playlist.keys())
                old_index       = data[u'index']
                new_playlist    = {}
                have_extensions = extensions is not None

                # for each song
                i = 0
                for pl_key in pl_keys:
                    old_song        = old_playlist[pl_key]
                    regex_match     = bool(re.search(regex, unicode(old_song)))

                    # Do some pruning:
                    prune = regex_match

                    # if user passed extensions, only prune if the extension
                    # matches
                    if have_extensions:
                        prune = regex_match and old_song.path.endswith(extensions)

                    if prune:
                        removed.append(pl_key)
                        print u"x ",
                        sys.stdout.flush()
                    else:
                        new_playlist[i] = old_playlist[pl_key]
                        i = i + 1

                if len(removed) > 0:
                    # Then we may need to adjust now-playing pointer.  There
                    # are a few possibilities for mutating the playlist:
                    #
                    #   1) We clobbered the track at the index.  Reset
                    #   now-playing to the beginning of the playlist.
                    #
                    if old_index in removed:
                        data[u'index'] = 0
                        data[u'status'] = u'stopped'
                        data[u'song'] = u''
                        data[u'skip'] = True
                    else:
                    #
                    #   2) We removed n tracks coming before the index.
                    #   Shift now-playing index back n indices.
                    #   list or if we clobbered whatever it was pointing to in the
                    #   middle of the list.
                        data[u'index'] = (old_index) - len([t for t in removed if t < old_index])
                    #
                    #   3) We removed n tracks coming after the index.
                    #   No re-ordering necessary

                    data[u'playlist'] = new_playlist
                    self.data = data

            else:
                # clear everything
                self.data[u'playlist'] = {}

            nr = len(removed)
            if nr > 0:
                print u"{} tracks removed.".format(nr)
                return self.query(lines=10)
            return "no matches for regex `{}'".format(userregex)

            # index           = self.data['index'] + 1
            # pl_len          = len(self.data['playlist'])
            # shuffle         = label_bool[self.data['shuffle']]
            # repeat          = label_bool[self.data['repeat']]
            # kontinue        = label_bool[self.data['continue']]
            # pad             = (72 - len(name) + 1) * '*'
            # Self            = unicode(self)
            # if self.status == "playing":
            #     percentage = int(( / song.size) / 100.0)
            # else:
            #     percentage = 0
        except:
            print type(old_song)
            print(old_song is None)

    def query(self, lines=0):
        name            = u"riddim"
        uptime          = self.uptime()
        status_symbol   = label_status[ self.status ]
        song            = self.get_song()
        #
        width           = 72
        fill            = u'='
        blank           = u'.'
        step            = 100 / float(width)
        #
        q               = []
        q.append(u"{} up {} sent {} total continue {} shuffle {} repeat {} index {}".format(
            name, uptime, filesizeformat(self.data["sum_bytes"]),
            self.data[u"continue"],
            self.data[u"shuffle"],
            self.data[u"repeat"],
            self.data[u"index"]
        ))
        q.append(u"{} {}".format(status_symbol, song))
        if self.status == u"playing":
            percentage      = int(self.data[u"progress"] / step)
            fill            = percentage * u'='
            blank           = (width - percentage) * u'.'
            q.append(u"{} {} [{}>{}] {}%".format(
                    seconds_to_time(self.data[u"elapsed"]), seconds_to_time(song.length), fill, blank, percentage))
            q.append(u"{} ({})".format( self.data[u"progress"], song.length) )
            q.append(u"{}".format(  self  ))

        if lines > 0:
            q = q[:lines]
            q.append('...')
        return u"\n".join( q )

    def index(self, index, _):

        if index == u"+1":  # corresponds to option -n with no argument
            self.next()
        else:
            try:
                new_index   = int(index) - 1
                (first_index, last_index) = self.index_bounds()
                if new_index > last_index:      new_index = last_index
                elif new_index < first_index:   new_index = first_index
                self.data[u'index'] = new_index
            except ValueError:
                return u"``{}'' is not an integer".format(index)

        if self.data[u'status'] == 'playing':
            self.data[u'skip'] = True

        return self.query(lines=10)

    def index_bounds(self):
        sorted_indices = sorted(self.data[u'playlist'].keys())
        try:
            return (sorted_indices[0], sorted_indices[-1])
        except IndexError:
            return (0, 0)

    def uptime(self):
        delta = datetime.now() - self.data[u'started_at']
        hours, _ = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(_, 60)
        return u"%sd %02dh %02dm %02ds" % \
               (delta.days, hours, minutes, seconds)

    def kontinue(self):
        self.toggle(u'continue')
        return self.query()

    def song(self):
        return self.data[u'playlist'][self.data[u'index']]

    def next_album(self):
        album_this = self.song().album
        while True:
            self.next()
            album_next = self.song().album
            if album_this != album_next: break
        return self.query()

    def next_artist(self):
        artist_this = self.song().artist.lower()
        while True:
            self.next()
            artist_next = self.song().artist.lower()
            if artist_this != artist_next: break
        return self.query()

    def repeat(self):
        self.toggle(u'repeat')
        return self.query()

    def shuffle(self):
        self.toggle(u'shuffle')
        return self.query()

    def next(self):
        if self.data[u'shuffle']:
            self.data[u'index'] = random.choice( self.data[u'playlist'].keys() )
        elif self.data[u'repeat']:
            pass
        else:
            new_index = int(self.data[u'index'] + 1)
            if not self.data[u'continue']:
                # prevent rollover
                first_index, last_index = self.index_bounds()
                if new_index > last_index:
                    self.data[u'index'] = 0
                    return
            self.data[u'index'] = new_index

    def toggle(self, key):
        self.data[key] = not(bool(self.data[key]))

    def save(self):
        PlaylistFile.save( self.data[u'playlist'] )
        # TODO
        #PlaylistFile.save( self.data )
