#!/usr/bin/env python2
import sys, os

'''This module is used to fork the current process into a daemon.

Almost none of this is necessary (or advisable) if your daemon
is being started by inetd. In that case, stdin, stdout and stderr are
all set up for you to refer to the network connection, and the fork()s
and session manipulation should not be done (to avoid confusing inetd).
Only the chdir() and umask() steps remain as useful.

References:
    UNIX Programming FAQ
        1.7 How do I get my program to act like a daemon?
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16

    Advanced Programming in the Unix Environment
        W. Richard Stevens, 1992, Addison-Wesley, ISBN 0-201-56317-7.
'''

def daemonize (stdin='/dev/null', stdout='/dev/null', stderr='/dev/null', reset_umask=False):
    '''This forks the current process into a daemon.
    The stdin, stdout, and stderr arguments are file names that
    will be opened and be used to replace the standard file descriptors
    in sys.stdin, sys.stdout, and sys.stderr.
    These arguments are optional and default to /dev/null.
    Note that stderr is opened unbuffered, so
    if it shares a file with stdout then interleaved output
    may not appear in the order that you expect.
    '''

    # Do first fork.
    pid = os.fork()
    if pid > 0:
        sys.exit(0)   # Exit first parent.

    # Decouple from parent environment.
    os.chdir("/")
    if reset_umask:
        os.umask(0)
    os.setsid()

    # Do second fork.
    pid = os.fork()
    if pid > 0:
        os._exit(0)   # Exit second parent, without calling cleanup handlers.

    # Now I am a daemon!

    # Redirect standard file descriptors.
    si = open(stdin, 'r')
    so = open(stdout, 'a+')
    se = open(stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

def main ():
    '''This is an example main function run by the daemon.
    This prints a count and timestamp once per second.
    '''
    import time
    sys.stdout.write ('Daemon started with pid %d\n' % os.getpid() )
    sys.stdout.write ('Daemon stdout output\n')
    sys.stderr.write ('Daemon stderr output\n')
    c = 0
    while 1:
        sys.stdout.write ('%d: %s\n' % (c, time.ctime(time.time())) )
        sys.stdout.flush()
        c = c + 1
        time.sleep(1)

if __name__ == "__main__":
    daemonize('/dev/null','/tmp/daemon.log','/tmp/daemon.log')
    main()
