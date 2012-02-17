import os, time,socket
from SocketServer import TCPServer
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from lib.config import Config
from lib.streamer import Streamer
from lib.logger import log
from lib.data import DataManager


class Server(HTTPServer):

    def __init__(self, addr):
        self.allow_reuse_address = 1
        TCPServer.__init__(self, addr, ServerRequestHandler)

        # shared state
        self.data = dict()

        # set server defaults
        self.data = {
                'started_at'    : time.time(),
                'port'          : Config.port,
                'hostname'      : Config.hostname
        }

        # create a shared Data object
        manager = DataManager(address=('', 18945), authkey="riddim")

        # "Private" methods are *not* exported out of the manager
        # by default.  This includes stuff to make dict work minimally.  See
        #   http://docs.python.org/library/multiprocessing.html#multiprocessing.managers.BaseManager.register
        DataManager.register('get_data', callable=lambda: self.data,
                exposed=('__str__', '__delitem__', '__getitem__',
                    '__setitem__'))

        manager.start()


        log.info("Server running at http://%s:%s" % \
                self.server_address)
        self.serve_forever()

class ServerRequestHandler(BaseHTTPRequestHandler):

    #def __init__(self, request, client_address, server):

    def do_HEAD(self, icy_client):
        #if icy_client:
        self.send_response(200, "ICY")
        config = Config().config
        # fixme verbose
        headers = {
            'icy-notice1'   : config.get('icy', 'notice1'),
            'icy-notice2'   : config.get('icy', 'notice2'),
            'icy-name'      : config.get('icy', 'name',0, {'hostname': socket.gethostname()}),
            'icy-genre'     : config.get('icy', 'genre'),
            'icy-url'       : config.get('icy', 'url'),
            'icy-pub'       : config.getboolean('icy', 'pub'),
            #'icy-br'        : 128,
            'icy-metaint'   : config.getint('icy', 'metaint'),
            'content-type'  : config.get('icy', 'content_type')
        }
        [self.send_header(k,v) for k,v, in headers.iteritems()]
        self.end_headers()

    def do_POST(self):
        pass

    def do_GET(self):
        # Client candidates:

        """ cmus """
        # GET / HTTP/1.0
        # Host: 0x7be.org
        # User-Agent: cmus/v2.3.2
        # Icy-MetaData: 1

        """ mplayer """
        # GET / HTTP/1.0
        # Host: 0x7be.org:18944
        # User-Agent: MPlayer/SVN-r31347-4.5.0
        # Icy-MetaData: 1
        # Connection: close

        # GET / HTTP/1.0
        # Accept: */*
        # User-Agent: NSPlayer/4.1.0.3856
        # Host: 0x7be.org:18944
        # Pragma: xClientGUID={c77e7400-738a-11d2-9add-0020af0a3278}
        # Pragma: no-cache,rate=1.000000,stream-time=0,stream-offset=0:0,request-context=1,max-duration=0
        # Connection: Close

        """ squeezebox """
        # Connection: close
        # Cache-Control: no-cache
        # Accept: */*
        # Host: localhost:18944
        # User-Agent: iTunes/4.7.1 (Linux; N; Linux; i686-linux; EN; utf8) SqueezeCenter, Squeezebox Server/7.4.1/28947
        # Icy-Metadata: 1

        H = self.headers
        icy_client = False
        try:
            icy_client = (int(H['icy-metadata']) == 1)
        except KeyError, e:
            log.exception("non-icy client:  %s" % e)

        user_agent = None
        try:
            user_agent = H['user-agent']
        except KeyError, e:
            log.exception("Couldn't get user agent.")

        if user_agent:
            log.info("User-Agent:  %s" % user_agent)

        self.do_HEAD( icy_client )

        #Streamer( self.request, self.server.data ).stream( icy_client )
        Streamer( self.request ).stream( icy_client )
