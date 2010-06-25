import os
import pickle

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
        D[key] = value
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
            data = None
            try:
                f = open(self.datafile,'r')
                data = pickle.load(f)
                f.close()
            except IOError:
                f = open(self.datafile,'w')
                f.close()
            except EOFError:
                f = open(self.datafile,'w')
                f.close()
            if data is None: data = {}
            return data
    
    def write(self,data):
        with lock:
            return pickle.dump(data,open(self.datafile,'w'))

# if __name__ == '__main__':
#     rd = RiddimData()
#     rd['p'] = 234895723457908236489572346987234565
#     rd['this'] = True
#     print rd['p']
#     if rd['this']:
#         print "yup"
#     print rd.truncate()
#     print rd.read()
