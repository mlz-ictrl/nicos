description = 'setup for the NICOS watchdog'

group = 'special'

devices = dict(
    Watchdog = device('nicos.services.watchdog.Watchdog',
        cache = 'localhost',
        notifiers = {},
        mailreceiverkey = 'email/receivers',
        watch = [],
    ),
)
