import time
import errno
import socket

from lib.mp3 import RiddimMP3

class RiddimStreamer:

    def __init__(self,request):
        self.request = request
        self.byte_count = 0

    #  It's always a good day for smoking crack at Nullsoft!
    #
    # See amarok for ideas on the (crappy) icecast metadata "protocol"
    # http://www.google.com/codesearch/p?hl=en#bor5KmW_n7E/pub/freeware/KDE/SOURCES/IA32AMD32/amarok-1.3.5.S10X86.SS10.tar.bz2%7CBIlNJDe3jFE/amarok-1.3.5/amarok/src/scripts/shouter/Services.py&q=ICYRESP&exact_package=ftp://ftp.sunfreeware.com/pub/freeware/KDE/SOURCES/IA32AMD32/amarok-1.3.5.S10X86.SS10.tar.bz2&l=118
    #
    # see this for an explantion of the whole cockamamie thing:
    #   http://www.smackfu.com/stuff/programming/shoutcast.html

    def get_meta(self):
        # lifted from amarok
        metadata = "%cStreamTitle='%s';StreamUrl='%s';%s"
        padding = '\x00' * 16
        if self.dirty_meta:
            stream_title = str(self.mp3)
            # TODO lib/config.py
            stream_url = "http://downbe.at/"

            # 28 is the number of static characters in metadata (!)
            length = len(stream_title) + len(stream_url) + 28
            pad = 16 - length % 16
            meta = metadata % (((length+pad)/16),stream_title,stream_url,padding[:pad])
            self.dirty_meta = False
            return meta
        else:
            return '\x00'

    def stream(self,playlist,icy_client=False):
        for path in playlist:
            self.mp3 = RiddimMP3(path)
            print 'streaming %s' % self.mp3

            try:
                # loop lifted from amarok
                buffer              = 0
                buffer_size         = 4096
                metadata_interval   = 16384

                f = file(path, 'r')
                f.seek(self.mp3.start())
                self.dirty_meta = True
                mp3_size = self.mp3.size()
                while f.tell() < mp3_size:
                    bytes_until_meta = (metadata_interval - self.byte_count)
                    if bytes_until_meta == 0:
                        if icy_client:
                            meta = self.get_meta()
                            self.request.send(meta)
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
            #except socket.error, e:
            #    print "Uh oh, socket error"
            #    print e
            except IOError, e:
                if e.errno == errno.EPIPE:
                    print "Broken pipe"
                elif e.errno == errno.ECONNRESET:
                    print "Connection reset by peer"
                else:
                    print errno.errorcode[e.errno]
    #return
