import xmlrpclib

s = xmlrpclib.ServerProxy('http://localhost:18944')
# Print list of available methods
print s.system.listMethods()
