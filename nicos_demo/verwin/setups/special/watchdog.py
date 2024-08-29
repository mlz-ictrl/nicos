
description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
    dict(condition = 'LogSpace_status[0] == WARN',
         message = 'Disk space for the log files becomes too low.',
         type = 'critical',
         gracetime = 30,
    ),
    dict(condition = 'Space_status[0] == WARN',
         message = 'Disk space for the data files becomes too low.',
         type = 'critical',
         gracetime = 10,
    ),
    dict(condition = 's_tripped_value == "Trip"',
         # precondition = 's_hv_value != "Off"',
         # precondtime = 60,
         # setup = 'source',
         message = 'Small detector high voltage current too high',
         type = 'critical',
         action = 'maw(s_hv, "off")',
         actiontimeout = 600,
         # gracetime = 5,
    ),
    dict(condition = 'b_tripped_value == "Trip"',
         # precondition = 's_hv_value != "Off"',
         # precondtime = 60,
         # setup = 'source',
         message = 'Big detector high voltage current too high',
         type = 'critical',
         action = 'maw(b_hv, "off")',
         actiontimeout = 600,
         # gracetime = 5,
    ),
]

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = configdata('config_data.cache_host'),
        notifiers = {'default': [],
                     'critical': []},
        watch = watch_conditions,
        loglevel = 'info',
    ),
)
