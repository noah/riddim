import os
import pickle

import threading
lock = threading.Lock()

from config import Config

class Data(object):

    def __init__(self):
        self.config = Config()

    def __getitem__(self, key):
        try:
            return self.read()[key]
        except KeyError:
            return None

    def __setitem__(self, key, value):
        D = self.read()
        D[key] = value
        self.write(D)

    def truncate(self):
        try:
            f = open(self.config.datapath, 'w')
            return True
        except:
            return False

    def read(self):
        f       = None
        data    = None

        try:
            f = open(self.config.datapath, 'r')
            data = pickle.load(f)
        except IOError:
            f = open(self.config.datapath, 'w')
        except EOFError:
            f = open(self.config.datapath, 'w')
        finally:
            if f is not None: f.close()

        if data is None: data = {}

        return data

    def write(self, data):
        return pickle.dump(data, open(self.config.datapath, 'w'))

if __name__ == '__main__':
    import pprint
    rd = Data()
    pprint.pprint(rd.read())
