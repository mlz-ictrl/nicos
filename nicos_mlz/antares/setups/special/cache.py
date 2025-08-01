description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB = device('nicos.services.cache.database.influxdb.InfluxDB2CacheDatabase',
        url = 'http://app.antares.frm2.tum.de:8086',
        org = 'mlz',
        bucket = 'nicos-cache',
        bucket_latest = 'nicos-cache-latest-values',
        loglevel = 'info',
    ),
    Server = device('nicos.services.cache.server.CacheServer',
        description = 'Value caching server',
        db = 'DB',
        server = '',
        loglevel = 'info',
    ),
)
