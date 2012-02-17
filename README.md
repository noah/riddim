## Introduction 

riddim is an audio streaming server written in python.  It has the
following features:

        + FLAC transcoding (lame)
        + Low memory footprint
        + Track scrobbling to Last.fm


## Digital jukebox

riddim maintains an internal list of mp3s that it plays in sequential
order, like a digital jukebox.  

Commands are used to manipulate the internal playlist state (enqueue,
dequeue, display).

## Synopsis

```bash
% riddim -h
usage: riddim [-h] [-k {stop,start,restart}] [-c REGEX] [-i INDEX] [-q]
              [-e /PATH/TO/TRACKS [/PATH/TO/TRACKS ...]]

optional arguments:
  -h, --help            show this help message and exit
  -k {stop,start},      --signal {stop,start}
                        signal stop/start/status
  -c REGEX, --clear REGEX
                        clear playlist of tracks matching REGEX
  -i INDEX, --index INDEX
                        set now playing to index INDEX
  -q, --query           display server state
  -e /PATH/TO/TRACKS [/PATH/TO/TRACKS ...], --enqueue /PATH/TO/TRACKS [/PATH/TO/TRACKS ...]
                        enqueue track(s)

```

The config file has some tweaks but you shouldn't have to change the defaults:

        % $EDITOR riddim.cfg

Like apachectl, riddim can be started, stopped, and
restarted by passing the -k flag.

        % ./riddim.py -k start

## Using riddim to listen to streaming music

On the server side, queue up some tracks:

```bash
% ./riddim.py --enqueue ./path/to/some_music
```

From the client, connect to the server:

```bash
% mplayer http://server:18944
% vlc -I curses http://server:18944
% cmus http://server:18944
```

(Music should now be coming out of your speakers).  Display the
playlist:

```bash
  % ./riddim.py -q

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
```

You can remove tracks by passing a regex to the `-c` (clear) flag:

```bash
    % riddim -c Jungle
```
 
## Dependencies

```bash
        % python --version
        Python 2.6.5

        % pacman -Q mutagen  
        mutagen 1.19-1

        % pacman -Q pymad
        pymad 0.6-3
```

## Optional Dependencies
    
```bash
        # pip install scrobbler
```

If you want to scrobble tracks, you will need to set scrobble=True in
riddim.cfg and also create a scrobbler.cfg file with the following
contents:

    [scrobbler]
    username='Your Username'
    password='Your Password'

## Contributors

I ripped off some code from Amarok for the streaming logic (lib/streamer).

## TODO

+ Web control
+ Shuffle/repeat/advanced playlist functionality
