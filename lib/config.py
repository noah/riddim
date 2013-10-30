import os
import socket
import ConfigParser


def join_path(*args):
    return os.path.join(*args)



class Config(object):

        running         = True
        basepath        = os.path.dirname(os.path.dirname(__file__))
        config          = ConfigParser.ConfigParser()
        config.read( join_path(basepath, 'riddim.cfg') )

        authkey         = open(join_path(basepath, "secret"),'r').read()
        # set up some config stuff that we will need
        runpath         = join_path('/tmp')
        datapath        = join_path(basepath, 'data', config.get('riddim', 'datafile'))
        hostname        = socket.gethostname()
        scrobble        = config.getboolean('riddim', 'scrobble')
        url             = config.get('riddim', 'url')
        lame_args       = config.get('riddim', 'lame_args')
        pool_size       = config.getint('riddim', 'pool_size')
        #
        metaint         = config.getint('icy', 'metaint')
        buffer_size     = config.getint('icy', 'buffer_size')
        notice_1        = config.get('icy', 'notice1')
        notice_2        = config.get('icy', 'notice2')
        icy_name        = config.get('icy', 'name', 0, {'hostname': socket.gethostname()})
        icy_genre       = config.get('icy', 'genre')
        icy_url         = config.get('icy', 'url')
        icy_pub         = config.getboolean('icy', 'pub')
        icy_metaint     = config.getint('icy', 'metaint')
        content_type    = config.get('icy', 'content_type')



        @classmethod
        def pidpath(cfg, port):
            return join_path(cfg.runpath, "%s.%s" % (cfg.config.get('riddim', 'pidfile'), port))
