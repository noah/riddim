import os, sys, ConfigParser

def join_path( *args ):
    return os.path.join( *args )

class Config(object):

        basepath    = os.path.dirname( os.path.dirname( __file__ ) )
        config = ConfigParser.ConfigParser()

        config.read( os.path.join(basepath, 'riddim.cfg') )

        # set up some config stuff that we will need
        port        = config.get('riddim', 'port')
        hostname    = "0.0.0.0"
        runpath          = join_path('/tmp')
        pidpath     = join_path(runpath, config.get('riddim', 'pidfile'))
        datapath    = join_path(basepath, 'data', config.get('riddim','datafile'))
        scrobble    = config.getboolean('riddim', 'scrobble')
        url         = config.get('riddim', 'url')
        metaint     = config.getint('icy', 'metaint')
