import glob
import SocketServer # see:  http://docs.python.org/library/socketserver.html
import SimpleXMLRPCServer

try:
    import eyeD3
except:
    print """
    You need eyeD3 for id3 tag support:
        # pacman -S extra/python-eyed3 
        on archlinux
    """
    import sys
    sys.exit(0)

def icy_header():
    return """ICY 200 OK
icy-notice1: <BR>Riddim<BR>
icy-notice2: riddim-server<BR>
icy-name: riddim on %s
icy-genre: unknown
icy-url: http://github.com/noah/riddim
content-type: audio/mpeg
icy-pub: 1
icy-br: 128

""" % ("localhost")

def mp3tags(path):
    tag = eyeD3.Tag()
    tag.link(path)
    return tag.getArtist(),tag.getAlbum(),tag.getTitle()

class RiddimServerRequestHandler(SocketServer.BaseRequestHandler):
    
    def handle(self):

        print 'handling request'
        # self.request is the socket connect, SocketServer gives us this instance
        self.request.sendall(icy_header())
        playlist = glob.glob('./mp3/*.mp3')
        for mp3 in playlist:
            print "%s - %s - %s" % mp3tags(mp3)
            # Echo the back to the client
            with open(mp3) as FILE:
                for bytes in FILE:
                    self.request.send(bytes)
        return

class RiddimServer(SocketServer.ThreadingMixIn, SimpleXMLRPCServer.SimpleXMLRPCServer):
    def __init__(self,addr):
        print "initializing TCPServer"
        SocketServer.TCPServer.__init__(self,addr,RiddimServerRequestHandler)
