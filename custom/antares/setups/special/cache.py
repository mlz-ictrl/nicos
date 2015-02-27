#  -*- coding: utf-8 -*-

description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB     = device('services.cache.server.FlatfileCacheDatabase',
                     description = 'On disk storage for Cache Server',
                     storepath = '/data/cache',
                     loglevel = 'info',
                   ),

    Server = device('services.cache.server.CacheServer',
                     description = 'Value caching server',
                     db = 'DB',
                     #~ server = 'antareshw.antares.frm2', # for reasons not understood this doesn't work!
                     server = '0.0.0.0',  # this works
                     loglevel = 'info',
                   ),
)
