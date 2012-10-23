description = 'setup for the electronic logbook'
group = 'special'

sysconfig = dict(
    cache = None,
)

devices = dict(
    Logbook = device('nicos.elog.Logbook',
                     prefix = 'logbook/',
                     cache = 'cpci1.toftof.frm2:14869'),
)
