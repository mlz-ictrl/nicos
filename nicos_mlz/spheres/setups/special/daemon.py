# -*- coding: utf-8 -*-

description = 'setup for the execution daemon'

group = 'special'

devices = dict(
    UserDB = device('nicos_mlz.devices.proposaldb.Authenticator'),

    Auth   = device('nicos.services.daemon.auth.list.Authenticator',
        hashing = 'md5',
        passwd = [('guest', '', 'guest'),
                  ('spheres', '4c0a917d493cb63f3ff5006981878727', 'user'),
                  ('jcns', '51b8e46e7a54e8033f0d7a3393305cdb', 'admin'),
        ],
    ),
    Daemon = device('nicos.services.daemon.NicosDaemon',
        server = '',
        authenticators = ['Auth'],
        loglevel = 'info',
        autosimulate = True,
    ),
)
