description = 'setup for the electronic logbook'
group = 'special'

sysconfig = dict(
    cache = None,
)

devices = dict(
    Logbook = device('nicos.services.elog.Logbook',
        prefix = 'logbook/',
        cache = 'antareshw.antares.frm2:14869'
    ),
)
