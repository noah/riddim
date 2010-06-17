import os
import glob
import SocketServer # see:  http://docs.python.org/library/socketserver.html
import SimpleXMLRPCServer

#   It's always a good day for smoking crack at winamp, inc.
#
# see amarok for ideas on the (crappy) icecast metadata "protocol"
# http://www.google.com/codesearch/p?hl=en#bor5KmW_n7E/pub/freeware/KDE/SOURCES/IA32AMD32/amarok-1.3.5.S10X86.SS10.tar.bz2%7CBIlNJDe3jFE/amarok-1.3.5/amarok/src/scripts/shouter/Services.py&q=ICYRESP&exact_package=ftp://ftp.sunfreeware.com/pub/freeware/KDE/SOURCES/IA32AMD32/amarok-1.3.5.S10X86.SS10.tar.bz2&l=118
#
# see this for an explantion of the whole cockamamie thing:
#   http://www.smackfu.com/stuff/programming/shoutcast.html

# TODO
#   make this not suck
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
icy-pub: 0
icy-br: 128
icy-metaint: 16384

""" % ("localhost")

def mp3tags(path):
    tag = eyeD3.Tag()
    tag.link(path)
    return tag.getArtist(),tag.getTitle()

def get_mp3_start(path):
    # lifted from amarok
    f = open(path, 'r')
    id3 = f.read(3)
    if not id3=="ID3": return 0
    f.seek(6)
    l = f.read(4)
    start = eyeD3.binfuncs.bin2dec(eyeD3.binfuncs.bytes2bin(l, 7)) + 10
    f.close()
    return start

class RiddimServerRequestHandler(SocketServer.BaseRequestHandler):

    def __init__(self,request,client_address,server):
        self.server = server
        SocketServer.BaseRequestHandler.__init__(self, request, client_address,
                server)

    def get_meta(self,path):
        # lifted from amarok
        META = "%cStreamTitle='%s';StreamUrl='%s';%s"
        PADDING = '\x00' * 16
        if self.dirty_meta:
            stream_title = "%s - %s" % mp3tags(path)
            stream_url = "http://downbe.at/"

            # The literal 28 is the number of static characters in the META string (see top)
            length = len(stream_title) + len(stream_url) + 28
            padding = 16 - length % 16
            meta = META % ( (length + padding)/16, stream_title, stream_url, PADDING[:padding] )
            self.dirty_meta = False
            return meta
        else:
            return '\x00'
    
    def handle(self):
        bufsize = 4096
        print 'handling request'
        # self.request is the socket connect, SocketServer gives us this instance
        self.request.sendall(icy_header())
        # mp3, MP3, mP3, Mp3 <-- why do people insist on mixed-case filenames?
        playlist = glob.glob(os.path.join(self.server.media_dir,'*.[mM][pP]3'))  

        # icy streaming
        META_INTERVAL = 16384

        for FILE in playlist:
            print 'streaming %s ' % FILE
            f = file(FILE,'r')
            fsize = os.stat(FILE)[6]
            mp3start = get_mp3_start(FILE)
            #f.seek(fsize * pos + mp3start)
            f.seek(mp3start)

            byte_count = 0
            self.dirty_meta = True
            # lifted from amarok
            while f.tell() < fsize and True:
                bytes_until_meta = META_INTERVAL - byte_count
                #print 'bytes until meta %s' % bytes_until_meta
                if bytes_until_meta == 0:
                    meta = self.get_meta(FILE)
                    self.request.send(meta)
                    byte_count = 0
                else:
                    if bytes_until_meta < bufsize:
                        buf = f.read(bytes_until_meta)
                        self.request.send(buf)
                        byte_count += len(buf)
                    else:
                        buf = f.read(bufsize)
                        self.request.send(buf)
                        byte_count += len(buf)
            self.dirty_meta = True
        return

class RiddimServer(SocketServer.ThreadingMixIn, SimpleXMLRPCServer.SimpleXMLRPCServer):
    def __init__(self,addr,media_dir):
        self.media_dir = media_dir
        print "initializing TCPServer"
        SocketServer.TCPServer.__init__(self,addr,RiddimServerRequestHandler)
