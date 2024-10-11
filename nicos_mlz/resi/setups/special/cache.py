description = 'setup for the cache server'
group = 'special'

devices = dict(
    DBmem = device('nicos.services.cache.database.MemoryCacheDatabase',
        loglevel = 'info',
    ),
    DBfile = device('nicos.services.cache.database.FlatfileCacheDatabase',
        storepath = '/data/nicos/cache',
        loglevel = 'info',
    ),
    Server = device('nicos.services.cache.server.CacheServer',
        db = 'DBfile',
        server = 'resictrl.resi.frm2.tum.de',
        loglevel = 'info',
    ),
)
