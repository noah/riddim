import glob
import logging
import SocketServer # see:  http://docs.python.org/library/socketserver.html

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
        filename='/dev/stdout',
        level=logging.DEBUG)

try:
    import eyeD3
except:
    logging.error("""
    You need eyeD3 for id3 tag support:
        # pacman -S extra/eyed3 
        on archlinux
    """)
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

        logging.info('handling request')
        # self.request is the socket connect, SocketServer gives us this instance
        self.request.sendall(icy_header())
        playlist = glob.glob('./mp3/*.mp3')
        for mp3 in playlist:
            logging.info("%s - %s - %s" % mp3tags(mp3))
            # Echo the back to the client
            with open(mp3) as FILE:
                for bytes in FILE:
                    self.request.send(bytes)
        return

class RiddimServer():
    def __init__(self,address):
        self.server = SocketServer.TCPServer(address,RiddimServerRequestHandler)
