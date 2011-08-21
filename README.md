## Introduction 

riddim is an audio streaming server written in python.  It has the
following features:

        + Multithreaded, supports multiple clients
        + FLAC transcoding (lame)
        + Low memory footprint
        + Track scrobbling to Last.fm


## Networking

riddim maintains an internal list of mp3s that it plays in sequential
order, just like a digital jukebox.  It accepts two types of
connections:

1.  HTTP GET requests
1.  XMLRPC requests

In the first instance, it begins streaming mp3 data to the client.
In the second instance, it attempts to interpret the request as a
command.

Commands are used to manipulate the internal playlist state
(enqueue, dequeue, display).

## Synopsis

The first thing you'll probably want to do is edit the general config
file. 

        % $EDITOR riddim.cfg

riddim can be run either in the foreground (so that you can see
debugging output) or as a backgrounded process.  This is controlled by
the -f flag.  Like apachectl, riddim can be started, stopped, and
restarted by passing the -k flag.

        % ./riddim.py -k start

Next, queue up some tracks:


        % ./riddim.py --enqueue ./path/to/bob_marley

Connect a client:

        % mplayer http://localhost:18944

(Music should now be coming out of your speakers).  Display the
playlist:

        % ./riddim.py -Q     


        [riddim]  uptime:  00:00:13
        playing:  Bob Marley & The Wailers - Stop That Train
        10 tracks ******************************
        * Bob Marley & The Wailers - Intro
          Bob Marley & The Wailers - Rasta Man Chant
          Bob Marley & The Wailers - Slave Driver
          Bob Marley & The Wailers - Stop That Train
          Bob Marley & The Wailers - No More Trouble
          Bob Marley & The Wailers - 400 Years
          Bob Marley & The Wailers - Stir It Up
          Bob Marley & The Wailers - Concrete Jungle
          Bob Marley & The Wailers - Get Up Stand Up
          Bob Marley & The Wailers - Kinky Reggae
 
## "Advanced" Usage

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


## Dependencies

        % python --version
        Python 2.6.5

        % pacman -Q mutagen  
        mutagen 1.19-1

        % pacman -Q pymad
        pymad 0.6-3

## Optional Dependencies
    
        # pip install scrobbler

If you want to scrobble tracks, you will need to set scrobble=True in
riddim.cfg and also create a scrobbler.cfg file with the following
contents:

    [scrobbler]
    username='Your Username'
    password='Your Password'

## Contributors

I ripped off some code from Amarok for the streaming logic (lib/streamer).

## TODO

+ Auth (signing !)
+ Web control
+ import multiprocessing ...
