import os
import re
from argparse import ArgumentParser

from lib.config import Config

class Args(object):

    def __init__(self):
        self.config = Config().config
        parser      = ArgumentParser()

        # server controls a la apachectl
        signals = ["stop", "start", "restart"]
        mutex_group = parser.add_mutually_exclusive_group()
        mutex_group.add_argument("-k", "--signal",
                                help="signal stop/start/status",
                                choices=signals,
                                default=False)

        # playlist manipulation
        parser.add_argument("-c", "--clear",
                                help="clear playlist of tracks matching REGEX",
                                metavar="REGEX")
        parser.add_argument("-i", "--index",
                                type=int,
                                metavar="INDEX",
                                help="set now playing to index INDEX")
        parser.add_argument("-q", "--query",
                                action="store_true",
                                default=False,
                                help="display server state")
        parser.add_argument("-e", "--enqueue",
                                metavar="/PATH/TO/TRACKS",
                                help="enqueue track(s)", nargs="+")
        # TODO
        #         '-R' : ['--repeat',     'toggle repeat',            'store_true',   False],
        #         '-S' : ['--shuffle',    'toggle shuffle',           'store_true',   False],

        self.args = parser.parse_args()

    # expose self.args to external classes
    def __getattr__(self, attr):
        return self.args.__dict__[attr]

    def __repr__(self):
        return dict(vars(self.args))
