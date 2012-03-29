description = 'setup for the electronic logbook'
group = 'special'

devices = dict(
    Logbook = device('nicos.elog.Logbook',
                     prefix = 'logbook/',
                     server = 'mira1:14869'),
)
