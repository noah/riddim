import sys
import time
from config import Config

from multiprocessing import managers, connection

def _new_init_timeout():
        return time.time() + 0.2

sys.modules['multiprocessing'].__dict__['managers'].__dict__['connection']._init_timeout = _new_init_timeout

from multiprocessing.managers import BaseManager

class DataManager(BaseManager): pass


def set_data(port, k, v):
        # create a shared Data object
        DataManager.register('get_data')
        manager = DataManager(address=(Config.hostname, port + 1),
                authkey=Config.authkey)
        manager.connect()
        data = manager.get_data()
        data[k] = v
