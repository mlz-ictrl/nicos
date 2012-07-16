description = 'setup for the electronic logbook'
group = 'special'

sysconfig = dict(
    cache = None,
)

devices = dict(
    Logbook = device('nicos.elog.Logbook',
                     prefix = 'logbook/',
                     cache = 'mira1:14869'),
)
