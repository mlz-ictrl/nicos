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
        condition = 'reactorpower_value < 19.1',
        message = 'Possible Reactor Shutdown! Reactor power < 19MW',
        type = 'critical',
        setup = 'reactor',
        gracetime = 300,
    ),
    dict(condition = 'HomeSpace_value < 1',
         message = '/home/nectar is running out of space. Only 1GB left!',
         type = 'default',
         setup = 'system',
         gracetime = 300,
    ),
    dict(condition = 'DataSpace_value < 50',
         message = '/data is running out of space. Only 1TB left!',
         type = 'default',
         setup = 'system',
         gracetime = 300,
    ),
    dict(condition = 'Space_value < 1',
         message = 'The root directory of antareshw is running out of space. Only 1GB left!',
         type = 'default',
         setup = 'system',
         gracetime = 300,
    ),
]

includes = ['notifiers']

notifiers = {
    'default': ['warning', 'smser'],
    'critical': ['warning', 'smser'],
    'logspace': ['warning', 'smser', 'logspace_notif'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        # use only 'localhost' if the cache is really running on
        # the same machine, otherwise use the official computer
        # name
        cache = 'localhost',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watch_conditions,
    ),
)
