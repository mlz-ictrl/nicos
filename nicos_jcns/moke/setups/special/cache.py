description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB = device('nicos.services.cache.database.influxdb.InfluxDB2CacheDatabase',
        url = 'http://localhost:8086',
        org = 'mlz',
        bucket = 'nicos-cache',
        # bucket_latest = 'nicos-latest',
        loglevel = 'info',
    ),
    Server = device('nicos.services.cache.server.CacheServer',
        db = 'DB',
        server = '127.0.0.1',
        loglevel = 'info',
    ),
)
