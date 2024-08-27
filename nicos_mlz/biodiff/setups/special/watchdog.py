description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
    dict(condition = '(sixfold_value == \'closed\' or nl1_value == \'closed\') '
                     'and reactorpower_value > 19.1',
         message = 'NL1 or sixfold shutter closed',
         type = 'critical',
        ),
    dict(condition = 'selector_speed_status[0] == ERROR',
         message = 'Selector in error status; check Windows software!',
         type = 'critical',
        ),
]

includes = ['notifiers']

notifiers = {
    'default': ['email'],
    'critical': ['email', 'smser'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'phys.biodiff.frm2:14869',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watch_conditions,
    ),
)
