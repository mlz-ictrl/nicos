description = 'setup for the electronic logbook'
group = 'special'

devices = dict(
    Logbook = device('services.elog.Logbook',
                     prefix = 'logbook/',
                     cache = 'refsans10.refsans.frm2'),
)
