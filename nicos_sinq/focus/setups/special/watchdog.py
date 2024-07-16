description = 'setup for the NICOS watchdog'
group = 'special'

# watchlist:
# The entries in this list are dictionaries.
# For the entry keys and their meaning see:
# https://forge.frm2.tum.de/nicos/doc/nicos-stable/services/watchdog
watchlist = [
    dict(
        condition = 'ch2vacuum_value > .01',
        message = 'Chopper vacuum broken',
        gracetime = 0,
        type = 'critical',
        action = 'maw(ch1_speed, 0)',
        scriptaction = 'immediatestop',
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
