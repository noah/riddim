# -*- coding: utf-8 -*-

import os
import sys
import subprocess

try:
    from mutagen import File as MutagenFile
except:
    print """
    You need mutagen
        # pacman -S mutagen
        on archlinux
    """
    sys.exit(0)


from logger import log


# todo make these static
class AudioUtil(object):
    ################################################################################
    #
    #  Copyright (C) 2010  Noah K. Tilton <noah@tilton.co>
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


# FIXME
def _mp3get(_mp3, key, default):
    try:    return unicode(_mp3[key])
    except: return default


class Song(AudioUtil):

    def __init__(self, path):
        self.path       = path
        self.ext        = os.path.splitext(path)[1].lower()
        self.corrupt    = False
        self.bitrate    = self.length = 0
        self.title      = self.artist = self.album = ''
        try:
            self.mimetype = subprocess.Popen([
                    "/usr/bin/file", "--mime-type", path],
                    stdout=subprocess.PIPE).communicate()[0].split(": ")[-1].rstrip()
        except ValueError:
            print(path)

        av          = self.mimetype[0:5]
        maybeaudio  = (self.mimetype == 'application/octet-stream') and (self.ext in ['.mp3','.flac','.m4a'])

        # enqueue any audio file, or file that looks like an audio file
        if (av == "audio") or maybeaudio:
            audio = MutagenFile( path, easy=True )
            try:    self.bitrate        = int(audio.info.bitrate)
            except: pass

            try:    self.length         = int(audio.info.length)
            except: pass

            try:
                self.artist         = unicode( audio.get('artist', [''])[0] )
                self.album          = unicode( audio.get('album', [''])[0] )
                self.title          = unicode( audio.get('title', [''])[0] )
                self.tracknumber    = int( audio.get('tracknumber', [0])[0].split("/")[0] )
                print self.artist, self.album, self.title, self.tracknumber
                # split in above b/c sometimes encoders will list track numbers as "i/n"
            except Exception, e:
                print e, audio, audio.info.bitrate
        elif av == "video":
            # Allow videos to be enqueued, from which we will (attempt)
            # to extract a wav and transcode to mp3 on the fly...
            self.tracknumber = self.length = 100000
            self.artist      = self.album = self.title = os.path.basename(self.path)
        else:
            log.warn("Mimetype %s unsupported %s" %
                    (self.mimetype, self.path))
            self.corrupt = True

        if not self.corrupt:
            self.size  = os.stat(self.path).st_size
            self.start = self._start()
            self.tags  = filter(lambda x: x != '', self._tags())

    def __str__(self):
        if len(self.tags): return ' - '.join(self.tags)
        return self.path

    def __getattr__(self, attr):
        log.debug("attribute lookup for %s" % attr)
        try:
            return self.__dict__[attr]
        except KeyError:
            return None

    def _tags(self):
        _tags = [self.artist, self.album, self.title]
        if None in _tags or u'' in _tags: _tags = [self.path, "", ""]
        return _tags

    def _start(self):
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

    # for pickling
    def __getstate__(self): return self.__dict__

    def __setstate__(self, d): self.__dict__.update(d)

    def __getnewargs__(self): return None,
