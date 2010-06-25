RiDDiM ~~ SHOUTcast on a diet
==============================================================

Synopsis
---------------------------------------------------------------

        % ./riddim.py -k start
        % ./riddim.py --enqueue ./path/to/mp3s
        % mplayer http://localhost:18944
 
"Advanced" Use
---------------------------------------------------------------

        % ./riddim.py -h
        Usage: riddim.py [options]

        Options:
          -h, --help            show this help message and exit
          -Q, --query           display server state
          -P PORT, --port=PORT  port number to try
          -S, --shuffle         toggle shuffle
          -R, --repeat          toggle repeat
          -e ENQUEUE, --enqueue=ENQUEUE
                                enqueue track(s) onto playlist
          -f, --foreground      don't fork the server
          -c, --clear           clear playlist
          -n, --next            proceed to next track
          -k SIGNAL, --signal=SIGNAL
                                signal stop/start/status
          -u, --pause           pause playback
          -p, --play            start playback
          -s, --stop            stop playback
          -r, --prev            go back to previous track


Everything is implemented in the client except for shuffle, repeat, and play (which is implicit in connecting to the stream).


Dependencies
---------------------------------------------------------------

        % python --version
        Python 2.6.5

TODO
---------------------------------------------------------------

## Auth
## Scrobbling
## Transcoding (flac, ogg, etc)
## Web control
## Crossfading
