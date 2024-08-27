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
        condition = 'o2_nguide_status[0] == WARN',
        message = 'O2 percentage in neutron guide exceeds warn limit!',
        type = 'neutronguide',
        gracetime = 600,
    ),
    dict(
        condition = 'abs(p1_nguide_value - p3_nguide_value) > 40',
        message = 'Difference P1/P3 > 40 mbar',
        type = 'neutronguide',
        gracetime = 600,
    ),
    dict(
        condition = 'abs(p2_nguide_value - p3_nguide_value) > 40',
        message = 'Difference P2/P3 > 40 mbar',
        type = 'neutronguide',
        gracetime = 600,
    ),
]

includes = ['notifiers']

notifiers = {
    'default': ['email'],
    'critical': ['email', 'smser'],
    'neutronguide': ['ngmail'],
    'logspace': ['email', 'smser', 'logspace_notif'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        # use only 'localhost' if the cache is really running on
        # the same machine, otherwise use the official computer
        # name
        cache = 'spodictrl.spodi.frm2.tum.de',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watch_conditions,
    ),
)
