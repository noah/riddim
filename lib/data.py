from multiprocessing.managers import BaseManager

class DataManager(BaseManager): pass

#import pprint

#from lib.logger import log
#from lib.config import Config

# try:
#     import cPickle as pickle
# except ImportError:
#     import pickle
# 
# class Data(object):
# 
#     def __init__(self):
# 
#         try:
#             # Read an existing file
#             with open( Config.datapath, 'rb' ) as picklef:
#                 self.__data = pickle.load(picklef)
#         except:
#             # File non-existent or corrupt.
#             self.truncate()
# 
#         print "data initialized "
# 
#     def __getitem__(self, key):
#         try:
#             return self.__data[key]
#         except KeyError:
#             return None
# 
#     def __setitem__(self, key, value):
#         print 'hellowz'
#         self.__data[key] = value
# 
#     def __delitem__(self, key):
#         del self.__data[key]
# 
#     def toggle(self, key):
#         self.__data[key] = not(bool(self.__data(key)))
# 
#     def __str__(self):
#         return pprint.pformat(self.__data)
# 
#     def truncate(self):
#         try:
#             f = open(Config.datapath, 'wb')
#             return True
#         except Exception, e:
#             log.exception(e)
#         return False
# 
#     def save(self):
#         try:
#             pickle.dump(self.__data, open(Config.datapath, 'wb'))
#             return True
#         except Exception, e:
#             log.exception(e)
#         return False
# 
#from multiprocessing.managers import BaseManager

#class DataManager(BaseManager): pass

#self.__data = dict()

#DataManager.register('ServerData', Data,
#        exposed=('__str__', '__delitem__', '__getitem__', '__setitem__', 'toggle', 'truncate', 'save'))
#
# if __name__ == '__main__':
#     import sys
#     dm = DataManager()
#     dm.start()
#     data = dm.ServerData()
#     print data._exposed_
#     data['greeting'] = 'hello, world!'
#     del data['greetz']
#     print data['greeting']
#     print data
