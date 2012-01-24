#  -*- coding: utf-8 -*-

name = 'setup for the cache server'
group = 'special'

devices = dict(
    DB     = device('nicos.cache.server.FlatfileCacheDatabase',
                    storepath = 'data/cache',
                    loglevel = 'info'),

    Server = device('nicos.cache.server.CacheServer',
                    db = 'DB',
                    server = 'localhost',
                    loglevel = 'info'),
)
