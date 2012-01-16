#  -*- coding: utf-8 -*-

description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB     = device('nicos.cache.server.MemoryCacheDatabase',
                    storepath = '/tmp/data/cache',
                    maxcached = 20,
                    granularity = 3,
                    loglevel = 'debug'),

    Server = device('nicos.cache.server.CacheServer',
                    db = 'DB',
                    server = 'resi2',
                    loglevel = 'info'),
)
