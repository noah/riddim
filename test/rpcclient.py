import xmlrpclib

s = xmlrpclib.ServerProxy('http://localhost:18944',allow_none=True)
# Print list of available methods
print s.query()
