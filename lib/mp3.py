import os

try:
    import eyeD3
except:
    print """
    You need eyeD3 for id3 tag support:
        # pacman -S extra/python-eyed3 
        on archlinux
    """
    import sys
    sys.exit(0)

class RiddimMP3(object):

    def __init__(self,path):
        self.path = path

    def __str__(self):
        return ' - '.join(self.tags())

    def bitrate(self):
        return eyeD3.Mp3AudioFile(self.path).getBitRate()[1]

    def title(self):
        return ' - '.join(self.tags())

    def tags(self):
        artist = title = ""
        try:
            tag = eyeD3.Tag()
            tag.link(self.path)
            artist = tag.getArtist()
            title = tag.getTitle()
        except eyeD3.TagException:
            print "Couldn't parse tags for %s" % self.path

        return artist,title

    def size(self):
        return os.stat(self.path)[6]

    def start(self):
        # lifted from amarok
        f = open(self.path, 'r')
        id3 = f.read(3)
        if not id3 == "ID3":
            return 0
        f.seek(6)
        l = f.read(4)
        start = eyeD3.binfuncs.bin2dec(eyeD3.binfuncs.bytes2bin(l,7)) + 10
        f.close()
        return start
