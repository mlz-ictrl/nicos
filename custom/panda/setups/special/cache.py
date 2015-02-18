#  -*- coding: utf-8 -*-

description = 'setup for the cache server'

group = 'special'

devices = dict(
    DB2    = device('services.cache.server.FlatfileCacheDatabase',
                    storepath = '/data/cache'),

    Server = device('services.cache.server.CacheServer',
                    db = 'DB2',
                    server = '',
                    loglevel = 'info'),
)
