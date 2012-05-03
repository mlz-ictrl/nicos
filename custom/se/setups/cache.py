description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB     = device('nicos.cache.server.FlatfileCacheDatabase',
                    storepath = '/var/cache/nicos',
                    loglevel = 'info'),

    Server = device('nicos.cache.server.CacheServer',
                    db = 'DB',
                    server = 'tasgroup2.taco.frm2',
                    loglevel = 'info'),
)
