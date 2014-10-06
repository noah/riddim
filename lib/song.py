# -*- coding: utf-8 -*-

import os
import sys
import codecs
import subprocess

try:
    from mutagen import File as MutagenFile
except:
    print u"""
    You need mutagen
        # pacman -S mutagen
        on archlinux
    """
    sys.exit(0)


from logger         import log
from lib.config     import Config


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
            raise ValueError(u"Invalid sz value: " + str(sz))

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
        try:
            self.path       = path.decode('utf-8')
        except UnicodeDecodeError, e:
            latin1path      = path.decode('latin1')
            # decoding file name into utf8 failed but latin1 worked.
            # filename contains latin1-only characters (?)
            # for example \xc2, \xa0
            # encode path in in utf8
            self.path       = latin1path.encode('utf-8').decode('utf-8')
            log.info(u"bad chars, mv {} -> {}".format(latin1path, self.path))
            import shutil
            shutil.move(path, self.path) # yes, first arg should be `path'.
            path = None # <- be sure not to use this again - it no longer exists.

        self.ext            = os.path.splitext(self.path)[1].lower().strip('.')
        self.corrupt        = False
        self.bitrate        = self.length = 0
        self.title          = self.artist = self.album = u''
        self.tracknumber    = -1
        self.mimetype       = subprocess.Popen([u"/usr/bin/file", u"--mime-type", self.path],
                                         stdout=subprocess.PIPE).communicate()[0].split(": ")[-1].rstrip()
        av                  = self.mimetype[0:5]
        maybeaudio          = (self.mimetype == u'application/octet-stream') and (self.ext in Config.audio_types.values())

        # enqueue any audio file, or file that looks like an audio file
        if (av == u"audio") or maybeaudio:
            audio = None
            try:
                audio = MutagenFile( self.path, easy=True )
            except Exception, e:
                # e.g.,
                # "header size not synchsafe"
                # mutagen.mp3.HeaderNotFoundError: can't sync to an MPEG frame
                log.error(u"{} {}".format(e, self.path))
                self.corrupt = True

            if audio is None or self.corrupt:
                log.error(u"Mutagen is None {}".format(self.path))
            else:
                if len(audio) < 1:
                    # couldn't read metadata for some reason
                    log.warn(u"mutagen failed {}".format(self.path))
                else:
                    try:    self.bitrate        = int(audio.info.bitrate)
                    except: pass

                    try:    self.length         = int(audio.info.length)
                    except: pass

                    try:
                        self.artist         = audio.get(u'artist', [''])[0]
                        self.album          = audio.get(u'album', [''])[0]
                        self.title          = audio.get(u'title', [''])[0]
                        if u'tracknumber' in audio:
                            tn = audio.get(u'tracknumber')[0]
                            # test for track number listed as i/n
                            tn = tn.split(u"/")[0]
                            # convert to a number
                            try:
                                self.tracknumber = int(tn, base=10)
                            except ValueError:
                                pass
                                #  not a base10 integer.  hex?
                                # try:
                                #     self.tracknumber = int(tn, base=16)
                                # except ValueError:
                                #     pass # give up
                    except Exception, e:
                        log.debug(u"track data error %s %s %s %s", self.path, self.mimetype, e, audio)

        elif av == u"video":
            # Allow videos to be enqueued, from which we will (attempt)
            # to extract a wav and transcode to mp3 on the fly...
            self.tracknumber = self.length = 100000
            self.artist      = self.album = self.title = os.path.basename(self.path)
        else:
            #log.warn(u"Mimetype {} unsupported {}".format(self.mimetype,
            #                                           self.path))
            self.corrupt = True

        if not self.corrupt:
            self.size  = os.stat(self.path).st_size
            self.start = self._start()
            self.tags  = filter(lambda x: x != '', self._tags())

    def __unicode__(self):
        if self.tags and len(self.tags): return u' - '.join(self.tags)
        return self.path

    def __str__(self):
        return self.__unicode__()

    def __getattr__(self, attr):
        log.debug(u"attribute lookup for %s" % attr)
        try:
            return self.__dict__[attr]
        except KeyError:
            return None

    def _tags(self):
        _tags = [unicode(self.tracknumber).zfill(2), self.artist, self.album, self.title]
        if None in _tags[1:] or u'' in _tags: _tags = [u"", self.path, u"", u""]
        return _tags

    def _start(self):
        # lifted from amarok
        f = codecs.open(self.path, u'r')
        id3 = f.read(3)
        if not id3 == "ID3": # (3 bytes, *not* unicode)
            return 0
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


#song = Song(sys.argv[1])
