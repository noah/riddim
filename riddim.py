#!/usr/bin/env python2

import sys, time

"""
riddim.py Copyright (c) <2010> <Noah K. Tilton> <noahktilton@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from lib.logger import log
from lib.cli import RiddimCLI

if __name__ == '__main__':

    cli = RiddimCLI( __file__ )

    try: # handle init signals
        {
                'start'     : cli.start,
                'stop'      : cli.stop,
                'restart'   : cli.restart,
                'status'    : cli.status,
        }[cli.o.signal]()
    except KeyError: pass


    flag = cli.o.flag

    if flag:

        opts = cli.o.options # handle flags
        try:
            print {          # no arg
                    'pause'     : cli.pause,
                    'query'     : cli.query,
                    'stop'      : cli.stop
            }[flag]()
        except KeyError: pass

        try:                    # arg
            print {
                    'enqueue'   : cli.enqueue,
                    'index'     : cli.index,
                    'clear'     : cli.clear,
            }[flag](eval("opts.%s" % flag))
        except KeyError: pass

        #except Exception, e:
        #    log.exception(e)
        #    sys.exit(-1)

    sys.exit(0)
