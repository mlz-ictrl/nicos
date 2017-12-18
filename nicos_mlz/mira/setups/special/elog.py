description = 'setup for the electronic logbook'
group = 'special'

sysconfig = dict(
    cache = None,
)

devices = dict(
    Logbook = device('nicos.services.elog.Logbook',
        plotformat = 'png',
        prefix = 'logbook/',
        cache = 'mira1:14869'
    ),
)
