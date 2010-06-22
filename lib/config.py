import os
import ConfigParser

class RiddimConfig(object):
    def __init__(self,cwd):
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.join(cwd,'riddim.cfg'))
