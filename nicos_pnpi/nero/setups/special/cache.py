description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB = device('nicos.services.cache.database.FlatfileCacheDatabase',
        storepath = 'data/cache',
        loglevel = 'info',
    ),
    Server = device('nicos.services.cache.server.CacheServer',
        db = 'DB',
        # 'localhost' will normally bind the cache service to the
        # loopback device
        # '' will bind the daemon to all network interfaces in the
        # machine
        # If server is the hostname (official computer name) or an
        # IP address the daemon will be bound to the corresponding
        # network interface.
        # Binding the cache to the 'localhost' leads to trouble if
        # some other NICOS services are running on different
        # machines
        server = 'localhost',
        loglevel = 'info',
    ),
)
