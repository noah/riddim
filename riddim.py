#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import codecs
from multiprocessing import Pool

from lib.args       import Args
from lib.control    import Control
from lib.playlist   import Playlist
from lib.config     import Config
from lib.util       import init_worker
from lib.logger     import log

# needed if LANG=en_US.UTF-8
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

def main():
    args = Args()

    if args.signal:
        c = Control(args.port)
        if   args.signal == u"start"     : c.start()
        elif args.signal == u"stop"      : c.stop()
        elif args.signal == u"restart"   : c.restart()
    else:
        pool        = Pool(Config.pool_size, init_worker)
        playlist    = Playlist(args.port, pool)
        if   args.query                 :
            try:            print playlist.query()
            except IOError: pass # don't puke if quitting less(1)
        elif args.shuffle               : print playlist.shuffle()
        elif args.repeat                : print playlist.repeat()
        elif args.kontinue              : print playlist.kontinue()
        elif args.next_album            : print playlist.next_album()
        elif args.next_artist           : print playlist.next_artist()
        else:
            limit_to_extensions = args.args_dict.get('extensions', None)
            for action, arg in args.args_dict.items():
                try:
                    print {
                        u"clear"         : playlist.clear,
                        u"index"         : playlist.index,
                        u"enqueue"       : playlist.enqueue
                    }[ action ]( arg, limit_to_extensions )
                except KeyError: pass
                except KeyboardInterrupt:
                    pool.terminate()
                    pool.join()
                # except Exception, e:
                #     import traceback
                #     traceback.print_exc()
                #     print 'e', e
                #     sys.stderr.write( str(e) )
                else:
                    pool.close()
                    pool.join()

    try:        sys.stdout.close()
    except:     pass
    try:        sys.stderr.close()
    except:     pass

if __name__ == u"__main__":
    main()
