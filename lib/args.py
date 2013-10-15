import sys
from argparse import ArgumentParser
# from lib.logger import log
from lib.config import Config


class Args(object):

    def __init__(self):
        self.config = Config().config
        parser      = ArgumentParser()

        # server controls a la apachectl
        parser.add_mutually_exclusive_group().add_argument("-k", "--signal",
                        help="signal stop/start/status",
                        choices=["stop", "start", "restart"],
                        default=False)

        # CLI options
        [parser.add_argument( *_, **__) for _, __ in [
                [("-C", "--continue"), {
                    "action"    : "store_true",
                    "default"   : False,
                    "help"      : "toggle continue",
                    "dest"      : "kontinue"  # avoid kw collision
                }],
                [("-N", "--next-album"), {
                    "action"    : "store_true",
                    "default"   : False,
                    "help"      : "skip forward to the next album",
                }],
                [("-A", "--next-artist"), {
                    "action"    : "store_true",
                    "default"   : False,
                    "help"      : "skip forward to the next artist",
                }],
                [("-c", "--clear"), {
                    "help"      : "clear playlist of tracks matching REGEX",
                    "metavar"   : "REGEX"
                }],
                [("-e", "--enqueue"), {
                    "metavar"   : "/PATH/TO/TRACKS",
                    "help"      : "enqueue track(s)",
                    "nargs"     : "+"
                }],
                [( "-n", "--index"), {
                    "help"      : "set now playing to index INDEX",
                    "metavar"   : "INDEX",
                    "const"     : "+1",
                    "nargs"     : "?"
                }],
                [("-p", "--port"), {
                    "type"      : int,
                    "default"   : 18944 # (ridd)
                }],
                [("-q", "--query"), {
                    "action"    : "store_true",
                    "default"   : False,
                    "help"      : "display server state"
                }],
                [("-r", "--repeat"), {
                    "action"    : "store_true",
                    "default"   : False,
                    "help"      : "Toggle song repeat"
                }],
                [("-s", "--shuffle"), {
                    "action"    : "store_true",
                    "default"   : False,
                    "help"      : "Toggle shuffle"
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
