description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
    dict(condition = 'LogSpace_status[0] == WARN',
         message = 'Disk space for log files becomes too low.',
         type = 'logspace',
         gracetime = 30,
    ),
    dict(
        condition = '(sixfold_value == "closed" or nl6_value == "closed") '
        'and reactorpower_value > 19.1',
        message = 'NL6 or sixfold shutter closed',
        type = 'critical',
    ),
    dict(
        condition = 'cooltemp_value > 25',
        message =
        'Cooling water temperature exceeds 25C, clean filter or check FAK40 or MIRA Leckmon!',
        type = 'critical',
    ),
    dict(
        condition = 'psdgas_value == "empty"',
        message = 'PSD gas is empty, change bottle very soon!',
        type = 'critical',
        setup = 'cascade',
    ),
#    dict(
#        condition = 'tbe_value > 70',
#        message = 'Be filter temperature > 70 K, check cooling water!',
#    ),
]

includes = ['notifiers']

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'miractrl.mira.frm2.tum.de:14869',
        notifiers = {
            'default': ['email'],
            'critical': ['email', 'smser'],
            'logspace': ['email', 'smser', 'logspace_notif'],
        },
        watch = watch_conditions,
        mailreceiverkey = 'email/receivers',
    ),
)
