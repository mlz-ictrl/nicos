description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = []
# watch_conditions = [
#    dict(condition = 't_value > 100',
#         message = 'Temperature too high',
#         type = 'critical',
#         action = 'maw(T, 0)',
#        ),
#    dict(condition = 'phi_value > 100 and mono_value > 1.5',
#         message = 'phi angle too high for current mono setting',
#         gracetime = 5,
#        ),
# ]

notifiers = {
    'default': ['email'],
    'critical': ['email'],
}

includes = ['notifiers']

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'localhost:14869',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watch_conditions,
    ),
)
