#  -*- coding: utf-8 -*-

name = 'setup for the cache server'
group = 'special'

devices = dict(
    DB     = device('nicos.cache.server.DbCacheDatabase',
                    storepath = '/data/cache',
                    maxcached = 500),

    Server = device('nicos.cache.server.CacheServer',
                    db = 'DB',
                    server = 'pandasrv',
                    loglevel = 'info'),
)
