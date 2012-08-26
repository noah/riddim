# -*- coding: utf-8 -*-

import os
import shlex
import subprocess
# import mad

try:
    # easyid3 maps the real id3 standard tag names to the same as the flac ones
    from mutagen.mp3 import MP3, HeaderNotFoundError
    from mutagen.flac import FLAC
except:
    print """
    You need mutagen
        # pacman -S mutagen
        on archlinux
    """
    import sys
    sys.exit(0)


from logger import log


# todo make these static
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


# FIXME
def _mp3get(_mp3, key, default):
    try:    return unicode(_mp3[key])
    except: return default


# FIXME
def _flacget(_flac, key, default):
    try:    return unicode(_flac[key][0])
    except: return default


class Song(AudioUtil):

    def __init__(self, path):
        self.path       = path
        self.corrupt    = False
        self.mimetype   = subprocess.Popen(shlex.split("/usr/bin/file -i \"%s\"" % path),
                stdout=subprocess.PIPE).communicate()[0].strip().split(': ')[1].split(';')[0]

        if self.mimetype == 'audio/x-flac':
            _flac = FLAC(path)
            try:    self.tracknumber = int(_flacget(_flac, "tracknumber", 0))
            except: self.tracknumber = 0
            self.artist = _flacget(_flac, "artist", "")
            self.album  = _flacget(_flac, "album", "")
            self.title  = _flacget(_flac, "title", "")
            self.length = int(_flac.info.length)
            #"bitrate"           : _flac.info.bitrate,
        elif self.mimetype in ['audio/mpeg', 'application/octet-stream']:
                # Handle it anyway --  sometimes mp3 will have content-type
                # application/octet-stream, but this is ok.
                try:
                    _mp3 = MP3(path)
                    try:    self.tracknumber = int( _mp3get(_mp3, "TRCK", 0) )
                    except: self.tracknumber = 0
                    self.artist     = _mp3get(_mp3, "TPE1", "")
                    self.album      = _mp3get(_mp3, "TALB", "")
                    self.title      = _mp3get(_mp3, "TIT2", "")
                    self.length     = int(_mp3.info.length)
                    self.bitrate    = int(_mp3.info.bitrate)
                except HeaderNotFoundError, e:
                    log.error("File %s corrupt: %s" % (path, e))
                    self.corrupt = True
        else:
            log.warn("Mimetype %s unsupported %s" % \
                    (self.mimetype, self.path))
            self.corrupt = True

        if not self.corrupt:
            self.size  = os.stat(self.path)[6]
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
        if None in _tags: _tags = [self.path, "", ""]
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
