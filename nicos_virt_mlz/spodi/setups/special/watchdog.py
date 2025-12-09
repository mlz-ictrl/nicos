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
        condition = 'o2_nguide_status[0] == WARN',
        message = 'O2 percentage in neutron guide exceeds warn limit!',
        type = 'neutronguide',
        gracetime = 600,
    ),
    dict(
        # condition = 'p1_nguide_status[0] == WARN or p1_nguide_value > 8',
        condition = 'p1_nguide_status[0] == WARN',
        # precondition = 'p1_nguide_value < 10',
        setup = 'nguide',
        message = 'ErwiN: P1 is to high!',
    ),
    dict(condition = 'p1_nguide_status[0] == WARN',
        setup = 'nguide',
        precondition = 'p1_nguide_value < 10',
        precondtime = 60,
        type = '',  # neutronguide',
        message = 'ErwiN: P1 is to high (> 10 mbar)',
    ),
]

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = configdata('config_data.cache_host'),
        notifiers = {
            'default': [],
            'critical': [],
            'neutronguide': [],
        },
        watch = watch_conditions,
        loglevel = 'info',
    ),
)
