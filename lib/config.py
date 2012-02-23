import os
import socket
import ConfigParser


def join_path( *args ):
    return os.path.join( *args )


class Config(object):

        basepath    = os.path.dirname( os.path.dirname( __file__ ) )
        config = ConfigParser.ConfigParser()

        config.read( os.path.join(basepath, 'riddim.cfg') )

        # set up some config stuff that we will need
        runpath         = join_path('/tmp')
        pidpath         = join_path(runpath, config.get('riddim', 'pidfile'))
        datapath        = join_path(basepath, 'data', config.get('riddim', 'datafile'))
        hostname        = "0.0.0.0"
        port            = config.get('riddim', 'port')
        scrobble        = config.getboolean('riddim', 'scrobble')
        url             = config.get('riddim', 'url')
        metaint         = config.getint('icy', 'metaint')
        notice_1        = config.get('icy', 'notice1')
        notice_2        = config.get('icy', 'notice2')
        icy_name        = config.get('icy', 'name', 0, {'hostname': socket.gethostname()})
        icy_genre       = config.get('icy', 'genre')
        icy_url         = config.get('icy', 'url')
        icy_pub         = config.getboolean('icy', 'pub')
        icy_metaint     = config.getint('icy', 'metaint')
        content_type = config.get('icy', 'content_type')
