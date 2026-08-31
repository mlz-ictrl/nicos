description = 'setup for the NICOS watchdog'

group = 'special'

# watchlist:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-stable/services/watchdog/#watch-conditions
watchlist = [
    # These 2 entries check the disk space for the data and the log file
    # if there is any underflow in limits the user and/or instrument
    # responsible will be informed via the NICOS alarm channels
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
]

hv_conditions = [
    dict(condition = f'det{i}_hv_status[0] == ERROR',
         precondition = f"det{i}_hv_value != 'off' and det{i}_hv_target == 'on'",
         message = f'Detector HV{i} is probably tripped',
         type = 'critical',
         action = f"maw(det{i}_hv, 'off')",
         actiontimeout = 900,
         gracetime = 0,
         precondtime = 1,
         setup = f'hv{i}')
    for i in range(1, 9)
]

includes = [
    'notifiers',
]

notifiers = {
    'default': [],
    'critical': [],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        # use only 'localhost' if the cache is really running on
        # the same machine, otherwise use the official computer
        # name
        cache = 'localhost',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watchlist + hv_conditions,
    ),
)
