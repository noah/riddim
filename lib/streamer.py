import os
import time
import errno
import socket

from lib.mp3 import RiddimMP3
from lib.data import RiddimData
from lib.config import RiddimConfig

class RiddimStreamer(object):
    def __init__(self,request):
        self.data = RiddimData()
        self.config = RiddimConfig(os.getcwd()).config
        self.request = request
        self.byte_count = 0

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

    def get_song(self):
        playlist = sorted(eval(self.data['playlist']).keys())
        from pprint import pprint 
        pprint(playlist)
        if playlist is None:
            print "Playlist empty"
            return
        I = int(self.data['index'])
        if I is None: I = 0

        try:
            path = playlist[I]
        except IndexError:
            print "No song at index %s" % I
            return

        self.data['status'] = 'playing'
        self.data['song'] = self.mp3
        self.data['index'] = str(I)
        idx = int(self.data['index'])
        self.data['index'] = idx + 1
        self.data['status'] = 'stopped'
        self.data['song'] = ''

    def stream(self,path,icy_client=False):
        self.mp3 = RiddimMP3(path)
        print 'streaming %s' % self.mp3

        try:
            # this loop gets its ideas about the shoutcast protocol from amarok
            buffer              = 0
            buffer_size         = 4096
            metadata_interval   = self.config.getint('icy','metaint')

            f = file(path, 'r')
            f.seek(self.mp3.start())
            self.dirty_meta = True
            mp3_size = self.mp3.size()
            while f.tell() < mp3_size:
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
            self.dirty_meta = True
        except IOError, e:
            if e.errno == errno.EPIPE:
                print "Broken pipe"
            elif e.errno == errno.ECONNRESET:
                print "Connection reset by peer"
            else:
                print errno.errorcode[e.errno]
