import os, time, errno, socket, subprocess, Queue, signal
import mad

#from lib.data import Data
from lib.config import Config
from lib.scrobble import Scrobbler, ScrobbleItem, NOW_PLAYING, PLAYED
from lib.logger import log
from lib.playlist import Playlist


class Streamer(object):

    def __init__(self, request):

        self.playlist       = Playlist()
        #self.playlist       = sorted(self.data['playlist'].keys())
        self.request        = request
        self.byte_count     = 0
        self.total_bytes    = 0

        if Config.scrobble:

            self.scrobble_queue = Queue.Queue()
            self.scrobbler      = Scrobbler( self.scrobble_queue ).start()

    # It's always a good day for smoking crack at Nullsoft!
    #   See the Amarok source for ideas on the (crappy) icecast metadata "protocol"
    #           This explains the whole cockamamie thing:
    #           http://www.smackfu.com/stuff/programming/shoutcast.html


    def get_meta(self, song):
        # lifted from amarok
        metadata    = "%cStreamTitle='%s';StreamUrl='%s';%s"
        padding     = '\x00' * 16
        meta        = None
        if self.dirty_meta:
            stream_title    = song['audio']['title'].encode('ascii', 'ignore')
            stream_url      = Config.url

            # 28 is the number of static characters in metadata (!)
            length          = len(stream_title) + len(stream_url) + 28
            pad             = 16 - length % 16
            what = padding[:pad]
            meta            = metadata % (((length+pad)/16), stream_title, stream_url, what)
            self.dirty_meta = False
        else:
            meta = '\x00'

        return meta

    def empty_scrobble_queue(self):
        if Config.scrobble:
            with self.scrobble_queue.mutex:
                self.scrobble_queue.queue.clear()

    def stream(self, icy_client=False):
        f = None
        song = None
        while True:
            if Config.scrobble:
                if song:
                    self.scrobble_queue.put(ScrobbleItem(PLAYED, song)) # just played one . . . scrobble it
                    #log.debug("enqueued played")

            # new song
            song = self.playlist.get_song()

            if not song:
                log.info("no playlist, won't stream"); return
                self.byte_count = 0
                self.empty_scrobble_queue()
                return

            if Config.scrobble:
                #log.debug("enqueued now playing")
                self.scrobble_queue.put(ScrobbleItem(NOW_PLAYING, song))

            log.info('> %s' % song['audio']['title'])

            flac_pipe = mp3_pipe = None
            try:
                # sorry code gods
                flac = False

                # this loop gets some of its ideas about the shoutcast protocol from Amarok
                buffer              = 0
                buffer_size         = 1024
                metadata_interval   = Config.metaint

                try:
                    f.close()
                except:
                    pass

                if song['audio']['mimetype'] == 'audio/x-flac':
                    flac_pipe = subprocess.Popen(
                            "/usr/bin/flac --silent -d \"%s\" --stdout" % song['path'],
                            stdout=subprocess.PIPE,
                            shell=True)
                    mp3_pipe = subprocess.Popen(
                            "/usr/bin/lame --quiet -V0 - -",
                            stdout=subprocess.PIPE,
                            shell=True,
                            stdin = flac_pipe.stdout)
                    f = mp3_pipe.stdout
                    flac = True
                else: # assume mp3
                    try:
                        f = file(song['path'], 'r')
                        f.seek(song['audio']['start'])
                    except IOError:
                        #import pprint
                        # file deleted?
                        log.warn("removing %s.  file deleted?" % song['path'])
                        self.playlist.remove()
                        self.empty_scrobble_queue()
                        song = None
                        continue

                self.dirty_meta = True

                audio_size = song['audio']['size']
                skip = False
                i=0
                while flac or (f.tell() < audio_size):
                    bytes_until_meta = (metadata_interval - self.byte_count)
                    if bytes_until_meta == 0:
                        if icy_client:
                            metadata = self.get_meta(song)
                            #print len(metadata)
                            #import sys
                            #sys.exit(-1)
                            self.request.send(metadata)
                        self.byte_count = 0
                    else:
                        if bytes_until_meta < buffer_size:
                            n_bytes = bytes_until_meta
                        else:
                            n_bytes = buffer_size
                        buffer = f.read(n_bytes)

                        self.request.send(buffer)
                        self.byte_count += len(buffer)
                        self.total_bytes += len(buffer)
                        if len(buffer) == 0: break
                    i+=1

                    if self.playlist.data['skip']:
                        log.info(">>")
                        skip = True
                        song = None # don't scrobble
                        break

                    if self.playlist.data['status'] == 'stopped':
                        log.info(".")
                        skip = True
                        song = None # don't scrobble
                        break

                if not skip:
                    # increment the counter if we're not ffwd
                    self.playlist.next()
                else:
                    self.playlist.data['skip'] = False
                self.dirty_meta = True
            except IOError, e:
                #self.data['song'] = None
                if e.errno == errno.EPIPE:
                    self.empty_scrobble_queue()
                    log.exception("Broken pipe")
                elif e.errno == errno.ECONNRESET:
                    self.empty_scrobble_queue()
                    #log.exception("Connection reset by peer")
                    log.info("Client disconnected")
                else:
                    self.empty_scrobble_queue()
                    log.exception(errno.errorcode[e.errno])
                break # while
            finally:
                pipes = [mp3_pipe, flac_pipe]
                for pipe in pipes:
                    if pipe is not None:
                        try:
                            pipe.kill()
                            pipe.wait()
                        except OSError:
                            # can't kill dead proc
                            pass
