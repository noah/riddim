import os
import time
import errno
import socket

from lib.mp3 import RiddimMP3
from lib.data import RiddimData
from lib.config import RiddimConfig
from lib.playlist import RiddimPlaylist

class RiddimStreamer(object):
    def __init__(self,request):
        self.data = RiddimData()
        self.playlist = RiddimPlaylist()
        self.config = RiddimConfig(os.getcwd()).config
        self.request = request
        self.byte_count = 0
        self.total_bytes = 0


    # ~ It's always a good day for smoking crack at Nullsoft!
    # ~ See the Amarok source for ideas on the (crappy) icecast metadata "protocol"
    # ~ This explains the whole cockamamie thing:
    #   http://www.smackfu.com/stuff/programming/shoutcast.html

    def get_meta(self):
        # lifted from amarok
        metadata = "%cStreamTitle='%s';StreamUrl='%s';%s"
        padding = '\x00' * 16
        if self.dirty_meta:
            stream_title = str(self.mp3)
            stream_url = self.config.get('riddim','url')

            # 28 is the number of static characters in metadata (!)
            length = len(stream_title) + len(stream_url) + 28
            pad = 16 - length % 16
            meta = metadata % (((length+pad)/16),stream_title,stream_url,padding[:pad])
            self.dirty_meta = False
            return meta
        else:
            return '\x00'

    def stream(self,icy_client=False):
        while True:
            song = self.playlist.get_song()
            if not song: return
            self.mp3 = RiddimMP3(song)
            print 'streaming %s' % self.mp3

            try:
                # this loop gets its ideas about the shoutcast protocol from amarok
                buffer              = 0
                buffer_size         = 4096
                metadata_interval   = self.config.getint('icy','metaint')
                f = file(song, 'r')
                f.seek(self.mp3.start())
                self.dirty_meta = True
                mp3_size = self.mp3.size()
                while f.tell() < mp3_size:
                    # check for state change every 0.25MB (local I/O)
                    bytes_until_meta = (metadata_interval - self.byte_count)
                    if bytes_until_meta == 0:
                        if icy_client:
                            self.request.send(self.get_meta())
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

                    if self.byte_count > 0 and ((self.total_bytes % 262144) == 0):
                        print "self.byte_count:  %s" % self.total_bytes
                        # if we need to skip, reset the flag
                        if self.data['next'] or self.data['previous']:
                            self.data['next'] = self.data['previous'] = False
                            # and get a new song
                            next_prev = True
                            break
                if not next_prev:
                    # increment the counter if we're not ffwd or rewinding
                    self.data['index'] += 1
                self.dirty_meta = True
            except IOError, e:
                self.data['status'] = 'stopped'
                self.data['song'] = None
                if e.errno == errno.EPIPE:
                    print "Broken pipe"
                elif e.errno == errno.ECONNRESET:
                    print "Connection reset by peer"
                else:
                    print errno.errorcode[e.errno]
                break # while
