#  -*- coding: utf-8 -*-

description = 'setup for the cache server'
group = 'special'

devices = dict(
    DBmem     = device('services.cache.server.MemoryCacheDatabase',
                    loglevel = 'info'),
    DBfile     = device('services.cache.server.FlatfileCacheDatabase',
                    storepath = '/home/resi/pedersen/nicos-cache',
                    loglevel = 'info'),

    Server = device('services.cache.server.CacheServer',
                    db = 'DBmem',
                    server = 'resi1',
                    loglevel = 'info'),
)
