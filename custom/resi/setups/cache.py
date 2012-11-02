#  -*- coding: utf-8 -*-

description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB     = device('services.cache.server.MemoryCacheDatabase',
                    storepath = '/tmp/data/cache',
                    maxcached = 20,
                    granularity = 3,
                    loglevel = 'warning'),

    Server = device('services.cache.server.CacheServer',
                    db = 'DB',
                    server = 'resi1',
                    loglevel = 'info'),
)
