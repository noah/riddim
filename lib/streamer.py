import os
import glob
import time
import errno
import socket

from lib.mp3 import RiddimMP3

class RiddimStreamer:

    def __init__(self,request):
        self.request = request

    #  It's always a good day for smoking crack at winamp, inc.
    #
    # See amarok for ideas on the (crappy) icecast metadata "protocol"
    # http://www.google.com/codesearch/p?hl=en#bor5KmW_n7E/pub/freeware/KDE/SOURCES/IA32AMD32/amarok-1.3.5.S10X86.SS10.tar.bz2%7CBIlNJDe3jFE/amarok-1.3.5/amarok/src/scripts/shouter/Services.py&q=ICYRESP&exact_package=ftp://ftp.sunfreeware.com/pub/freeware/KDE/SOURCES/IA32AMD32/amarok-1.3.5.S10X86.SS10.tar.bz2&l=118
    #
    # see this for an explantion of the whole cockamamie thing:
    #   http://www.smackfu.com/stuff/programming/shoutcast.html

    def get_meta(self):
        # lifted from amarok
        META = "%cStreamTitle='%s';StreamUrl='%s';%s"
        PADDING = '\x00' * 16
        if self.dirty_meta:
            stream_title = str(self.mp3)
            # TODO lib/config.py
            stream_url = "http://downbe.at/"

            # 28 is the number of static characters in META (!)
            length = len(stream_title) + len(stream_url) + 28
            padding = 16 - length % 16
            meta = META % ((length + padding)/16, stream_title, stream_url, PADDING[:padding])
            self.dirty_meta = False
            return meta
        else:
            return '\x00'

    def stream(self):
        # mp3, MP3, mP3, Mp3 <-- why do people insist on 
        # mixed-case filenames?
        # FIXME
        playlist = glob.glob(
                os.path.join('/home/noah/gits/github/riddim/mp3',
                    '*.[mM][pP]3'))  
        buffer_size = 4096
        META_INTERVAL = 16384

        for path in playlist:
            self.mp3 = RiddimMP3(path)
            print 'streaming %s ' % self.mp3

            # main loop, lifted from amarok
            f = open(path, 'r')
            f.seek(self.mp3.start())
            try:
                byte_count = 0
                self.dirty_meta = True
                while f.tell() < self.mp3.size() and True:
                    bytes_until_meta = META_INTERVAL - byte_count
                    if bytes_until_meta == 0:
                        self.request.send(self.get_meta())
                        byte_count = 0
                    else:
                        if bytes_until_meta < buffer_size:
                            n_bytes = bytes_until_meta
                        else:
                            n_bytes = buffer_size

                        buffer = f.read(n_bytes)
                        self.request.send(buffer)
                        byte_count += len(buffer)

                self.dirty_meta = True
            #except socket.error, e:
            #    print "Uh oh, socket error"
            #    print e
            except IOError, e:
                if e.errno == errno.EPIPE:
                    print "client disconnected"
                    print e
                print e
            f.close()
        return
