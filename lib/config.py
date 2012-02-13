import os, sys, ConfigParser

def join_path(*args):
    return os.path.join( *args )

class Config(object):


    def __init__(self):

        basepath    = os.path.dirname(os.path.dirname( __file__ ))
        self.config = ConfigParser.ConfigParser()

        self.config.read(os.path.join(basepath, 'riddim.cfg'))

        # set up some config stuff that we will need
        self.port       = self.config.get('riddim', 'port')
        runpath         = join_path(basepath, 'var', 'run')
        self.pidpath    = join_path(runpath, self.config.get('riddim', 'pidfile'))
        self.datapath   = join_path(basepath, 'data', self.config.get('riddim','datafile'))
