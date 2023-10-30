description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB = device('nicos.services.cache.database.influxdb.InfluxDBCacheDatabase',
        url = 'http://app.antares.frm2:8086',
        keystoretoken = 'influxdb',
        org = 'mlz',
        bucket = 'nicos-cache',
        loglevel = 'info',
    ),
    Server = device('nicos.services.cache.server.CacheServer',
        description = 'Value caching server',
        db = 'DB',
        server = '',
        loglevel = 'info',
    ),
)
