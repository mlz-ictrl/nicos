description = 'setup for the HERMES electronic logbook'
group = 'special'

devices = dict(
    Logbook = device('nicos.services.elog.Logbook',
        prefix = 'logbook/',
        cache = 'localhost',
    ),
)