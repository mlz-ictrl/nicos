description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
    dict(condition = 'lab_humidity_value > 55',
         message='Humidity is too high in the lab which might cause '
                 'condensation of water inside SigmaPhi power supply and '
                 'its failure.',
         gracetime = 600,
         setup = 'moke'
    ),
]

includes = ['notifiers']

notifiers = {
    'default': ['email'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'localhost:14869',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watch_conditions,
    ),
)
