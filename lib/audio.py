import os

try:
    # easyid3 maps the real id3 standard tag names to the same as the flac ones
    from mutagen.mp3 import MP3
    from mutagen.flac import FLAC
    from mutagen.easyid3 import EasyID3 
except:
    print """
    You need mutagen
        # pacman -S mutagen
        on archlinux
    """
    import sys
    sys.exit(0)


class AudioUtil(object):
    ################################################################################
    #
    #  Copyright (C) 2010  Noah K. Tilton <noah@downbe.at>
    #  Copyright (C) 2002-2005  Travis Shirk <travis@pobox.com>
    #  Copyright (C) 2001  Ryan Finne <ryan@finnie.org>
    #
    #  This program is free software; you can redistribute it and/or modify
    #  it under the terms of the GNU General Public License as published by
    #  the Free Software Foundation; either version 2 of the License, or
    #  (at your option) any later version.
    #
    #  This program is distributed in the hope that it will be useful,
    #  but WITHOUT ANY WARRANTY; without even the implied warranty of
    #  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    #  GNU General Public License for more details.
    #
    #  You should have received a copy of the GNU General Public License
    #  along with this program; if not, write to the Free Software
    #  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
    #
    ################################################################################
    # Convert and array of "bits" (MSB first) to it's decimal value.
    def bin2dec(self,x):
       bits = [];
       bits.extend(x);
       bits.reverse();

       multi = 1;
       value = long(0);
       for b in bits:
          value += b * multi;
          multi *= 2;
       return value;

    # Accepts a string of bytes (chars) and returns an array of bits
    # representing the bytes in big endian byte (Most significant byte/bit first)
    # order.  Each byte can have it's higher bits ignored by passing an sz arg.
    def bytes2bin(self,bytes, sz = 8):
       if sz < 1 or sz > 8:
          raise ValueError("Invalid sz value: " + str(sz));

       retVal = [];
       for b in bytes:
          bits = [];
          b = ord(b);
          while b > 0:
             bits.append(b & 1);
             b >>= 1;

          if len(bits) < sz:
             bits.extend([0] * (sz - len(bits)));
          elif len(bits) > sz:
             bits = bits[:sz];

          # Big endian byte order.
          bits.reverse();
          retVal.extend(bits);

       if len(retVal) == 0:
          retVal = [0];
       return retVal;

class RiddimAudio(AudioUtil):

    def __init__(self,path,mimetype):
        self.path = path
        self.mimetype = mimetype

        if mimetype == 'audio/mpeg':
            self.audio = MP3(path,ID3=EasyID3)
        elif mimetype == 'audio/x-flac':
            self.audio = FLAC(path)
        else:
            print "Mimetype %s unsupported" % mimetype
            return

    def __getitem__(self,key):
        try:
            return self.data()[key]
        except KeyError:
            return None

    def __str__(self):
        tags = self.tags()
        return ' - '.join([tags[0],tags[2]])

    def bitrate(self):
        return self.audio.info.bitrate

    def title(self):
        return ' - '.join(self.tags())

    def tags(self):
        return [str(self.audio['artist'][0]),
                str(self.audio['album'][0]),
                str(self.audio['title'][0])]

    def size(self):
        return os.stat(self.path)[6]

    def start(self):
        # lifted from amarok
        f = open(self.path, 'r')
        id3 = f.read(3)
        if not id3 == "ID3": return 0
        f.seek(6)
        l = f.read(4)
        start = self.bin2dec(self.bytes2bin(l,7)) + 10
        f.close()
        return start

    def data(self):
        return {
                'size': self.size(),
                'tags': self.tags(),
                'title': self.title(),
                'bitrate': self.bitrate(),
                'start': self.start(),
                'mimetype': self.mimetype,
        }

if  __name__ == '__main__':
    song = RiddimAudio('./audio/01. Intro.MP3','audio/mpeg')
    print song
