description = 'setup for the electronic logbook'
group = 'special'

sysconfig = dict(
    cache = None,
)

devices = dict(
    Logbook = device('services.elog.Logbook',
                     prefix = 'logbook/',
                     cache = 'pandasrv:14869'),
)
