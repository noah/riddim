# -*- coding: utf-8 -*-

import os
import shlex
import subprocess
import mad

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


from logger import log


class AudioUtil(object):
    ################################################################################
    #
    #  Copyright (C) 2010  Noah K. Tilton <noah@0x7be.org>
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
    # Convert and array of "bits" (MSB first) to its decimal value.
    def bin2dec(self, x):
        bits = []
        bits.extend(x)
        bits.reverse()

        multi = 1
        value = long(0)
        for b in bits:
            value += b * multi
            multi *= 2
        return value

    # Accepts a string of bytes (chars) and returns an array of bits
    # representing the bytes in big endian byte (Most significant byte/bit first)
    # order.  Each byte can have its higher bits ignored by passing an sz arg.
    def bytes2bin(self, bytes, sz=8):
        if sz < 1 or sz > 8:
            raise ValueError("Invalid sz value: " + str(sz))

        retVal = []
        for b in bytes:
            bits = []
            b = ord(b)
            while b > 0:
                bits.append(b & 1)
                b >>= 1
            if len(bits) < sz:
                bits.extend([0] * (sz - len(bits)))
            elif len(bits) > sz:
                bits = bits[:sz]

            # Big endian byte order.
            bits.reverse()
            retVal.extend(bits)

        if len(retVal) == 0:
            retVal = [0]
        return retVal


class Audio(AudioUtil):

    def __init__(self, path):
        self.path = path
        self.corrupt = False
        self.mimetype = subprocess.Popen(shlex.split("/usr/bin/file -i \"%s\"" % path),
                stdout=subprocess.PIPE).communicate()[0].strip().split(': ')[1].split(';')[0]

        if self.mimetype == 'audio/x-flac':
            self.audio = FLAC(path)
        else:
            # assume mp3
            if self.mimetype != 'audio/mpeg':
                log.error("Mimetype %s unsupported %s" % \
                        (self.mimetype, self.path))
            # Handle it anyway --  sometimes mp3 will have content-type
            # application/octet-stream, but this is ok.
            self.audio = MP3(path, ID3=EasyID3)

    def __getitem__(self, key):
        try:
            return self.data()[key]
        except KeyError:
            return None

    def __str__(self):
        tags = self.tags()
        return ' - '.join([tags[0], tags[2]])

    def bitrate(self):
        bitrate = -1
        try:
            bitrate = self.audio.info.bitrate
        except AttributeError:
            pass

        try:
            bitrate = self.audio.info['bitrate']
        except TypeError:
            pass

        #log.warning("No bitrate available for %s" % self.path)
        return bitrate

    def tracknumber(self):
        tracknumber = -1
        try:
            tracknumber = self.audio.tracknumber
        except AttributeError:
            pass
        try:
            tracknumber = self.audio['tracknumber']
        except KeyError:
            pass

        if tracknumber == -1:
            #log.warning("No tracknumber available for %s" % self.path)
            pass

        return tracknumber

    def title(self):
        return ' - '.join(self.tags())

    def tags(self):
        artist = album = title = ""
        try:
            artist  = self.audio['artist'][0]
            album   = self.audio['album'][0]
            title   = self.audio['title'][0]
        except KeyError, e:
            #log.warning("no %s found" % e)
            pass
        except Exception, e:
            log.exception(e)
            log.exception(self.audio)
            log.exception("Couldn't parse mimetype for %s" % self.path)
            self.corrupt = True
        return [artist, album, title]

    def length(self):
        length = 0
        if self.mimetype == 'audio/mpeg':
            try:
                length = (mad.MadFile(self.path).total_time() / 1000)
            except Exception, e:
                log.exception("Couldn't get time for %s: %s" %\
                        (self.path, e))
        elif self.mimetype == 'audio/x-flac':
            try:
                length = self.audio.info.length
            except e:
                log.exception("Couldn't get time for %s" % self.path)
        return length

    def size(self):
        return os.stat(self.path)[6]

    def start(self):
        # lifted from amarok
        f = open(self.path, 'r')
        id3 = f.read(3)
        if not id3 == "ID3": return 0
        f.seek(6)
        L = f.read(4)
        b2b = self.bytes2bin(L, 7)
        start = self.bin2dec(b2b) + 10
        f.close()
        return start

    def data(self):
        return {
                'size': self.size(),
                'tags': self.tags(),
                'title': self.title(),
                'bitrate': self.bitrate(),
                'length' : self.length(),
                'start': self.start(),
                'mimetype': self.mimetype,
                'tracknumber' : self.tracknumber()
        }

if  __name__ == '__main__':
    """
    import glob
    for file in glob.glob("./audio/*"):
        if not os.path.isdir(file):
            song = Audio(file)
            print song
    a = [0,1,0,1,0,1,1,0,0,1,1,0,1,0,0,1];
    A = AudioUtil()
    print A.bin2dec(a)
    b = ['a', 'b']
    A = AudioUtil()
    print A.bytes2bin(b)
    """
    ra = Audio("/media/_rock/islands/return_to_the_sea/07_jogging_gorgeous_summer.mp3")
    print ra.start()
