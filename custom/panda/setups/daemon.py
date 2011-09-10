#  -*- coding: utf-8 -*-

name = 'setup for the execution daemon'
group = 'special'

devices = dict(
    Daemon = device('nicos.daemon.NicosDaemon',
                    server = 'localhost',
                    startupsetup = 'base',
                    loglevel = 'debug'),
)
