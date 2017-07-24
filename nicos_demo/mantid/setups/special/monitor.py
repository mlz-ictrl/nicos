# This setup file configures the nicos status monitor.

description = 'setup for the status monitor'
group = 'special'

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
                     title = 'NICOS status monitor',
                     loglevel = 'info',
                     # Use only 'localhost' if the cache is really running on
                     # the same machine, otherwise use the hostname (official
                     # computer name) or an IP address.
                     cache = 'localhost',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     padding = 0,
                     layout = [],
                    ),
)
