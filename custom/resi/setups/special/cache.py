#  -*- coding: utf-8 -*-

description = 'setup for the cache server'
group = 'special'

devices = dict(
    DBmem     = device('services.cache.server.MemoryCacheDatabase',
                    loglevel = 'info'),
    DBfile     = device('services.cache.server.FlatfileCacheDatabase',
                    storepath = '/data/nicos/cache',
                    loglevel = 'info'),

    Server = device('services.cache.server.CacheServer',
                    db = 'DBfile',
                    server = 'resictrl.resi.frm2',
                    loglevel = 'info'),
)
