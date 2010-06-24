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

    def __getitem__(self,key):
        try:
            return self.read()[key]
        except KeyError:
            return None

    def __setitem__(self,key,value):
        D = self.read()
        D[str(key)] = str(value)
        self.write(D)

    def truncate(self):
        with lock:
            try:
                f = open(self.datafile,'w')
                return True
            except:
                return False

    def read(self):
        with lock:
            try:
                f = open(self.datafile,'r')
            except IOError:
                f = open(self.datafile,'w')
                f.close()
            try:
                data = json.load(f)
            except ValueError:
                data = {}
            f.close()
            return data
    
    def write(self,data):
        with lock:
            return json.dump(data,open(self.datafile,'w'),indent=2)

#if __name__ == '__main__':
    #rd = RiddimData()
    #rd['p'] = 234895723457908236489572346987234565
    #print rd['p']
