#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import codecs

from lib.args import Args
from lib.control import Control
from lib.playlist import Playlist

# needed if LANG=en_US.UTF-8
sys.stdout = codecs.getwriter('utf8')( sys.stdout )

if __name__ == "__main__":

    args = Args()

    if args.signal:
        {
                "start"     : Control().start,
                "stop"      : Control().stop,
                "restart"   : Control().restart,
        }[ args.signal ]()

    else:
        playlist = Playlist()
        if args.query:
            print playlist.query()
        elif args.shuffle:
            print playlist.shuffle()
        elif args.repeat:
            print playlist.repeat()
        elif args.kontinue:
            print playlist.kontinue()
        else:
            for action, arg in args.args_dict.items():
                    print {
                        "clear"         : playlist.clear,
                        "index"         : playlist.index,
                        "enqueue"       : playlist.enqueue,
                    }[ action ]( arg )

    try:    sys.stdout.close()
    except: pass
    try:    sys.stderr.close()
    except: pass
    sys.exit(0)
