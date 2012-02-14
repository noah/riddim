import os, time
import pickle

import threading
lock = threading.Lock()

from lib.config import Config

# TODO singleton
class Data(object):

    def __init__(self):
        self.config = Config()

        self.data = {}
        try:
            # read the file
            with open( self.config.datapath, 'r' ) as picklef:
                self.data = pickle.load(picklef)
        except IOError:
            # file doesn't exist
            open(self.config.datapath, 'w').close()


        self.data['started_on'] = time.time()
        self.data['port']       = self.config.port
        self.data['hostname']   = self.config.hostname
        self.data['song']       = ''
        self.data['status']     = 'stopped'
        self.data['index']      = 0
        if self.data['playlist'] is None: self.data['playlist'] = {}

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
