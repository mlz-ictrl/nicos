description = 'setup for the NICOS watchdog'
group = 'special'

# watchlist:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-stable/services/watchdog
watchlist = [
    # The first 2 entries check the disk space for the data and the log file
    # if there is any underflow in limits the user and/or instrument
    # responsible will informed via the NICOS alarm channels
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
    dict(
        condition = 't_value > 100',
        message = 'Temperature too high',
        type = 'critical',
        action = 'maw(T, 0)',
    ),
    dict(
        condition = 'phi_value > 100 and mono_value > 1.5',
        message = 'phi angle too high for current mono setting',
        gracetime = 5,
    ),
]

includes = [
    'notifiers',
]

notifiers = {
    'default': ['email'],
    'critical': ['email'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        # use only 'localhost' if the cache is really running on
        # the same machine, otherwise use the official computer
        # name
        cache = 'localhost',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watchlist,
    ),
)
