# -*- coding: utf-8 -*-
import sys
from argparse import ArgumentParser
# from lib.logger import log
from lib.config import Config


class Args(object):

    def __init__(self):
        self.config = Config().config
        parser      = ArgumentParser()

        # server controls a la apachectl
        parser.add_mutually_exclusive_group().add_argument(u"-k", u"--signal",
                        help=u"signal stop/start/status",
                        choices=[u"stop", u"start", u"restart"],
                        default=False)

        # CLI options
        [parser.add_argument( *_, **__) for _, __ in [
                [(u"-C", u"--continue"), {
                    u"action"    : u"store_true",
                    u"default"   : False,
                    u"help"      : u"toggle continue",
                    u"dest"      : u"kontinue"  # avoid kw collision
                }],
                [(u"-N", u"--next-album"), {
                    u"action"    : u"store_true",
                    u"default"   : False,
                    u"help"      : u"skip forward to the next album",
                }],
                [("-A", "--next-artist"), {
                    u"action"    : u"store_true",
                    u"default"   : False,
                    u"help"      : u"skip forward to the next artist",
                }],
                [(u"-c", u"--clear"), {
                    u"help"      : u"clear playlist of tracks matching REGEX",
                    u"metavar"   : u"REGEX"
                }],
                [(u"-e", u"--enqueue"), {
                    u"metavar"   : u"/PATH/TO/TRACKS",
                    u"help"      : u"enqueue track(s)",
                    u"nargs"     : u"+"
                }],
                [( u"-n", u"--index"), {
                    u"help"      : u"set now playing to index INDEX",
                    u"metavar"   : u"INDEX",
                    u"const"     : u"+1",
                    u"nargs"     : u"?"
                }],
                [(u"-p", u"--port"), {
                    u"type"      : int,
                    u"default"   : 18944 # (ridd)
                }],
                [(u"-q", u"--query"), {
                    u"action"    : u"store_true",
                    u"default"   : False,
                    u"help"      : u"display server state"
                }],
                [(u"-r", u"--repeat"), {
                    u"action"    : u"store_true",
                    u"default"   : False,
                    u"help"      : u"Toggle song repeat"
                }],
                [(u"-s", u"--shuffle"), {
                    u"action"    : u"store_true",
                    u"default"   : False,
                    u"help"      : u"Toggle shuffle"
                }],
        ]]

        self.args       = parser.parse_args()
        self.args_dict  = vars(self.args)

        # remove null (unselected) and default options
        for op, arg in self.args_dict.items():
            if not arg: del self.args_dict[op]

        if len(self.args_dict.keys()) == 1: # (port always present)
            # bail on no arguments
            parser.print_help()
            sys.exit(-1)

    # expose self.args to external classes
    def __getattr__(self, attr):
        try:
            return self.args.__dict__[attr]
        except KeyError:
            return None

    def __repr__(self):
        return dict(vars(self.args))
