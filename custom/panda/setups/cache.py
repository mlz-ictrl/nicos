#  -*- coding: utf-8 -*-

description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB     = device('services.cache.server.DbCacheDatabase',
                    storepath = '/data/cache',
                    maxcached = 500),

    DB2     = device('services.cache.server.FlatfileCacheDatabase',
                    storepath = '/data/cache'),

    Server = device('services.cache.server.CacheServer',
                    db = 'DB2',
                    server = 'pandasrv',
                    loglevel = 'info'),
)
