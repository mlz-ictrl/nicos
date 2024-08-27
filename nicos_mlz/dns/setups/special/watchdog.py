description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
#    dict(condition = 'nlashutter_value == "closed" '
#                     'and reactorpower_value > 19.1',
#         message = 'NL6 or sixfold shutter closed',
#         type = 'critical',
#         gracetime = 300
#        ),
#    dict(condition = 'expshutter_value == "open" '
#                     'and reactorpower_value < 0.1',
#         message = 'reactor off',
#         type = 'critical',
#         gracetime = 300
#        ),
#    dict(condition = 't_value > 100',
#         message = 'Temperature too high',
#         type = 'critical',
#         action = 'maw(T, 0)',
#        ),
#    dict(condition = 'phi_value > 100 and mono_value > 1.5',
#         message = 'phi angle too high for current mono setting',
#         gracetime = 5,
#        ),
]

includes = ['notifiers']

notifiers = {
    'default':  ['email'],
    'critical': ['email', 'smser'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'localhost:14869',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watch_conditions,
    ),
)
