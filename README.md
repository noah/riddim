## Introduction 

**riddim** is a digital jukebox server written in python2 with the
following features:

        + CLI Playlist management
        + MP3 metadata stream encoding
        + Transcoding of all audio formats supported by FFmpeg
        + Track scrobbling to Last.fm
        + Low memory footprint

## Installation and mini-tutorial

```
# pip2 install mutagen scrobbler
% git clone https://github.com/noah/riddim.git
% cd riddim
% $EDITOR riddim.cfg
% ./riddim -k start
% ./riddim -e /path/to/some/music
% vlc -I curses http://localhost:18944
```
Music should now be coming out of your speakers.

Once you have started the server, as above, you can manipulate the
playlist:

```bash
% riddim -e Siamese\ Dream                      # add a directory of tracks to the playlist ...
% riddim -e 03.\ Today.mp3                      # ... or a single track
% riddim -i 9                                   # skip to 9th track in the playlist
% riddim -c ^Smashing                           # clear tracks from playlist via regex pattern
% riddim -c .                                   # clear all tracks
% riddim -h                                     # show help
% aliased to riddim -q | less --pattern="^\*"   # show playlist at current track 
```
N.B.: The length of time it takes before changes to the playlist will be
reflected to a client listener is determined by the variable `buffer_size`
in `riddim.cfg`.


## Audioscrobbler

If you want to scrobble tracks, you will need to set `scrobble=True` in
`riddim.cfg` and also create a `scrobbler.cfg` file with the following
contents:

    [scrobbler]
    username='Your Username'
    password='Your Password'

## Configuring Apache (optional)

**riddim** works well in combination with Apache or another web server.
The following configuration enables streaming from a `VirtualHost` (so
you can have a pretty url like `http://stream.your.tld`).  I use
something like this:

```
<VirtualHost *:80>
   ServerName stream.your.tld
   ServerAdmin you@your.tld
   ProxyPass / http://192.168.1.2:18944
</VirtualHost>      
```

Of course, **riddim** will need to be running on host
`192.168.1.2:18944` for that to work, but if you set it up correctly you
can point your music streamer at `http://stream.your.tld` and listen to
the music that way (cough ... thus defeating corporate firewalls ...
cough).

## Contributors

I ripped off some code from Amarok for the streaming logic (lib/streamer).

## TODO

+ Web control (?)
