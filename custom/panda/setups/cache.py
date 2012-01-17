#  -*- coding: utf-8 -*-

description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB     = device('nicos.cache.server.DbCacheDatabase',
                    storepath = '/data/cache',
                    maxcached = 500),

    DB2     = device('nicos.cache.server.FlatfileCacheDatabase',
                    storepath = '/data/cache'),

    Server = device('nicos.cache.server.CacheServer',
                    db = 'DB2',
                    server = 'pandasrv',
                    loglevel = 'debug'),
)
