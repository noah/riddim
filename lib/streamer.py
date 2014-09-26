# -*- coding: utf-8 -*-
import time
import errno
import subprocess
import Queue

from lib.config     import Config
from lib.scrobble   import Scrobbler, ScrobbleItem, NOW_PLAYING, PLAYED
from lib.logger     import log
from lib.playlist   import Playlist


class Streamer(object):

    def __init__(self, request, port):

        self.playlist       = Playlist(port)
        self.request        = request
        self.byte_count     = 0

        if Config.scrobble:

            self.scrobble_queue = Queue.Queue()
            self.scrobbler      = Scrobbler( self.scrobble_queue )
            self.scrobbler.daemon = True
            self.scrobbler.start()

    # It's always a good day for smoking crack at Nullsoft!
    #   See the Amarok source for ideas on the (crappy) icecast metadata "protocol"
    #           This explains the whole cockamamie thing:
    #           http://www.smackfu.com/stuff/programming/shoutcast.html

    def get_meta(self, song):
        # lifted from amarok
        metadata    = u"%cStreamTitle='%s';StreamUrl='%s';%s"
        padding     = u'\x00' * 16
        meta        = None
        if self.dirty_meta:
            songs           = unicode(song)
            stream_title    = songs.encode(u'ascii', u'ignore')
            stream_url      = Config.url

            # 28 is the number of static characters in metadata (!)
            length          = len(stream_title) + len(stream_url) + 28
            pad             = 16 - length % 16
            what            = padding[:pad]
            meta            = metadata % (((length + pad) / 16), stream_title, stream_url, what)
            self.dirty_meta = False
        else:
            meta = u'\x00'

        return meta

    def empty_scrobble_queue(self):
        if Config.scrobble:
            with self.scrobble_queue.mutex:
                self.scrobble_queue.queue.clear()

    def stream(self, icy_client=False):
        song = None
        while self.playlist.data[u'running']:
            if Config.scrobble and song:
                    # just played one . . . scrobble it
                    self.scrobble_queue.put(ScrobbleItem(PLAYED, song))
                    #log.debug("enqueued played")
                    #log.debug(song)

            # new song
            song            = self.playlist.get_song()
            song_start_time = time.time()
            self.playlist.data[u"progress"] = 0

            if not song:
                log.warn(u"no playlist, won't stream")
                self.playlist.data[u'status'] = u'stopped'
                self.byte_count = 0
                self.empty_scrobble_queue()
                return

            if Config.scrobble:
                #log.debug("enqueued now playing")
                self.scrobble_queue.put(ScrobbleItem(NOW_PLAYING, song))

            log.info(u'> %s' % unicode(song))

            transcode = None
            try:
                # this loop gets some of its ideas about the shoutcast protocol from Amarok
                buffer              = 0
                buffer_size         = Config.buffer_size
                metadata_interval   = Config.metaint

                try:
                    transcode.stdout.close()
                except:
                    pass

                #cif song.mimetype[0:5] in ["audio", "video"]:
                transcode = subprocess.Popen([u"/usr/bin/ffmpeg",
                                              u"-i", song.path,
                                              u"-vn",
                                              u"-loglevel", u"warning",
                                              u"-qscale:a", u"0",
                                              u"-f", u"mp3",
                                              u"-"],
                                             stdout=subprocess.PIPE,
                                             shell=False)
                self.dirty_meta = True

                skip = False
                while self.playlist.data[u'running'] and transcode:
                    bytes_until_meta = (metadata_interval - self.byte_count)
                    if bytes_until_meta == 0:
                        if icy_client:
                            metadata = self.get_meta(song)
                            self.request.send(metadata.encode(u'ascii', u'ignore'))
                        self.byte_count = 0
                    else:
                        if bytes_until_meta < buffer_size:
                            chunk_bytes = bytes_until_meta
                        else:
                            chunk_bytes = buffer_size
                        buffer = transcode.stdout.read(chunk_bytes)

                        self.request.send(buffer)
                        buflen = len(buffer)
                        self.byte_count                     += buflen
                        self.playlist.data[u"sum_bytes"]     += buflen
                        elapsed = time.time() - song_start_time
                        self.playlist.data[u'elapsed'] = elapsed
                        # set percentage elapsed
                        self.playlist.data[u"progress"] = float(elapsed * 100) / song.length

                        if len(buffer) == 0: break

                    if self.playlist.data[u'skip']:
                        log.info(u">>")
                        skip = True
                        song = None  # don't scrobble
                        self.playlist.data[u"elapsed"] = 0
                        self.playlist.data[u"progress"] = 0
                        break

                    if self.playlist.data[u'status'] == u'stopped':
                        log.info(u".")
                        skip = True
                        song = None  # don't scrobble
                        self.playlist.data[u"elapsed"] = 0
                        break

                if not skip:
                    # increment the counter if we're not ffwding
                    self.playlist.next()
                else:
                    self.playlist.data[u'skip'] = False
                self.dirty_meta = True
            except IOError, e:
                if e.errno == errno.EPIPE:
                    self.empty_scrobble_queue()
                    log.info(u"Broken pipe.  Client disconnected.")
                elif e.errno == errno.ECONNRESET:
                    self.empty_scrobble_queue()
                    log.info(u"Client disconnected")
                else:
                    self.empty_scrobble_queue()
                    log.exception(errno.errorcode[e.errno])
                self.playlist.data[u'status'] = 'stopped'
                break  # while
            except KeyboardInterrupt:
                self.playlist.data[u'running']   = False
            finally:
                if transcode is not None:
                    try:
                        transcode.kill()
                        transcode.wait()
                    except OSError:
                        # can't kill dead proc
                        pass
