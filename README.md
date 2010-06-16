RiDDiM -- A modern music streamer, written in python.

Design goals
    * Modularity
    * Use python stdlib only
    * Borrow/steal ideas from other good media players (cmus)
        * Vi bindings
        * Verbs copy/pasted from cmus-remote

TODO
  ICY metadata

Synopsis
    Usage: riddim.py [options]

    Options:
      -h, --help            show this help message and exit
      -k SIGNAL, --signal=SIGNAL
                            signal stop/start/status
      -P PORT, --port=PORT  port number to try
      -Q, --query           display server state
      -S, --shuffle         toggle shuffle
      -R, --repeat          toggle repeat
      -e, --enqueue         enqueue track(s) onto playlist
      -f, --foreground      don't for the server
      -c, --clear           clear playlist
      -n, --next            proceed to next track
      -u, --pause           pause playback
      -p, --play            start playback
      -s, --stop            stop playback
      -r, --prev            go back to previous track
