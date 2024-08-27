description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
    dict(condition = 'LogSpace_status[0] == WARN',
         message = 'Disk space for log files becomes too low.',
         type = 'critical',
         gracetime = 30,
    ),
    dict(
        condition = 'mono_status[0] == BUSY',
        message = 'mtt is not moving. Maybe hardware blocked? Mobile block?',
        gracetime = 600,
        type = 'critical',
    ),
]

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = configdata('config_data.host'),
        notifiers = {'default': [],
                     'critical': []},
        watch = watch_conditions,
    ),
)
