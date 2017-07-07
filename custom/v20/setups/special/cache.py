# This setup file configures the nicos cache service.

description = 'setup for the cache server'
group = 'special'

devices = dict(
    DB     = device('nicos.services.cache.server.FlatfileCacheDatabase',
                    storepath = '/home/pi/nicos-core/data/cache',
                    loglevel = 'info',
                   ),

    Server = device('nicos.services.cache.server.CacheServer',
                    db = 'DB',
                    # 'localhost' will normally bind the cache service to the
                    # loopback device
                    # '' will bind the daemon to all network interfaces in the
                    # machine
                    # If server is the hostname (official computer name) or an
                    # IP address the daemon will be bound the the corresponding
                    # network interface.
                    # Binding the cache to the 'localhost' leads to trouble if
                    # some other NICOS services are running on different
                    # machines
                    server = 'localhost',
                    loglevel = 'info',
                   ),
)
