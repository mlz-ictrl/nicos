description = 'setup for the electronic logbook'
group = 'special'

devices = dict(
    Logbook = device('nicos.services.elog.Logbook',
                     prefix = 'logbook/',
                     cache = 'sans1ctrl.sans1.frm2:14869'),
)
