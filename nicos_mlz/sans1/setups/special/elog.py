description = 'setup for the electronic logbook'
group = 'special'

devices = dict(
    Logbook = device('nicos.services.elog.Logbook',
                     prefix = 'logbook/',
                     cache = 'sans1hw02.sans1.frm2:14869'),
)
