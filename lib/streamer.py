import os
import time
import errno
import socket
import subprocess

from lib.data import RiddimData
from lib.config import RiddimConfig
from lib.playlist import RiddimPlaylist

class RiddimStreamer(object):
    def __init__(self,request):
        self.data = RiddimData()
        self.playlist = RiddimPlaylist()
        self.config = RiddimConfig().config
        self.request = request
        self.byte_count = 0
        self.total_bytes = 0


    # ~ It's always a good day for smoking crack at Nullsoft!
    # ~ See the Amarok source for ideas on the (crappy) icecast metadata "protocol"
    # ~ This explains the whole cockamamie thing:
    #   http://www.smackfu.com/stuff/programming/shoutcast.html

    def get_meta(self,song):
        # lifted from amarok
        metadata = "%cStreamTitle='%s';StreamUrl='%s';%s"
        padding = '\x00' * 16
        if self.dirty_meta:
            stream_title = str(song['audio']['title'])
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
            print '> %s' % str(song['audio']['title'])

            try:
                flac = False
                # this loop gets its ideas about the shoutcast protocol from amarok
                buffer              = 0
                buffer_size         = 4096
                metadata_interval   = self.config.getint('icy','metaint')

                print song
                if song['audio']['mimetype'] == 'audio/x-flac':
                    flac_pipe = subprocess.Popen(
                            "/usr/bin/flac -d \"%s\" --stdout" % song['path'], 
                            stdout=subprocess.PIPE,
                            shell=True)
                    mp3_pipe = subprocess.Popen(
                            "/usr/bin/lame -V0 - -",
                            stdout=subprocess.PIPE,
                            shell=True,
                            stdin = flac_pipe.stdout)
                    f = mp3_pipe.stdout
                    flac = True
                else: # assume mp3
                    f = file(song['path'], 'r')
                    f.seek(song['audio']['start'])

                self.dirty_meta = True

                audio_size = song['audio']['size']
                index_change = False
                while flac or (f.tell() < audio_size):
                    bytes_until_meta = (metadata_interval - self.byte_count)
                    if bytes_until_meta == 0:
                        if icy_client:
                            metadata = self.get_meta(song)
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

                    # check for state change every 0.5MB (local I/O!)
                    # this sucks FIXME
                    if self.byte_count > 0 and ((self.total_bytes % 524288) == 0):
                        #print "self.byte_count:  %s" % self.total_bytes
                        if self.data['status'] == 'stopped':
                            self.data['song'] == ''
                            print "RiDDiM stopped."
                            return
                        # if we need to skip, reset the flag(s)
                        if self.data['index_changed']:
                            self.data['index_changed'] = False
                            # and get a new song
                            index_change = True
                            break
                if not index_change :
                    # increment the counter if we're not ffwd or rewinding
                    self.data['index'] += 1
                self.dirty_meta = True
            except IOError, e:
                self.data['song'] = None
                if e.errno == errno.EPIPE:
                    print "Broken pipe"
                elif e.errno == errno.ECONNRESET:
                    print "Connection reset by peer"
                else:
                    print errno.errorcode[e.errno]
                break # while
