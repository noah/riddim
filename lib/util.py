# -*- coding: utf-8 -*-

from signal import signal, SIGINT, SIG_IGN

def init_worker():
    signal(SIGINT, SIG_IGN)

def is_stream(arg):
    #from urlparse import urlparse
    # TODO
    return False

def filesizeformat(bytes):
    """
    Formats the value like a 'human-readable' file size (i.e. 13 KB, 4.1 MB,
    102 bytes, etc).  Modified django
    """
    try:    bytes = float(bytes)
    except (TypeError, ValueError, UnicodeDecodeError):
        return u"%s bytes" % 0

    pretty = lambda x: round(x, 1)

    if bytes < 1024: return u"%s bytes" % pretty(bytes)
    if bytes < 1024 * 1024: return u"%s KB" % pretty((bytes / 1024))
    if bytes < 1024 * 1024 * 1024: return u"%s MB" % pretty((bytes / (1024 * 1024)))
    if bytes < 1024 * 1024 * 1024 * 1024: return u"%s GB" % pretty((bytes / (1024 * 1024 * 1024)))
    if bytes < 1024 * 1024 * 1024 * 1024 * 1024: return u"%s TB" % pretty((bytes / (1024 * 1024 * 1024 * 1024)))
    return u"%s PB" % pretty((bytes / (1024 * 1024 * 1024 * 1024 * 1024)))


