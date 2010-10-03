import os
import ConfigParser

# this file should be ro

class RiddimConfig(object):
    def __init__(self):
        self.cwd = os.path.realpath(os.path.dirname(__file__) + '/..')
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.join(self.cwd,'riddim.cfg'))
