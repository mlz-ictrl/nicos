description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB     = device('nicos.cache.server.FlatfileCacheDatabase',
                    storepath = '/users/cache',
                    loglevel = 'info'),

    Server = device('nicos.cache.server.CacheServer',
                    db = 'DB',
                    server = 'cpci1.toftof.frm2',
                    loglevel = 'info'),
)
