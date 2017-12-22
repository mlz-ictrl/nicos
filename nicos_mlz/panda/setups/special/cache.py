#  -*- coding: utf-8 -*-

description = 'setup for the cache server'

group = 'special'

devices = dict(
    DB2 = device('nicos.services.cache.server.FlatfileCacheDatabase',
        storepath = '/data/cache'
    ),
    Server = device('nicos.services.cache.server.CacheServer',
        db = 'DB2',
        server = '',
        loglevel = 'info'
    ),
)
