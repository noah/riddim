RiDDiM ~~ SHOUTcast on a diet
==============================================================

Synopsis
---------------------------------------------------------------

        % ./riddim.py -k start
        % ./riddim.py --enqueue ./path/to/bob_marley
        % mplayer http://localhost:18944
        % python riddim.py -Q     

        Playlist: playing:  Bob Marley & The Wailers - Stop That Train
        10 tracks ******************************
          Bob Marley & The Wailers - Intro
          Bob Marley & The Wailers - Rasta Man Chant
          Bob Marley & The Wailers - Slave Driver
        * Bob Marley & The Wailers - Stop That Train
          Bob Marley & The Wailers - No More Trouble
          Bob Marley & The Wailers - 400 Years
          Bob Marley & The Wailers - Stir It Up
          Bob Marley & The Wailers - Concrete Jungle
          Bob Marley & The Wailers - Get Up Stand Up
          Bob Marley & The Wailers - Kinky Reggae
 
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

Motivation
---------------------------------------------------------------
All of my mp3s are at my house, on my server.  When I'm elsewhere, I like to
listen to Radio Paradise, soma.fm, etc.  But sometimes those stations have a
sucky patch.  Or I just really need to hear some AC/DC.  Previously I'd been
mounting my mp3s over sshfs, which is _really_ slow, and thinking a lot about
setting up SHOUTcast.  Unfortunately, SHOUTcast seems to require a Ph.D. in
voodoo magic to set up and has way more bellz 'n whistlez than I need.


Caveat Emptor
---------------------------------------------------------------
This code may suck.


License 
---------------------------------------------------------------
Copyright (c) <2010> <Noah K. Tilton> <noah@downbe.at>

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

Contributors
---------------------------------------------------------------
I ripped off some code from Amarok for the streaming logic (lib/streamer).

TODO
---------------------------------------------------------------
# Auth
# Scrobbling
# Transcoding (flac, ogg, etc)
# Web control
# Crossfading
