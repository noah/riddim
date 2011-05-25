import threading, time, os, datetime, sys, Queue, hashlib
from urllib import quote, unquote
import ConfigParser
from mutagen.id3 import ID3

try:
    import scrobbler
except ImportError:
    print """Oops.  You need to run:\n\
    % pip install scrobbler"""
    sys.exit(-1)

NOW_PLAYING=0
PLAYED=1

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('riddim')

class ScrobbleItem:
    def __init__(self, scrobble_type, song):
        self.type = scrobble_type
        self.song = song

def escape(str):
    return unquote(str).decode('utf-8')

class RiddimScrobbler(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def login(self):
        config = ConfigParser.ConfigParser()
        cwd = os.path.realpath(os.path.dirname(__file__) + '/..')
        config.read(os.path.join(cwd, 'scrobbler.cfg'))
        username = config.get('scrobbler', 'username')
        password = hashlib.md5(config.get('scrobbler', 'password')).hexdigest()
        try:
            scrobbler.login(user=username, password=password)
        except Exception as e:
            print "Couldn't login: %s" % e

    def run(self):
        # well this is just fugly.  call it "experimental"
        while True:
            try:
                scrobble_item = self.queue.get(0)
                try:
                    song = scrobble_item.song
                    type = scrobble_item.type

                    (artist, album, track) = [escape(item) for item in song['audio']['tags']]

                    if type == NOW_PLAYING:
                        print "scrobbling now playing %s %s %s" % (artist, track, album)
                        self.login()
                        scrobbler.now_playing(
                                artist,
                                track
                        )
                        # now_playing auto flushes, apparently.  don't call
                        # flush here or it will throw an exception, which is not
                        # what we want.
                    elif type == PLAYED:
                        # See: http://exhuma.wicked.lu/projects/python/scrobbler/api/public/scrobbler-module.html#login
                        if (song['audio']['length'] > 30) and len(artist) and len(track):
                            print "scrobbling played %s %s %s %s" %\
                                    (artist, track, album, song['audio']['length'])
                            self.login()
                            scrobbler.submit(
                                artist,
                                track,
                                int(time.mktime(datetime.datetime.now().timetuple())),
                                source=escape('P'),
                                length=int(song['audio']['length']),
                                album=escape(album),
                            )
                            scrobbler.flush()
                except Exception as e:
                    print "scrobble error: %s" % e
                    # put it back
                    self.queue.put(scrobble_item)
            except Queue.Empty:
                pass

            # AS API enforced limit -- do not change.
            time.sleep(10)
