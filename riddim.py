import socket
import struct

import playlist

class Jukebox:

    def __init__(self):
        pass

    def modes(self):
        # repeat
        # continue
        # shuffle
    

class Riddim:

    def __init__(self,port=18944):
        self.hostname = socket.gethostname()

        self.CHUNK_SIZE=8192
        print "riddim running on %s" % self.port

    def header(self):
        return """ICY 200 OK
icy-notice1: <BR>Riddim<BR>
icy-notice2: riddim-server<BR>
icy-name: riddim on %s
icy-genre: unknown
icy-url: http://github.com/noah/riddim
content-type: audio/mpeg
icy-pub: 1
icy-br: 128
icy-metaint: %s

""" % (self.hostname,self.CHUNK_SIZE)

    def on(self):
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sockets.bind(('localhost',self.port))
        self.socket.listen(1)
        self.conn,self.addr = self.sockets.accept()
        print 'connect by', self.addr

    def off(self):
        self.conn.close()

    def stream(self):
        while 1:
            with open('mp3/asdf.mp3') as f:
              while bytes is not None:
                bytes = f.read(self.CHUNK_SIZE)
                self.conn.send(bytes)

playlist = Playlist(['./mp3'])

riddim = Riddim(18945)
riddim.on()
riddim.stream(playlist)
riddim.off()
