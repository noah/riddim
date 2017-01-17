# -*- coding: utf-8 -*-
import os
import socket
import codecs
import ConfigParser


def join_path(*args):
    return os.path.join(*args)



class Config(object):

        running         = True
        basepath        = os.path.dirname(os.path.dirname(__file__))
        config          = ConfigParser.ConfigParser()
        config.read( join_path(basepath, u'riddim.cfg') )

        authkey         = codecs.open(join_path(basepath, u"secret"), u'r').read()
        # set up some config stuff that we will need
        runpath         = join_path( u'/tmp')
        datapath        = join_path(basepath,  u'data', config.get( u'riddim', u'datafile'))
        #hostname        = socket.gethostname()
        hostname        = u"0.0.0.0"
        scrobble        = config.getboolean(u'riddim', u'scrobble')
        url             = config.get(u'riddim', u'url')
        lame_args       = config.get(u'riddim', u'lame_args')
        pool_size       = config.getint(u'riddim', u'pool_size')
        #
        metaint         = config.getint(u'icy', u'metaint')
        buffer_size     = config.getint(u'icy', u'buffer_size')
        notice_1        = config.get(u'icy', u'notice1')
        notice_2        = config.get(u'icy', u'notice2')
        icy_name        = config.get(u'icy', u'name', 0, {u'hostname': socket.gethostname()})
        icy_genre       = config.get(u'icy', u'genre')
        icy_url         = config.get(u'icy', u'url')
        icy_pub         = config.getboolean(u'icy', u'pub')
        icy_metaint     = config.getint(u'icy', u'metaint')
        content_type    = config.get(u'icy', u'content_type')
        audio_types     = {
            u'audio/mpeg'                   : u'mp3',
            u'audio/x-flac'                 : u'flac',
            u'audio/aac'                    : u'aac',
            u'audio/mp4'                    : u'm4a',
            u'audio/x-m4a'                  : u'm4a',
            u'audio/wav'                    : u'wav',
            u'audio/x-wav'                  : u'wav',
            u'audio/ogg'                    : u'ogg',
            u'audio/x-ape'                  : u'ape',
            u'video/mp4'                    : u'mp4',
            u'video/x-matroska'             : u'matroska',
            u'application/octet-stream'     : '?',
        }



        @classmethod
        def pidpath(cfg, port):
            return join_path(cfg.runpath, u"%s.%s" % (cfg.config.get(u'riddim', u'pidfile'), port))
