description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
    dict(
        condition = '(sixfold_value == \'closed\' or nl5_value == \'closed\') '
                    'and reactorpower_value > 19.1',
        message = 'NL5 or sixfold shutter closed',
        type = 'critical',
    ),
    dict(
        condition = 'selector_speed_status[0] == ERROR',
        message =
        'Selector in error status. Please check selector2.maria.frm2.',
        type = 'critical',
    ),
    dict(
        condition = 'selector_speed_target > 0 '
                    'and selector_vacuum_status[0] == WARN',
        message = 'Selector vacuum in warning range.',
        type = 'default',
    ),
]

includes = ['notifiers']

notifiers = {
    'default':  ['mailer'],
    'critical': ['mailer', 'smser'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'localhost',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watch_conditions,
    ),
)
