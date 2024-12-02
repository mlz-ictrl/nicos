description = 'setup for the NICOS watchdog'
group = 'special'

# watch_conditions:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-master/services/watchdog/#watch-conditions
watch_conditions = [
    dict(condition = 'LogSpace_status[0] == WARN',
         message = 'Disk space for the log files becomes too low.',
         type = 'logspace',
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
         setup = 'charmsmall',
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
         setup = 'charmbig',
         action = 'maw(b_hv, "off")',
         actiontimeout = 600,
         # gracetime = 5,
    ),
]

nguide_conditions = [
    dict(condition = 'p1_nguide_status[0] == WARN',
        # precondition = 'p1_nguide_value < 10',
        # precondtime = 60,
        type = 'neutronguide',
        message = 'ErwiN: P1 is to high (> 10 mbar)',
    ),
    dict(condition = 'p2_nguide_status[0] == WARN',
        # precondition = 'p2_nguide_value < 10',
        # precondtime = 60,
        type = 'neutronguide',
        message = 'ErwiN: P2 is to high (> 10 mbar)',
    ),
]

charm_conditions = [
    dict(condition = 'charm2_pdet_status[0] == WARN',
        type = 'charm',
        setup = 'charmbox02',
        message = 'ErwiN/Charm: Pdet outside [7.70, 7.76] bar',
    ),
    dict(condition = 'charm2_ppump1_status[0] == WARN',
        type = 'charm',
        setup = 'charmbox02',
        message = 'ErwiN/Charm: P pump 1 outside [7.72, 7.78] bar',
    ),
    dict(condition = 'charm2_ppump2_status[0] == WARN',
        type = 'charm',
        setup = 'charmbox02',
        message = 'ErwiN/Charm: P pump 1 outside [7.71, 7.77] bar',
    ),
]

includes = ['notifiers']

notifiers = {
    'default': ['email'],
    'critical': ['email'],
    'neutronguide': ['ngmail'],
    'logspace': ['email', 'logspace_notif'],
    'charm': ['dmail', 'dsms'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'localhost:14869',
        notifiers = notifiers,
        watch = watch_conditions + nguide_conditions,  # + charm_conditions,
        loglevel = 'info',
    ),
)
