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
        condition = 'o2_nguide_value > 0.4',
        message = 'O2 pressure in neutron guide exceeds 0.4 %%',
        type = 'neutronguide',
        gracetime = 60,
    ),
]

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = configdata('config_data.cache_host'),
        notifiers = {
            'default': [],
            'critical': [],
        },
        watch = watch_conditions,
        loglevel = 'info',
    ),
)
