description = 'Setup for the GALAXI electronic logbook.'
group = 'special'

devices = dict(
    Logbook = device('nicos.services.elog.Logbook',
        prefix = 'logbook/',
        cache = 'localhost:14869',
    ),
)
