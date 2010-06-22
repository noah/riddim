import os
import json

import threading
lock = threading.Lock()

#from lib.config import RiddimConfig
from config import RiddimConfig

class RiddimData(object):

    def __init__(self):
        config = RiddimConfig(os.getcwd()).config
        self.datafile = os.path.join(os.getcwd(),'data',
                config.get('riddim','datafile'))

    def read(self):
        with lock:
            return json.load(open(self.datafile,'r'))
    
    def write(self,data):
        with lock:
            return json.dump(data,open(self.datafile,'w'))

    # TODO use properties
    def set(self,key):
        json = self.read()

if __name__ == '__main__':
    data = RiddimData()
    print data.read()
