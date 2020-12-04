description = 'setup for the NICOS watchdog'
group = 'special'

# watchlist:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-stable/services/watchdog
watchlist = [
    dict(
        # condition='len(Exp_scripts) > 0 and  emergency_value == 1',
        # message='Emergency stop engaged: FULL STOP!!!!',
        # gracetime=0,
        # type='critical',
        # scriptaction='immediatestop',
    ),
]

notifiers = {}

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
