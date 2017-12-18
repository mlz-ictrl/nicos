description = 'setup for the electronic logbook'
group = 'special'

devices = dict(
    Logbook = device('nicos.services.elog.Logbook',
        prefix = 'logbook/',
        cache = 'nectarhw.nectar.frm2',
    ),
)
