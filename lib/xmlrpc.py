class RiddimXMLRPCRegisters(object):

    def __init__(self,server):
        self.server = server
        #self.streamer = server.streamer

    def status(self):
        return {
                'None'  :   'stopped'
        }[self.streamer.status]

    def query(self):
        if self.server.streamer is not None:
            print "here:  %s" % self.server.streamer['status']
            return self.server.streamer
        else:
            return 'Not streaming.'
