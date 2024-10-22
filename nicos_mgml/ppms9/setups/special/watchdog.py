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
    dict(condition = 'Cryostat_status[0] == WARN',
         message = 'Cryostat is below safe helium level!',
         type = 'critical',
         gracetime = 30,
         setup = 'ppms',
    ),
]

includes = [
    'notifiers',
]

notifiers = {
    'default': [],  # ['email'],
    'critical': [],  # ['email'],
}

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        # use only 'localhost' if the cache is really running on
        # the same machine, otherwise use the official computer
        # name
        cache = 'localhost:14870',
        notifiers = notifiers,
        mailreceiverkey = 'email/receivers',
        watch = watchlist,
    ),
)
