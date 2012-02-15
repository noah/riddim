#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
riddim.py Copyright (©) <2012> <Noah K. Tilton> <noahktilton@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

import sys, time, codecs, socket
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

from lib.logger import log
from lib.args import Args
from lib.riddim import Riddim

if __name__ == "__main__":

    args    = Args()
    riddim  = Riddim( args )

    if args.signal:
        {
                "start"     : riddim.start,
                "stop"      : riddim.stop,
                "restart"   : riddim.restart,
                "status"    : riddim.status,
        }[ args.signal ]()

    elif args.query:
        print riddim.query()
    else:
        # dispatch variadic args to the appropriate method
        for action, arg in args.args_dict.items():
            try:
                print {
                    "clear"         : riddim.clear,
                    "index"         : riddim.index,
                    "query"         : riddim.query,
                    "enqueue"       : riddim.enqueue
                }[ action ]( arg )
            except KeyError: pass

    sys.exit(0)
